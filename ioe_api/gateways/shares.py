# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateways.shares
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, as_dict


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
