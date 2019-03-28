# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications
#

from __future__ import unicode_literals
import os
import frappe
from werkzeug.utils import secure_filename

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict
from .versions import get_app_release_path


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "app.test"
	})


@frappe.whitelist()
def list():
	try:
		apps = []
		filters = {"owner": frappe.session.user}
		for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application", d.name), keep_owner=True))

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
def create():
	try:
		data = get_post_json_data()
		data.update({
			"doctype": "IOT Application",
			"owner": frappe.session.user,
			"published": 0
		})

		doc = frappe.get_doc(data).insert()

		frappe.response.update({
			"ok": True,
			"data": as_dict(doc)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def save_app_icon(app, f):
	fname = secure_filename(repr(f.filename))
	ext = fname.rsplit('.', 1)[1].lower()  # 获取文件后缀
	if ext not in ['png', 'PNG']:
		throw("icon_must_be_png_file")

	file_path = os.path.join(get_app_release_path(app), "icon.png")
	f.save(file_path)  # 保存文件到upload目录

	return "/files/app_center_files/" + app + "/icon.png"


@frappe.whitelist()
def icon():
	try:
		name = frappe.dict.name
		try:
			doc = frappe.get_doc("IOT Application", name)
		except Exception as ex:
			throw("app_not_found")

		f = frappe.request.files.get('icon_file')  # 从表单的file字段获取文件，app_file为该表单的name值
		if f:
			file_path = save_app_icon(name, f)
			doc.set("icon_image", file_path)
			doc.save()

		frappe.response.update({
			"ok": True,
			"data": file_path
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def read(name):
	try:
		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("IOT Application", name, keep_owner=True)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update():
	try:
		data = get_post_json_data()
		update_doc("IOT Application", data)
		frappe.response.update({
			"ok": True,
			"message": "application_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def remove(name):
	try:
		owner = frappe.get_value("IOT Application", name, "owner")
		if not owner:
			throw("application_not_found")

		if owner != frappe.session.user:
			throw("not_application_owner")

		# TODO: remove application not implemented so far
		throw("contact_admin")
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


