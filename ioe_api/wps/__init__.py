# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for wps integration
#

from __future__ import unicode_literals
import frappe
from .helper import valid_weboffice_token, get_signature
from ioe_api.helper import valid_auth_code


WPS_APPID = "a7bda3f18c394a967269c15cbd7f224e"
WPS_APPKEY = "ddd831d67c7d452f6c61e19c5ae2b8dc"


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "wps.test"
	})


@frappe.whitelist(allow_guest=True)
def wps_url(conf, version, version_new):
	valid_auth_code()
	return get_signature(WPS_APPID, WPS_APPKEY, frappe.session.user, frappe.session.sid, conf, version, version_new)


@frappe.whitelist(allow_guest=True)
def onnotify():
	return {
		"msg": "success"
	}
