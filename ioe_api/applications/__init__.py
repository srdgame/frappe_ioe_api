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

from ioe_api.helper import get_post_json_data, throw, as_dict, update_doc, get_doc_as_dict, valid_auth_code
from .versions import get_app_release_path


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "applications.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		apps = []
		filters = {"developer": frappe.session.user}
		for d in frappe.get_all("IOT Application", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("IOT Application", d.name),  include_tags=True))

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
def create():
	try:
		valid_auth_code()
		data = get_post_json_data()
		data.update({
			"doctype": "IOT Application",
			"developer": frappe.session.user,
			# "published": 0
		})

		if 'star' in data:
			data.pop('star')

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
		valid_auth_code()
		name = frappe.form_dict.name
		try:
			doc = frappe.get_doc("IOT Application", name)
		except Exception as ex:
			throw("app_not_found")

		f = frappe.request.files.get('file')  # 从表单的file字段获取文件，app_file为该表单的name值
		if not f:
			throw("icon_file_not_found")

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


@frappe.whitelist(allow_guest=True)
def read(name):
	try:
		valid_auth_code()
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
def update():
	try:
		valid_auth_code()
		data = get_post_json_data()

		if 'star' in data:
			data.pop('star')

		if frappe.get_value("IOT Application", data.get('name'), 'developer') != frappe.session.user:
			throw("invalid_permission")

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


@frappe.whitelist(allow_guest=True)
def remove(name):
	try:
		valid_auth_code()
		developer = frappe.get_value("IOT Application", name, "developer")
		if not developer:
			throw("application_not_found")

		if developer != frappe.session.user:
			throw("not_application_developer")

		if frappe.get_value("IOT Application", name, "published") == 1:
			throw("published_iot_application_cannot_be_deleted!")

		# TODO: check whether the application is belongs to company, thus it only can not deleted by cloud admin

		doc = frappe.get_doc("IOT Application", name)
		doc.clean_before_delete()
		frappe.delete_doc("IOT Application", name)
		frappe.response.update({
			"ok": True,
			"message": "application_removed"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


