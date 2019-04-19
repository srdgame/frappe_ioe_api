# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for configurations
#

from __future__ import unicode_literals
import frappe

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict


@frappe.whitelist()
def list(conf_type='Template'):
	try:
		apps = []
		filters = {"owner": frappe.session.user, "type": conf_type}
		for d in frappe.get_all("IOT Application Conf", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application Conf", d.name), keep_owner=True))

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
def create():
	try:
		data = get_post_json_data()
		data.update({
			"doctype": "IOT Application Conf",
			"owner": frappe.session.user
		})

		doc = frappe.get_doc(data).insert()

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
def read(name):
	try:
		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application Conf", name, keep_owner=True)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update():
	try:
		data = get_post_json_data()
		update_doc("IOT Application Conf", data)
		frappe.response.update({
			"ok": True,
			"message": "configuration_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def remove(name):
	try:
		owner = frappe.get_value("IOT Application Conf", name, "owner")
		if not owner:
			throw("configuration_not_found")

		if owner != frappe.session.user:
			throw("not_configuration_owner")

		# TODO: remove application not implemented so far
		throw("contact_admin")
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

