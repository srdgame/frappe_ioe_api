# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.reviews
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw, as_dict, update_doc, get_post_json_data


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.favorites.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()

		data = []
		doc = frappe.get_doc("IOT Application Favorites", frappe.session.user)
		for d in doc.apps.favorites:
			data.append(as_dict(frappe.get_doc("IOT Application", d.app)))

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
def add(app, comment=None, priority=0):
	try:
		valid_auth_code()

		if frappe.request.method != "POST":
			throw("method_must_be_post")

		if not frappe.get_value("IOT Application Favorites", frappe.session.user, "name"):
			frappe.get_doc({
				"doctype": "IOT Application Favorites",
				"user": frappe.session.user,
				"favorites": [{"app": app, "comment": comment, "priority": priority}]
			}).insert()
		else:
			doc = frappe.get_doc("IOT Application Favorites", frappe.session.user)
			doc.add_favorites({"app": app, "comment": comment, "priority": priority})

		frappe.response.update({
			"ok": True,
			"data": "favorites_added"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove(app):
	try:
		valid_auth_code()

		if frappe.request.method != "POST":
			throw("method_must_be_post")

		doc = frappe.get_doc("IOT Application Favorites", frappe.session.user)
		doc.remove_favorites(app)

		frappe.response.update({
			"ok": True,
			"data": "favorites_added"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})