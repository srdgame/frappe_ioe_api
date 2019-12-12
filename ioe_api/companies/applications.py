# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.applications
#

from __future__ import unicode_literals
import frappe

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict, valid_auth_code
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.applications.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		apps = []
		companies = list_admin_companies(frappe.session.user)
		filters = {"company": ["in", companies]}

		for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
			apps.append(get_doc_as_dict("IOT Application", d.name, include_tags=True))

		for app in apps:
			app.installed = frappe.get_value("IOT Application Counter", app.name, "installed") or 0

		frappe.response.update({
			"ok": True,
			"data": apps
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
		data = get_doc_as_dict("IOT Application", name, include_tags=True)
		data.installed = frappe.get_value("IOT Application Counter", name, "installed") or 0
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
def update():
	try:
		valid_auth_code()
		data = get_post_json_data()

		companies = list_admin_companies(frappe.session.user)
		if frappe.get_value("IOT Application", data.get('name'), 'company') not in companies:
			throw("invalid_permission")
		update_doc("IOT Application", data)
		frappe.response.update({
			"ok": True,
			"message": "application_updated"
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
		company = frappe.get_value("IOT Application", name, "company")
		if not company:
			throw("application_not_found")

		if company not in list_admin_companies(frappe.session.user):
			throw("invalid_permission")

		if frappe.get_value("IOT Application", name, "published") == 1:
			throw("published_iot_application_cannot_be_deleted!")

		doc = frappe.get_doc("IOT Application", name)
		doc.clean_before_delete()
		frappe.delete_doc("IOT Application", name)
		frappe.response.update({
			"ok": True,
			"message": "application_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


