# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateways.applications
#

from __future__ import unicode_literals
import frappe
import redis
import json
import uuid
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.device_api import send_action
from ioe_api.helper import valid_auth_code, get_post_json_data, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateways.applications.test"
	})


@frappe.whitelist(allow_guest=True)
def list(gateway):
	try:
		valid_auth_code()

		device = frappe.get_doc('IOT Device', gateway)
		if not device.has_permission("read"):
			throw("has_no_permission")

		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6", decode_responses=True)
		app_list = []
		app_list_json_str = client.get(gateway)
		if app_list_json_str:
			try:
				app_list = json.loads(app_list_json_str)
			except Exception as ex:
				throw("json_decode_failure")
		else:
			throw("data_not_found")

		frappe.response.update({
			"ok": True,
			"data": app_list
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def fire_action(id, action, gateway, data):
	try:
		if id is None:
			id = str(uuid.uuid1()).upper()
		return send_action("app", action=action, id=id, device=gateway, data=data)
	except Exception as ex:
		throw("exception")


@frappe.whitelist(allow_guest=True)
def refresh(gateway, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="list", gateway=gateway, data="1")

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
def install(gateway, app, version, inst, conf, id=None, from_web=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		data = {
			"inst": inst,
			"name": app,
			"version": version,
			"conf": conf
		}
		if from_web is not None:
			data.update({"from_web": 1})

		ret = fire_action(id=id, action="install", gateway=gateway, data=data)

		frappe.get_doc({
			"doctype": "IOT Application Statistics",
			"app": app,
			"device": gateway,
			"version": version,
			"action": 'INSTALL',
			"owner_company": doc.company,
			"owner_type": doc.owner_type,
			"owner_id": doc.owner_id,
		}).insert()

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
def remove(gateway, inst, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="uninstall", gateway=gateway, data={"inst": inst})

		# frappe.get_doc({
		# 	"doctype": "IOT Application Statistics",
		# 	"app": app,
		# 	"device": gateway,
		# 	"version": version,
		# 	"action": 'UNINSTALL',
		# 	"owner_company": doc.company,
		# 	"owner_type": doc.owner_type,
		# 	"owner_id": doc.owner_id,
		# }).insert()

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
def conf(gateway, inst, conf, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="conf", gateway=gateway, data={"inst": inst, "conf": conf})

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
def start(gateway, inst, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="start", gateway=gateway, data={"inst": inst})

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
def stop(gateway, inst, reason, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="stop", gateway=gateway, data={"inst": inst, "reason": reason})

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
def restart(gateway, inst, reason, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="restart", gateway=gateway, data={"inst": inst, "reason": reason})

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
def upgrade(gateway, inst, app, version, conf=None, id=None, fork=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		data = {
			"inst": inst,
			"name": app,
			"version": version,
		}
		if conf is not None:
			data.update({"conf": conf})
		if fork is not None:
			data.update({"fork": fork})

		ret = fire_action(id=id, action="upgrade", gateway=gateway, data=data)

		frappe.get_doc({
			"doctype": "IOT Application Statistics",
			"app": app,
			"device": gateway,
			"version": version,
			"action": 'UPGRADE',
			"owner_company": doc.company,
			"owner_type": doc.owner_type,
			"owner_id": doc.owner_id,
		}).insert()

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
def query_log(gateway, inst, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="query_log", gateway=gateway, data={"inst": inst})

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
def query_comm(gateway, inst, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="query_comm", gateway=gateway, data={"inst": inst})

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
def upload_comm(gateway, inst, sec=60, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="upload_comm", gateway=gateway, data={"inst": inst, "sec": sec})

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
def option(gateway, inst, option="auto", value=1, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="option", gateway=gateway, data={"inst": inst, "option": option, "value": value})

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
def rename(gateway, inst, new_name, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="rename", gateway=gateway, data={"inst": inst, "new_name": new_name})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
