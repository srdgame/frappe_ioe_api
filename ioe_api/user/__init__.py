# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
from frappe import throw
from frappe.core.doctype.user.user import sign_up, reset_password
from ..api_auth import valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.test"
	})


@frappe.whitelist(allow_guest=True)
def valid_auth():
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"user": frappe.session.user,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def register(email, full_name, redirect_to=None):
	try:
		ret, info = sign_up(email=email, full_name=full_name, redirect_to=redirect_to)

		frappe.response.update({
			"ok": True,
			"result": ret,
			"info": info
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": 'exception',
			"exception": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def update(info):
	try:
		if 'Guest' == frappe.session.user:
			throw("have_no_permission")

		frappe.response.update({
			"ok": True,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		if not True:
			throw("have_no_permission")

		frappe.response.update({
			"ok": True,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})

