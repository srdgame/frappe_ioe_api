# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.events
#

from __future__ import unicode_literals
import frappe
import json
from six import text_type, string_types
from iot.iot.doctype.iot_device_event.iot_device_event import count_device_event_by_company, query_device_event_by_company, get_event_detail
from ioe_api.helper import valid_auth_code, throw, get_post_json_data


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.events.test"
	})


'''
filters = [["creation", ">", "2014-01-01"]]

filters = {"creation": [">", "2014-01-01"], "operation": "Owner"}
'''


@frappe.whitelist(allow_guest=True)
def list(name, start=0, limit=40, filters=None):
	try:
		valid_auth_code()
		if isinstance(filters, string_types):
			filters = json.loads(filters) or {}

		frappe.response.update({
			"ok": True,
			"data": query_device_event_by_company(company=name, start=start, limit=limit, filters=filters)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def count(name, filters=None):
	try:
		valid_auth_code()
		if isinstance(filters, string_types):
			filters = json.loads(filters) or {}

		frappe.response.update({
			"ok": True,
			"data": count_device_event_by_company(company=name, filters=filters)
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
			"data": get_event_detail(name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def dispose(events, disposed=1):
	try:
		valid_auth_code()

		postdata = get_post_json_data()
		events = postdata['events'] or {}
		disposed = postdata['disposed'] or 1

		warns = []
		for event in events:
			try:
				doc = frappe.get_doc("IOT Device Event", event)
				doc.dispose(disposed)
			except Exception as ex:
				warns.append(str(ex))

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
			"error": str(ex)
		})
