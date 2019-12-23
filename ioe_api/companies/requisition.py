# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.requisition
#

from __future__ import unicode_literals
import frappe
import os
import hashlib
from frappe.utils import get_files_path
from werkzeug.utils import secure_filename
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc, as_dict

ALLOWED_EXTENSIONS = set(['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'jpeg'])
COMPANY_REQUISITION_FILES = 'company_requisition_files'


def allowed_file(filename):
	# 用于判断文件后缀
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_requisition_file_path(comp_name_hash):
	basedir = get_files_path(COMPANY_REQUISITION_FILES)
	file_dir = os.path.join(basedir, comp_name_hash)
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)

	return file_dir


def hash_company_name(comp_name):
	m = hashlib.md5()
	m.update(frappe.as_unicode(comp_name + 'HASH_COMPANY_NAME_DIRK').encode('utf-8'))
	return m.hexdigest()


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.requisition"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		apps = []
		filters = {"owner": frappe.session.user}
		for d in frappe.get_all("Cloud Company Requisition", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("Cloud Company Requisition", d.name), keep_owner=True))

		frappe.response.update({
			"ok": True,
			"data": apps
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def save_image_file(comp_name, image_file, image_name):
	fname = secure_filename(repr(image_file.filename))
	ext = fname.rsplit('.', 1)[1].lower()  # 获取文件后缀

	if image_file and allowed_file(fname):  # 判断是否是允许上传的文件类型
		comp_name_hash = hash_company_name(comp_name)
		file_dir = get_requisition_file_path(comp_name_hash)

		new_filename = os.path.join(file_dir, image_name + '.' + ext)  # 修改了上传的文件名
		if os.path.exists(new_filename):
			os.remove(new_filename)
		image_file.save(new_filename)  # 保存文件到upload目录
		return "/files/{0}/{1}/{2}.{3}".format(COMPANY_REQUISITION_FILES, comp_name_hash, image_name, ext)
	else:
		throw("{0}_file_type_error".format(image_name))


@frappe.whitelist(allow_guest=True)
def create():
	try:
		valid_auth_code()
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		data = {
			"doctype": "Cloud Company Requisition",
			"admin": frappe.session.user,
			'comp_name': frappe.form_dict.comp_name,
			'full_name': frappe.form_dict.full_name,
			'credit_code': frappe.form_dict.credit_code,
			'domain': frappe.form_dict.domain,
			'telephone': frappe.form_dict.telephone
		}

		comp_name = data.get("comp_name")
		if not comp_name:
			throw("company_name_missing")

		if not frappe.request.files:
			throw("file_not_found")

		business_licence_file = frappe.request.files.get('business_licence_file')  # 从表单的file字段获取文件，app_file为该表单的name值
		if not business_licence_file:
			throw("business_licence_image_file_not_attached")
		business_licence_file_path = save_image_file(comp_name, business_licence_file, 'business_licence')
		data.update({
			'business_licence': business_licence_file_path
		})

		doc = frappe.get_doc(data).insert()

		frappe.response.update({
			"ok": True,
			"data": doc.name
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

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("Cloud Company Requisition", name)
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
		if not data.get("name"):
			throw("object_name_missing")

		if not frappe.get_value("Cloud Company Requisition", data.get("name"), "name"):
			throw("object_not_found")

		update_doc("Cloud Company Requisition", data)
		frappe.response.update({
			"ok": True,
			"message": "company_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update_business_licence():
	try:
		valid_auth_code()
		name = frappe.form_dict.name
		if not frappe.get_value("Cloud Company Requisition", name, "name"):
			throw("object_not_found")

		f = frappe.request.files.get('file')  # 从表单的file字段获取文件，app_file为该表单的name值
		if not f:
			throw("business_licence_image_file_not_attached")

		doc = frappe.get_doc("Cloud Company Requisition", name)
		file_path = save_image_file(doc.comp_name, f, 'business_licence')
		doc.set("business_licence", file_path)
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
def remove(name):
	try:
		valid_auth_code()
		frappe.delete_doc("Coud Company Requisition", name)
		frappe.response.update({
			"ok": True,
			"message": "company_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

