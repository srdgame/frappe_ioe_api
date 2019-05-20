# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications.forks
#

from __future__ import unicode_literals
import frappe
from app_center.app_center.doctype.iot_application_version.iot_application_version import get_latest_version
from ioe_api.helper import throw, as_dict
from .versions import copy_forked_app_files


@frappe.whitelist()
def create(name, version=0, pre_conf=None):
	try:
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		version = int(version)
		if version == 0:
			version = get_latest_version(name, beta=1)

		if not frappe.get_value('IOT Application Version', {"app": name, "version": version}, "name"):
			throw("version_not_exists")

		doc = frappe.get_doc("IOT Application", name)
		forked_doc = doc.fork(frappe.session.user, version, pre_conf)

		copy_forked_app_files(name, forked_doc.name, version)

		frappe.response.update({
			"ok": True,
			"message": as_dict(forked_doc)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def list(name, version=None, owner=None):
	try:
		filters = {"fork_from": name}
		if version:
			filters.update({"fork_version": version})
		if owner:
			filters.update({"owner": owner})

		apps = []
		for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application", d.name)))

		frappe.response.update({
			"ok": True,
			"data": apps
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def pull(name, version):
	try:
		fork_from = frappe.get_value("IOT Application", name, "frok_from")
		if not fork_from:
			throw("not_forked_application")
		if frappe.get_value("IOT Application Version", {"app": name, "version": version}):
			throw("version_already_exists")

		copy_forked_app_files(fork_from, name, version)

		frappe.response.update({
			"ok": True,
			"info": "version_pulled"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
