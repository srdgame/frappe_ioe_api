# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for wps integration wps.user
#

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.utils import get_fullname
from .helper import valid_weboffice_token
from ioe_api.helper import get_post_json_data


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "wps.user.test"
	})


@frappe.whitelist(allow_guest=True)
def info(_w_appid, _w_conf_name, _w_userid, _w_sid, _w_signature):
	valid_weboffice_token(_w_userid, _w_sid)
	_w_conf_name = _w_conf_name or frappe.get_request_header("x-weboffice-file-id")

	data = get_post_json_data()

	ids = data.get('ids')
	if ids:
		users = []
		for id in ids:
			users.append({
				"id": id,
				"name":  get_fullname(id),
				"avatar_url": "http://cloud.thingsroot.com/user?id=" + id
			})

		frappe.response.update({
			"users": users
		})
	else:
		throw("missing_ids")