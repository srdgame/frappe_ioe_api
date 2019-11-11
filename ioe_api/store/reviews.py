# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.reviews
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw, as_dict, update_doc, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.reviews.test"
	})


@frappe.whitelist(allow_guest=True)
def list(app):
	try:
		data = []
		filters = {"app": app}
		for d in frappe.get_all("IOT Application Review", "name", filters=filters, order_by="modified desc"):
			data.append(as_dict(frappe.get_doc("IOT Application Review", d.name)))

		frappe.response.update({
			"ok": True,
			"data": data
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def create(app, title, content, star):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")
		content = str(content).replace('\n', '<br>')

		doc = frappe.get_doc({
			"doctype": "IOT Application Review",
			"app": app,
			"star": star,
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
			"data": get_doc_as_dict("IOT Application Review", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update(name, title, content, star):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")
		content = str(content).replace('\n', '<br>')

		doc = update_doc("IOT Application Review", {
			"name": name,
			"star": star,
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

		frappe.delete_doc("IOT Application Review", name)

		frappe.response.update({
			"ok": True,
			"data": "application_review_deleted"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

