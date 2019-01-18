# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
from ..helper import valid_auth_code, get_post_json_data, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "conf.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def add():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def info():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def update():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def remove():
	frappe.response.update({
		"ok": True
	})

