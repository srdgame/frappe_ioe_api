# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateways.extensions
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
		"source": "gateways.extensions.test"
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
		return send_action("sys", action=action, id=id, device=gateway, data=data)
	except Exception as ex:
		throw("exception")


@frappe.whitelist(allow_guest=True)
def refresh(gateway, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="ext/list", gateway=gateway, data={})

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
def upgrade(gateway, extension, version, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="ext/upgrade", gateway=gateway, data={"name": extension, "version": version})

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
def auto_clean(gateway, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', gateway)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="ext/auto_clean", gateway=gateway, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
