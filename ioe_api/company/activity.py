# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway.activity
#

from __future__ import unicode_literals
import frappe
from frappe import throw
from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_company, count_logs_by_company, get_log_detail
from ..api_auth import valid_auth_code, get_post_json_data


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "company.activity.test"
	})



'''
filters = [["creation", ">", "2014-01-01"]]

filters = {"creation": [">", "2014-01-01"], "operation": "Owner"}
'''


@frappe.whitelist(allow_guest=True)
def list(name, start=0, limit=40, filters=None):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"activities": query_logs_by_company(company=name, start=start, limit=limit, filters=filters)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def count(name, filters=None):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"activities": count_logs_by_company(company=name, filters=filters)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def info(name):
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"data": get_log_detail(name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def dispose(*name, disposed=1):
	try:
		valid_auth_code()
		warns = []
		for activity in name:
			try:
				doc = frappe.get_doc("IOT Device Activity", activity)
				doc.dispose(disposed)
			except Exception as ex:
				warns.append(repr(ex))

		if len(warns) > 0:
			frappe.response.update({
				"ok": True,
				"warning": warns
			})
		else:
			frappe.response.update({
				"ok": True,
			})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})
