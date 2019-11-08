# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications.tags
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_tags, update_tags


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
			"data": get_tags('IOT Application', name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, tags):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Application', name)
		update_tags(doc, tags)

		frappe.response.update({
			"ok": True,
			"data": 'done'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
