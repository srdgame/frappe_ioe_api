# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for user.company_invitation
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.company_invitation.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()

		data = []
		for d in frappe.get_all("Cloud Employee Invitation", "name", filters={"user": frappe.session.user}):
			data.append(get_doc_as_dict('Cloud Employee Invitation', d.name, keep_docstatus=True))

		frappe.response.update({
			"ok": True,
			"data": data
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def accept(name):
	try:
		valid_auth_code()

		if frappe.get_value('Cloud Employee Invitation', name, 'user') != frappe.session.user:
			throw("invalid_request")

		doc = frappe.get_doc('Cloud Employee Invitation', name)
		doc.submit()

		frappe.response.update({
			"ok": True,
			"data": 'invitation_accepted'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def reject(name):
	try:
		valid_auth_code()

		if frappe.get_value('Cloud Employee Invitation', name, 'user') != frappe.session.user:
			throw("invalid_request")

		doc = frappe.get_doc('Cloud Employee Invitation', name)
		doc.delete()

		frappe.response.update({
			"ok": True,
			"data": 'invitation_rejected'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})