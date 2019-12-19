# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateways.shares
#

from __future__ import unicode_literals
import frappe
from frappe.utils import get_datetime, time_diff_in_seconds
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, as_dict, update_doc


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateways.shares.test"
	})


@frappe.whitelist(allow_guest=True)
def list(name):
	try:
		valid_auth_code()

		if not frappe.has_permission(doctype="IOT Device", doc=name, ptype='write'):
			throw("no_permission")

		share_list = []
		for d in frappe.db.get_values("IOT Device Share", {"device": name}, "name"):
			share_list.append(get_doc_as_dict("IOT Device Share", d[0], keep_creation=True, keep_owner=True))

		frappe.response.update({
			"ok": True,
			"data": share_list
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create():
	try:
		valid_auth_code()

		data = get_post_json_data()
		data.update({
			"doctype": "IOT Device Share"
		})

		if not frappe.has_permission(doctype="IOT Device", doc=data.get("device"), ptype='write'):
			throw("no_permission")

		''' TODO: Change the permission implementation'''
		for d in frappe.db.get_values("IOT Device Share", {"device": data.get("device"), "share_to": frappe.session.user}, "name"):
			end_time = frappe.get_value("IOT Device Share", d[0], "end_time")
			if time_diff_in_seconds(end_time, get_datetime()) > 0:
				throw("cannot_share_the_shared_device")

		doc = frappe.get_doc(data).insert()

		frappe.response.update({
			"ok": True,
			"data": as_dict(doc)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def read(name):
	try:
		valid_auth_code()
		doc = frappe.get_doc("IOT Device Share", name)
		if doc.has_permission("write"):
			throw("no_permission")

		frappe.response.update({
			"ok": True,
			"data": as_dict(doc)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update():
	try:
		valid_auth_code()
		data = get_post_json_data()
		update_doc("IOT Device Share", data)
		frappe.response.update({
			"ok": True,
			"message": "shared_device_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove(name):
	try:
		valid_auth_code()

		frappe.delete_doc("IOT Device Share", name)

		frappe.response.update({
			"ok": True,
			"data": "iot_device_share_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
