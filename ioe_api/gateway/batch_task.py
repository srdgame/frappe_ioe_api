# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway.batch_task
#

from __future__ import unicode_literals
import frappe
from frappe import throw
from six import string_types
from ..helper import valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.batch_task.test"
	})


@frappe.whitelist(allow_guest=True)
def create(task_name, description, timeout, script, *devices):
	try:
		valid_auth_code()
		'''
		post_data = get_post_json_data()
		name = post_data.get('name')
		script = post_data.get('script')
		devices = post_data.get('devices')
		'''
		if not isinstance(task_name, string_types):
			throw("invalid_task_name_type")
		if not isinstance(script, string_types):
			throw("invalid_script_type")
		if not isinstance(devices, list):
			throw("devices_required_as_array")

		doc = frappe.get_doc({
			"doctype": "IOT Batch Task",
			"task_name": task_name,
			"task_description": description,
			"batch_script": script,
			"timeout": timeout,
			"owner_id": frappe.session.user,
		})

		for dev in devices:
			doc.append("device_list", { "device": dev })
		doc = doc.insert()
		frappe.db.commit() # Commit to database to make sure batch task has been there before submit()
		doc.submit()

		frappe.response.update({
			"ok": True,
			"data": doc.name
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex),
		})


@frappe.whitelist(allow_guest=True)
def info(name):
	try:
		valid_auth_code()
		if frappe.get_value("IOT Batch Task", name, "owner_id") != frappe.session.user:
			throw("have_no_permission")

		frappe.response.update({
			"ok": True,
			"data": frappe.get_doc("IOT Batch Task", name).as_dict()
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex),
		})


@frappe.whitelist(allow_guest=True)
def status(name, update=False):
	try:
		valid_auth_code()

		if frappe.get_value("IOT Batch Task", name, "owner_id") != frappe.session.user:
			throw("have_no_permission")

		if update is not False:
			doc = frappe.get_doc("IOT Batch Task", name)
			doc.update_status()

		frappe.response.update({
			"ok": True,
			"data": frappe.get_value("IOT Batch Task", name, "status")
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex),
		})
