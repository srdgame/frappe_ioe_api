# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for developers
#

from __future__ import unicode_literals
import frappe

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict, valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "developers.test"
	})
#
#
# @frappe.whitelist(allow_guest=True)
# def create():
# 	try:
# 		valid_auth_code()
#
# 		data = get_post_json_data()
# 		data.update({
# 			"doctype": "App Developer",
# 			"user": frappe.session.user,
# 			"enabled": 1
# 		})
#
# 		doc = frappe.get_doc(data).insert()
#
# 		frappe.response.update({
# 			"ok": True,
# 			"data": as_dict(doc)
# 		})
# 	except Exception as ex:
# 		frappe.response.update({
# 			"ok": False,
# 			"error": str(ex)
# 		})


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
		valid_auth_code()
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