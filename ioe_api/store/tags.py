# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.tags
#

from __future__ import unicode_literals
import frappe
from app_center.app_center.doctype.iot_application.iot_application import list_tags, add_tags, remove_tags, clear_tags
from ..helper import valid_auth_code, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "app.tags.test"
	})


@frappe.whitelist(allow_guest=True)
def list(name):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": list_tags(app=name)
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
			"data": add_tags(app=name, tags=tags)
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
			"data": remove_tags(app=name, tags=tags)
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
			"data": clear_tags(app=name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
