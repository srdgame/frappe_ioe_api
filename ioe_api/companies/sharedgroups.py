# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.sharedgroups
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc
from iot.iot.doctype.iot_share_group.iot_share_group import add_user as _add_user
from iot.iot.doctype.iot_share_group.iot_share_group import remove_user as _remove_user
from iot.iot.doctype.iot_share_group.iot_share_group import add_device as _add_device
from iot.iot.doctype.iot_share_group.iot_share_group import remove_device as _remove_device
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies

@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.sharedgroups.test"
	})


def list_company_shared_groups(company):
	if 'Company Admin' not in frappe.get_roles():
		return []

	return [d[0] for d in frappe.db.get_values("IOT Share Group", {"company": company}, "name")]


@frappe.whitelist(allow_guest=True)
def list(company):
	try:
		valid_auth_code()
		data = list_company_shared_groups(company)

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

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("only_admin_can_create_shared_group")

		# if frappe.get_value("Cloud Company", data.get('company'), "admin") != frappe.session.user:
		# 	throw("you_are_not_admin_of_this_company")

		if not data.get("group_name"):
			throw("group_name_missing")
		if not data.get("company"):
			throw("company_id_missing")

		data.update({
			"doctype": "IOT Share Group",
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
			"data": get_doc_as_dict("IOT Share Group", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, group_name, description, role): #, users=None, devices=None):
	try:
		valid_auth_code()

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("only_admin_can_update_shared_group")

		data = {
			"name": name,
			"group_name": group_name,
			"description": description,
			"role": role
		}
		post_data = get_post_json_data()
		users = post_data.get('users')
		if users is not None:
			data.update({
				"users": users
			})
		devices = post_data.get('devices')
		if devices is not None:
			data.update({
				"devices": devices
			})

		update_doc("IOT Share Group", data)
		frappe.response.update({
			"ok": True,
			"message": "company_shared_group_updated"
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

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("only_admin_can_remove_shared_group")

		frappe.delete_doc("IOT Share Group", name)
		frappe.response.update({
			"ok": True,
			"message": "company_shared_group_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def add_user(name, user, comment):
	try:
		valid_auth_code()

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("not_permitted")

		_add_user(name, user, comment)
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

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("not_permitted")

		_remove_user(name, user)
		frappe.response.update({
			"ok": True,
			"message": "user_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def add_device(name, device):
	try:
		valid_auth_code()

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("not_permitted")

		_add_device(name, device)
		frappe.response.update({
			"ok": True,
			"message": "device_added"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove_device(name, device):
	try:
		valid_auth_code()

		# TODO: Enable all employee to create/edit/delete for now!
		# if 'Company Admin' not in frappe.get_roles():
		# 	throw("not_permitted")

		_remove_device(name, device)
		frappe.response.update({
			"ok": True,
			"message": "device_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


