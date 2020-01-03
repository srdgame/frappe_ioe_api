# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications.categories
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "applications.categories.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": frappe.get_all("App Category", "name")
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

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict('App Category', name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
