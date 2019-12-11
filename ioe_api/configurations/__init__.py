# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for configurations
#

from __future__ import unicode_literals
import frappe

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict, valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "configurations.test"
	})


@frappe.whitelist(allow_guest=True)
def list(conf_type='Template'):
	try:
		valid_auth_code()
		apps = []
		filters = {"developer": frappe.session.user, "type": conf_type}
		for d in frappe.get_all("IOT Application Conf", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application Conf", d.name)))

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
def create():
	try:
		valid_auth_code()
		data = get_post_json_data()
		data.update({
			"doctype": "IOT Application Conf",
			"developer": frappe.session.user
		})
		if data.get('owner_type') != 'Cloud Company Group':
			data.update({
				"owner_id": frappe.session.user
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


@frappe.whitelist(allow_guest=True)
def read(name):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application Conf", name)
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


@frappe.whitelist(allow_guest=True)
def remove(name):
	try:
		valid_auth_code()
		developer = frappe.get_value("IOT Application Conf", name, "developer")
		if not developer:
			throw("configuration_not_found")

		if developer != frappe.session.user:
			throw("not_configuration_developer")

		if frappe.get_value("IOT Application Conf", name, "public") == 1:
			throw("public_application_conf_cannot_be_deleted!")

		# TODO: check whether the application is belongs to company, thus it only can not deleted by cloud admin

		doc = frappe.get_doc("IOT Application Conf", name)
		doc.clean_before_delete()
		frappe.delete_doc("IOT Application Conf", name)
		frappe.response.update({
			"ok": True,
			"message": "configuration_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

