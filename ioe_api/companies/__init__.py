# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies
#

from __future__ import unicode_literals
import frappe
from ..helper import valid_auth_code, get_post_json_data, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "company.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def create():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def info(name):
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def update(name, info=None):
	if not info:
		info = get_post_json_data()
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def remove(name):
	frappe.response.update({
		"ok": True
	})

