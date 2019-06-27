# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications
#

from __future__ import unicode_literals
import frappe

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict, valid_auth_code

@frappe.whitelist(allow_guest=True)
def list(order_by="modified desc"):
	try:
		valid_auth_code()
		devs = []
		for d in frappe.get_all("IOT Application", "name", order_by=order_by):
			devs.append(get_doc_as_dict("IOT Application", d.name))

		frappe.response.update({
			"ok": True,
			"data": devs
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create(group, nickname, enabled=1):
	try:
		valid_auth_code()

		data = get_post_json_data()
		data.update({
			"doctype": "App Developer",
			"user": frappe.session.user,
			"group": group,
			"nickname": nickname,
			"enabled": enabled
		})

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
def read(user=None):
	try:
		valid_auth_code()

		user = user or frappe.session.user
		name = frappe.get_value('App Developer', user)

		if not name:
			throw("not_developer")

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict('App Developer', user)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update():
	try:
		data = get_post_json_data()
		update_doc("App Developer", data)
		frappe.response.update({
			"ok": True,
			"message": "app_developer_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})