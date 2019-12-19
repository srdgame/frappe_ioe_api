# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateways.devices
#

from __future__ import unicode_literals
import frappe
import redis
import json
import uuid
import datetime
import requests
import html
from frappe.utils import convert_utc_to_user_timezone
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.device_api import send_action
from ioe_api.helper import valid_auth_code, throw
from ioe_api.gateways import fire_action


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateways.devices.test"
	})


@frappe.whitelist(allow_guest=True)
def list___xxx():
	try:
		valid_auth_code()
		if not True:
			throw("has_no_permission")

		frappe.response.update({
			"ok": True,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def gateway_device_list(gateway=None):
	doc = frappe.get_doc('IOT Device', gateway)
	if not doc.has_permission("read"):
		throw("has_no_permission")

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11", decode_responses=True)
	return client.lrange(gateway, 0, -1)


def gateway_device_info(gateway=None, device=None):
	doc = frappe.get_doc('IOT Device', gateway)
	if not doc.has_permission("read"):
		throw("has_no_permission")

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/10", decode_responses=True)
	return json.loads(client.get(device or gateway) or "{}")


@frappe.whitelist(allow_guest=True)
def list(gateway):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": gateway_device_list(gateway)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def read(gateway, name=None):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": gateway_device_info(gateway, name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def data(gateway, name=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("read"):
			throw("has_no_permission")

		if not name:
			name = gateway

		if name and name != gateway:
			if name not in gateway_device_list(gateway):
				throw("no_such_device_in_gateway")

		cfg = gateway_device_info(gateway, name)
		if not cfg:
			throw("device_info_empty")

		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12", decode_responses=True)
		hs = client.hgetall(name)
		device_data = []

		if "inputs" in cfg:
			inputs = cfg.get("inputs")
			for input in inputs:
				input_name = input.get('name')
				s = hs.get(input_name + "/value")
				if not s:
					device_data.append({
						"name": input_name,
						"pv": None,
						"tm": '',
						"q": -1,
						"vt": input.get('vt'),
						"desc": input.get("desc"),
						"unit": input.get('unit'),
					})
				else:
					val = json.loads(hs.get(input_name + "/value"))

					ts = datetime.datetime.utcfromtimestamp(int(val[0]))
					time_str = str(convert_utc_to_user_timezone(ts).replace(tzinfo=None))

					device_data.append({
						"name": input_name,
						"pv": val[1],
						"tm": time_str,
						"q": val[2],
						"vt": input.get('vt'),
						"desc": input.get("desc"),
						"unit": input.get('unit'),
					})

		frappe.response.update({
			"ok": True,
			"data": device_data
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def data_query(gateway, name, id=None):
	'''
	Force device data snapshot
	:return:
	'''
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="data/query", gateway=gateway, data=name)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def history_data(gateway, name, input, vt=None, time_condition=None, value_method=None, group_time_span=None, fill_method=None, count_limit=None, time_zone=None):
	try:
		valid_auth_code()

		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("read"):
			raise frappe.PermissionError

		inf_server = IOTHDBSettings.get_influxdb_server()
		if not inf_server:
			frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
			return

		# -------------------------------------------------------------------------------------------------------------
		vtdict = {"float": "value", "int": "int_value", "string": "string_value"}
		vt = vt or "float"
		field = '"' + vtdict.get(vt) + '"'
		fields = '"' + vtdict.get(vt) + '"' + ' , "quality"'
		method = dict(raw=fields, mean='mean(' + field + ')', max='max(' + field + ')', min='min(' + field + ')',
		              first='first(' + field + ')', last='last(' + field + ')', sum='sum(' + field + ')',
		              count='count(' + field + ')')
		if value_method not in ["raw", "mean", "max", "min", "first", "last", "sum", "count"]:
			value_method = "raw"
		filter = ' "iot"=\'' + gateway + '\' AND "device"=\'' + name + '\''
		if value_method != "raw":
			filter = ' "iot"=\'' + gateway + '\' AND "device"=\'' + name + '\'' + ' AND "quality"=0 '
		group_time_span = group_time_span or "1m"

		time_condition = time_condition or 'time > now() - 10m'
		time_condition = html.unescape(time_condition)

		# fill_method = "null/previous/none/linear"
		fill_method = fill_method or "none"
		group_method = ' GROUP BY time(' + group_time_span + ') FILL(' + fill_method + ')'
		count = count_limit or 200
		time_zone = time_zone or 'Asia/Shanghai'

		query = 'SELECT'
		get_method = method["raw"]
		if value_method:
			get_method = method[value_method]
		query = query + ' ' + get_method + ' FROM "' + input + '"' + ' WHERE ' + filter + ' AND ' + time_condition
		if value_method != "raw":
			query = query + group_method
		query = query + ' limit ' + str(count) + " tz('" + time_zone + "')"

		domain = frappe.get_value("Cloud Company", doc.company, "domain")
		r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
		if r.status_code == 200:
			ret = r.json()
			# print(ret)
			if not ret:
				return
			results = ret['results']
			if not results or len(results) < 1:
				return
			series = results[0].get('series')
			if not series or len(series) < 1:
				return
			res = series[0].get('values')
			if not res:
				return
			taghis = []
			if value_method == "raw":
				for i in range(0, len(res)):
					hisvalue = {'name': input, 'value': res[i][1], 'time': res[i][0], 'quality': res[i][2], 'device': name}
					taghis.append(hisvalue)
			else:
				for i in range(0, len(res)):
					hisvalue = {'name': input, 'value': res[i][1], 'time': res[i][0], 'quality': 0, 'device': name}
					taghis.append(hisvalue)

			frappe.response.update({
				"ok": True,
				"data": taghis
			})
		else:
			throw("failed_to_read_history")
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def output(gateway, name, output, prop, value, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		if not id:
			id = str(uuid.uuid1()).upper()

		try:
			ret = send_action("output", id=id, device=gateway, data= {
				"device": name,
				"output": output,
				"prop": prop,
				"value": value
			})

			frappe.response.update({
				"ok": True,
				"data": ret
			})
		except Exception as ex:
			throw("exception")

	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def command(gateway, name, command, param=None, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		if not id:
			id = str(uuid.uuid1()).upper()

		try:
			ret = send_action("command", id=id, device=gateway, data= {
				"device": name,
				"cmd": command,
				"param": param,
			})

			frappe.response.update({
				"ok": True,
				"data": ret
			})
		except Exception as ex:
			throw("exception")

	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

