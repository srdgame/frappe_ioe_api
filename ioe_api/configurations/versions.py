# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for configurations.versions
#

from __future__ import unicode_literals
import frappe
from conf_center.conf_center.doctype.iot_application_conf_version.iot_application_conf_version import get_latest_version
from ioe_api.helper import valid_auth_code, throw, as_dict, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "configurations.versions.test"
	})


@frappe.whitelist(allow_guest=True)
def list(conf):
	try:
		valid_auth_code()
		version_list = []
		for d in frappe.get_all("IOT Application Conf Version", "name", {"conf": conf}, order_by="modified desc"):
			version_list.append(as_dict(frappe.get_doc("IOT Application Conf Version", d.name)))

		frappe.response.update({
			"ok": True,
			"data": version_list
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create(name, version, data, comment):
	try:
		valid_auth_code()
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		doc = frappe.get_doc({
			"doctype": "IOT Application Conf Version",
			"conf": name,
			"version": version,
			"data": data,
			"comment": comment
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
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application Conf Version", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def latest(conf):
	try:
		valid_auth_code()
		ver = get_latest_version(conf=conf)
		frappe.response.update({
			"ok": True,
			"data": ver
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
		frappe.delete_doc("IOT Application Conf Version", name)
		frappe.response.update({
			"ok": True,
			"info": "configuration_version_deleted"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

