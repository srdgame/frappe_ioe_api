# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway.tags
#

from __future__ import unicode_literals
import frappe
from iot.iot.doctype.iot_device.iot_device import list_tags, add_tags, remove_tags, clear_tags
from ioe_api.helper import valid_auth_code, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.tags.test"
	})


@frappe.whitelist(allow_guest=True)
def list(name):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": list_tags(sn=name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create(name, *tags):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": add_tags(name, tags)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove(name, *tags):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": remove_tags(name, tags)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def clear(name):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": clear_tags(name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
