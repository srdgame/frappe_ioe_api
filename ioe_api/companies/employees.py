# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.groups
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.employees.test"
	})


@frappe.whitelist(allow_guest=True)
def list(company):
	try:
		valid_auth_code()
		data = [d.name for d in frappe.get_all("Cloud Employee", filters={"company": company})]

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

		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_create_employee")

		if not data.get("user"):
			throw("user_id_missing")
		if not data.get("company"):
			throw("company_id_missing")

		if frappe.get_value("Cloud Company", data.get('company'), "admin") != frappe.session.user:
			throw("you_are_not_admin_of_this_company")

		domain = frappe.get_value("Cloud Company", data.get('company'), "domain")
		user = data.get("user")

		if user == user[0 - len(domain):]:
			data.update({
				"doctype": "Cloud Employee",
			})
			doc = frappe.get_doc(data).insert()
		else:
			data.update({
				"doctype": "Cloud Employee Invitation",
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
def invite():
	try:
		valid_auth_code()
		data = get_post_json_data()

		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_create_employee")

		if not data.get("user"):
			throw("user_id_missing")
		if not data.get("company"):
			throw("company_id_missing")

		if frappe.get_value("Cloud Company", data.get('company'), "admin") != frappe.session.user:
			throw("you_are_not_admin_of_this_company")

		if frappe.get_value("Cloud Employee", data.get("user")):
			throw("user_is_already_joined_other_company")

		data.update({
			"doctype": "Cloud Employee Invitation",
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
			"data": get_doc_as_dict("Cloud Employee", name)
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
		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_remove_employee")

		frappe.delete_doc("Cloud Employee", name)
		frappe.response.update({
			"ok": True,
			"message": "company_employee_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

