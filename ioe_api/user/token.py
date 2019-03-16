# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for user.token
#

from __future__ import unicode_literals
import frappe
import uuid
from ioe_api.helper import throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.token.test"
	})


@frappe.whitelist()
def create():
	try:
		code = frappe.get_value("IOT User Api", frappe.session.user, "authorization_code")
		if code:
			throw("authorization_code_exists")

		auth_code = str(uuid.uuid1()).lower()
		doc = frappe.get_doc({
			"doctype": "IOT User Api",
			"user": frappe.session.user,
			"authorization_code": auth_code
		}).insert()

		frappe.response.update({
			"ok": True,
			"data": auth_code,
			"info": "authorization_code_created"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def read():
	try:
		code = frappe.get_value("IOT User Api", frappe.session.user, "authorization_code")
		if not code:
			throw("authorization_code_not_exists")
		frappe.response.update({
			"ok": True,
			"data": code,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update():
	try:
		auth_code = frappe.get_value("IOT User Api", frappe.session.user, "authorization_code")
		if not auth_code:
			throw("authorization_code_not_exists")

		doc = frappe.get_doc("IOT User Api", frappe.session.user)
		new_token = str(uuid.uuid1()).lower()
		doc.set("authorization_code", new_token)
		doc.save()

		frappe.response.update({
			"ok": True,
			"data": new_token,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def remove():
	try:
		frappe.delete_doc("IOT User Api", frappe.session.user)

		frappe.response.update({
			"ok": True,
			"info": "auth_code_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": "exception",
			"exception": str(ex)
		})

