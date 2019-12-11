# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.test"
	})


@frappe.whitelist(allow_guest=True)
def list(developer=None, tags=None):
	try:
		apps = []
		if not developer:
			developer = ["!=", "Administrator"]
		filters = {"developer": developer, "published": 1}
		if tags is None:
			for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
				'''
				for tag in frappe.get_value("IOT Application Tag", ["name", "tag"], {"parent": d[0]}):
					if tag[0] in tags:
						apps.append(as_dict(frappe.get_doc("IOT Application", d.name)))
				'''
				apps.append(get_doc_as_dict("IOT Application", d.name, include_tags=True))
		else:
			tag_filters = {"tag", ["in", tags]}
			for d in frappe.get_all("Tag Link", "document_name", filters=tag_filters):
				if frappe.get_value("IOT Application", d.document_name, "published") == 1:
					apps.append(get_doc_as_dict("IOT Application", d.name, include_tags=True))

		for app in apps:
			app.installed = frappe.get_value("IOT Application Counter", app.name, "installed") or 0

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
		data = get_doc_as_dict("IOT Application", name, include_tags=True)
		data.installed = frappe.get_value("IOT Application Counter", name, "installed") or 0
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
def search():
	frappe.response.update({
		"ok": True
	})


# TODO: