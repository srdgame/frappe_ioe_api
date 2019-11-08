# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications.tags
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, list_tags
from frappe.desk.reportview import get_sidebar_stats


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "app.tags.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		data = get_sidebar_stats(stats="_user_tags", doctype='IOT Application')

		frappe.response.update({
			"ok": True,
			"data": data.get('stats').get('_user_tags')
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})