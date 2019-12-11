# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for user.company
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.company.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()

		data = []
		for d in frappe.get_all("Cloud Employee", "company", filters={"user": frappe.session.user}):
			data.append(get_doc_as_dict('Cloud Company', d.name))

		frappe.response.update({
			"ok": True,
			"data": data
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def quit(company):
	try:
		valid_auth_code()

		user = frappe.session.user

		doc = frappe.get_doc("Cloud Employee", user)
		if doc.company != company:
			throw("invalid_company")

		domain = frappe.get_value("Cloud Company", company, "domain")

		if user == user[0 - len(domain):]:
			throw("cannot_quit_company")

		frappe.delete_doc("Cloud Employee", user, ignore_permissions=True)

		frappe.response.update({
			"ok": True,
			"data": 'done'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})