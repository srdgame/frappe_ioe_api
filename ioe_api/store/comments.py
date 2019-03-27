# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.comments
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import throw, as_dict, update_doc, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.comments.test"
	})


@frappe.whitelist(allow_guest=True)
def list(app):
	try:
		apps = []
		filters = {"app": app}
		for d in frappe.get_all("IOT Application Comment", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application Comment", d.name)))

		frappe.response.update({
			"ok": True,
			"data": apps
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def create(app, title, content, reply_to):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")
		content = str(content).replace('\n', '<br>')

		doc = frappe.get_doc({
			"doctype": "IOT Application Comment",
			"app": app,
			"reply_to": reply_to,
			"title": title,
			"content": content,
		}).insert()

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
def read(name):
	try:

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application Comment", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update(name, title, content):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")
		content = str(content).replace('\n', '<br>')

		doc = update_doc("IOT Application Comment", {
			"name": name,
			"title": title,
			"content": content
		})

		frappe.response.update({
			"ok": True,
			"data": as_dict(doc)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def remove(name):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		frappe.delete_doc("IOT Application Comment", name)

		frappe.response.update({
			"ok": True,
			"data": "application_comment_deleted"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

