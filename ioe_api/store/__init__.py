# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for app store
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "app.test"
	})


@frappe.whitelist(allow_guest=True)
def list(owner=None, tags=None):
	try:
		apps = []
		if not owner:
			owner = ["!=", "Administrator"]
		filters = {"owner": owner, "published": 1}
		if tags is None:
			for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
				'''
				for tag in frappe.get_value("IOT Application Tag", ["name", "tag"], {"parent": d[0]}):
					if tag[0] in tags:
						apps.append(as_dict(frappe.get_doc("IOT Application", d.name)))
				'''
				apps.append(get_doc_as_dict("IOT Application", d.name, keep_owner=True, include_tags=True))
		else:
			tag_filters = {"tag", ["in", tags]}
			for d in frappe.get_all("Tag Link", "document_name", filters=tag_filters):
				if frappe.get_value("IOT Application", d.document_name, "published") == 1:
					apps.append(get_doc_as_dict("IOT Application", d.name, keep_owner=True, include_tags=True))

		frappe.response.update({
			"ok": True,
			"data": apps
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def read(name):
	try:
		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application", name, keep_owner=True, include_tags=True)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def search():
	frappe.response.update({
		"ok": True
	})


# TODO: