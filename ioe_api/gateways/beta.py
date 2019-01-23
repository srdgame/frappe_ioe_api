# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway.beta
#

from __future__ import unicode_literals
import frappe
from frappe import throw
from ..helper import valid_auth_code, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.beta.test"
	})


@frappe.whitelist(allow_guest=True)
def info(gateway):
	try:
		valid_auth_code()
		device = frappe.get_doc('IOT Device', gateway)
		if not device.has_permission("read"):
			throw("has_no_permission")

		frappe.response.update({
			"ok": True,
			"data": {
				"use_beta": device.use_beta,
				"use_beta_start_time": device.use_beta_start_time
			}
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable(gateway):
	try:
		valid_auth_code()

		device = frappe.get_doc('IOT Device', gateway)
		if not device.has_permission("read"):
			throw("has_no_permission")
		device.set_use_beta()

		frappe.response.update({
			"ok": True,
			"message": "set_use_beta_done"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
