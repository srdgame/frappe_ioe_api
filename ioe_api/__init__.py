# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw

__version__ = '0.0.1'


@frappe.whitelist(allow_guest=True)
def test(exception=None):
	try:
		if exception:
			throw('not_allowed')

		frappe.response.update({
			"ok": True,
			"data": "test_ok_result",
			"source": "test"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex),
			"source": "test"
		})
