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
		"source": "companies.groups.test"
	})


def list_company_groups(company):
	if 'Company Admin' not in frappe.get_roles():
		return []

	return [d[0] for d in frappe.db.get_values("Cloud Company Group", {"company": company, "enabled": 1}, "name")]


@frappe.whitelist(allow_guest=True)
def list(company):
	try:
		valid_auth_code()
		data = list_company_groups(company)

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
			throw("only_admin_can_create_group")

		if not data.get("group_name"):
			throw("group_name_missing")
		if not data.get("company"):
			throw("company_id_missing")

		if frappe.get_value("Cloud Company", data.get('company'), "admin") != frappe.session.user:
			throw("you_are_not_admin_of_this_company")

		data.update({
			"doctype": "Cloud Company Group",
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
			"data": get_doc_as_dict("Cloud Company Group", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, group_name, description, enabled=1): #, user_list=None):
	try:
		valid_auth_code()
		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_update_group")

		data = {
			"name": name,
			"group_name": group_name,
			"description": description,
			"enabled": enabled
		}
		post_data = get_post_json_data()
		user_list = post_data.get('user_list')
		if user_list is not None:
			data.update({
				"user_list": user_list
			})

		if user_list is not None and group_name == "root":
			company = frappe.get_value("Cloud Company Group", name, "company")
			users = [d.user for d in user_list]
			org_users = [d.name for d in frappe.get_all("Cloud Employee", filters={"company": company})]

			for user in org_users:
				if user not in users:
					frappe.delete_doc("Cloud Employee", user)
			for user in users:
				if user not in org_users:
					doc = frappe.get_doc({"doctype": "Cloud Employee", "user": user, "company": company})
					doc.insert(ignore_permissions=True)

		update_doc("Cloud Company Group", data)
		frappe.response.update({
			"ok": True,
			"message": "company_group_updated"
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
			throw("only_admin_can_remove_group")

		update_doc("Cloud Company Group", {
			"name": name,
			"enabled": 0
		})
		frappe.response.update({
			"ok": True,
			"message": "company_group_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def add_user(name, user, role='Admin'):
	try:
		valid_auth_code()
		if 'Company Admin' not in frappe.get_roles():
			throw("not_permitted")

		group = frappe.get_doc("Cloud Company Group", name)

		user_comp = frappe.get_value("Cloud Employee", user, "company")
		if user_comp and user_comp != group.company:
			throw("user_in_another_company")

		if group.group_name == "root" and user_comp is None:
			doc = frappe.get_doc({"doctype": "Cloud Employee", "user": user, "company": group.company})
			doc.insert(ignore_permissions=True)
		group.add_users(role, user)

		frappe.response.update({
			"ok": True,
			"message": "user_added"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove_user(name, user):
	try:
		valid_auth_code()
		if 'Company Admin' not in frappe.get_roles():
			throw("not_permitted")

		group = frappe.get_doc("Cloud Company Group", name)

		group.remove_users(user)
		if group.group_name == "root":
			frappe.delete_doc("Cloud Employee", user)

		frappe.response.update({
			"ok": True,
			"message": "user_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

