# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for pushers
#

from __future__ import unicode_literals
import frappe

from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies
from ..helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict


def validate_owner(name):
	companies = list_admin_companies(frappe.session.user)
	user = frappe.get_value("IOT User Application", name, "on_behalf")
	if not user:
		throw("pusher_on_behalf_missing")
	company = frappe.get_value("Cloud Employee", user, "company")
	if not company:
		throw("pusher_on_behalf_user_company")
	if company not in companies:
		throw("pusher_not_yours")


@frappe.whitelist()
def list():
	try:
		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			throw("not_company_admin")

		companies = list_admin_companies(frappe.session.user)
		apps = []
		for d in frappe.get_all("IOT User Application", "name"):
			user = frappe.get_value("IOT User Application", d[0], "on_behalf")
			if not user:
				continue
			company = frappe.get_value("Cloud Employee", user, "company")
			if not company:
				continue
			if company in companies:
				apps.append(as_dict(frappe.get_doc("IOT User Application", d[0])))

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
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			throw("not_company_admin")

		data = get_post_json_data()
		data.update({
			"doctype": "IOT User Application",
			"owner": frappe.session.user,
			"public": 0
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
def info(name):
	try:
		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			throw("not_company_admin")

		validate_owner(name)

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT User Application", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update(name, info):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			throw("not_company_admin")

		validate_owner(name)

		update_doc("IOT User Application", name, info)
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
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			throw("not_company_admin")

		validate_owner(name)

		frappe.delete_doc("IOT User Application", name)
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


