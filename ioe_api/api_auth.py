# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt
#
# RESTFul API for IOT User which has his/her auth code
#

from __future__ import unicode_literals
import frappe
import json
from frappe import throw, _


def valid_auth_code(auth_code=None):
	if 'Guest' != frappe.session.user:
		return
	auth_code = auth_code or frappe.get_request_header("AuthorizationCode")
	if not auth_code:
		throw("auth_code_missing")
	frappe.logger(__name__).debug(_("API AuthorizationCode as {0}").format(auth_code))

	user = frappe.get_value("IOT User Api", {"authorization_code": auth_code}, "user")
	if not user:
		throw("auth_code_incorrect")

	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict


def get_post_json_data():
	if frappe.request.method != "POST":
		throw("method_must_be_post")
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw("http_content_type_is_not_json")
	data = frappe.request.get_data()
	if not data:
		throw("request_body_missing")
	return json.loads(data.decode('utf-8'))
