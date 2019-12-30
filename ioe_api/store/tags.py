# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.tags
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, list_tags, get_post_json_data
from frappe.desk.reportview import get_sidebar_stats


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.tags.test"
	})


@frappe.whitelist(allow_guest=True)
def list(filters=[]):
	try:
		valid_auth_code()
		# data = get_sidebar_stats(stats="_user_tags", doctype='IOT Application')
		#
		# frappe.response.update({
		# 	"ok": True,
		# 	"data": data.get('stats').get('_user_tags')
		# })

		_user_tags = []
		if frappe.request and frappe.request.method == "POST":
			data = get_post_json_data()
			filters = data.get("filters") or []

		for tag in frappe.get_all("Tag Link", filters={"document_type": 'IOT Application'}, fields=["tag"]):
			tag_filters = []
			tag_filters.extend(filters)
			tag_filters.extend([['Tag Link', 'tag', '=', tag.tag]])

			count = frappe.get_all('IOT Application', filters=tag_filters, fields=["count(*)"])
			if count[0].get("count(*)") > 0:
				_user_tags.append([tag.tag, count[0].get("count(*)")])

		frappe.response.update({
			"ok": True,
			"data": _user_tags
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})