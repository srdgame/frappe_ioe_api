# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for user.virtual_gateways
#

from __future__ import unicode_literals
import frappe
import uuid
from ..helper import throw
from ..gateways import info as gateway_info


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.virtual_gateways.test"
	})


@frappe.whitelist()
def list():
	try:
		devices = [d[0] for d in frappe.db.get_values('IOT Virtual Device', {"user": frappe.session.user})]
		frappe.response.update({
			"ok": True,
			"data": devices
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": "exception",
			"exception": str(ex)
		})


@frappe.whitelist()
def create():
	try:
		doc = frappe.get_doc({
			"doctype": "IOT Virtual Device",
			"user": frappe.session.user,
			"sn": str(frappe.generate_hash(frappe.session.user, 10)).upper(),
		}).insert()

		frappe.response.update({
			"ok": True,
			"data": doc.name,
			"info": "virtual_device_created"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": "exception",
			"exception": str(ex)
		})


@frappe.whitelist()
def info(name):
	try:
		doc = frappe.get_doc("IOT Virtual Device", name)
		return gateway_info(name)
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
