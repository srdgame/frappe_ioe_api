# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies
#

from __future__ import unicode_literals
import frappe
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "company.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		data = list_admin_companies(frappe.session.user)

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
def create():
	try:
		valid_auth_code()
		data = get_post_json_data()
		if not data.get("comp_name"):
			throw("company_name_missing")
		if not data.get("domain"):
			throw("domain_missing")

		data.update({
			"doctype": "Cloud Company",
			"admin": frappe.session.user,
			"enabled": 0,
			"wechat": 0
		})
		doc = frappe.get_doc(data).insert()

		frappe.response.update({
			"ok": True,
			"data": doc.name
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
			"data": get_doc_as_dict("Cloud Company", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, full_name, address, contact):
	try:
		valid_auth_code()

		update_doc("Cloud Company", {
			"name": name,
			"full_name": full_name,
			"address": address,
			"contact": contact
		})
		frappe.response.update({
			"ok": True,
			"message": "company_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove(name):
	try:
		valid_auth_code()

		update_doc("Cloud Company", {
			"name": name,
			"enabled": 0
		})
		frappe.response.update({
			"ok": True,
			"message": "company_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

