# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
import json
import redis
import datetime
import uuid
import requests
from six import string_types

from iot.hdb_api import list_iot_devices


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.app.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def info():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def install():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def remove():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def conf():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def start():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def stop():
	frappe.response.update({
		"ok": True
	})


@frappe.whitelist(allow_guest=True)
def upgrade():
	frappe.response.update({
		"ok": True
	})
