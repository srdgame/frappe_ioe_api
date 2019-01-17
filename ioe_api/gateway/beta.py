# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway.beta
#

from __future__ import unicode_literals
import frappe
from frappe import throw
from ..api_auth import valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.beta.test"
	})


@frappe.whitelist(allow_guest=True)
def info(name):
	try:
		valid_auth_code()
		device = frappe.get_doc('IOT Device', name)
		if not device.has_permission("read"):
			throw("have_no_permission")

		frappe.response.update({
			"ok": True,
			"use_beta": device.use_beta,
			"use_beta_start_time": device.use_beta_start_time
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})


@frappe.whitelist(allow_guest=True)
def update(name, use_beta):
	try:
		valid_auth_code()
		if use_beta != 1:
			throw('cannot_disable_beta_flag')

		device = frappe.get_doc('IOT Device', name)
		if not device.has_permission("read"):
			throw("have_no_permission")
		device.set_use_beta()

		frappe.response.update({
			"ok": True,
			"message": "set_use_beta_done"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": repr(ex),
		})
