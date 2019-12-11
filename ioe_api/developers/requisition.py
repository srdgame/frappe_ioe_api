# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for developers.requisition
#

from __future__ import unicode_literals
import frappe
import os
import hashlib
from frappe.utils import get_files_path
from werkzeug.utils import secure_filename
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc, as_dict

ALLOWED_EXTENSIONS = set(['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'jpeg'])
DEVELOPER_REQUISITION_FILES = 'developer_requisition_files'


def allowed_file(filename):
	# 用于判断文件后缀
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_requisition_file_path(comp_name_hash):
	basedir = get_files_path(DEVELOPER_REQUISITION_FILES)
	file_dir = os.path.join(basedir, comp_name_hash)
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)

	return file_dir


def hash_user_id(user):
	m = hashlib.md5()
	m.update(frappe.as_unicode(user + 'HASH_DEVELOPER_NAME_DIRK').encode('utf-8'))
	return m.hexdigest()


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "developers.requisition"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		apps = []
		filters = {"owner": frappe.session.user}
		for d in frappe.get_all("App Developer Requisition", "name", filters=filters, order_by="modified desc"):
			apps.append(as_dict(frappe.get_doc("App Developer Requisition", d.name), keep_owner=True))

		frappe.response.update({
			"ok": True,
			"data": apps
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def save_image_file(user, image_file, image_name):
	fname = secure_filename(repr(image_file.filename))
	ext = fname.rsplit('.', 1)[1].lower()  # 获取文件后缀

	if image_file and allowed_file(fname):  # 判断是否是允许上传的文件类型
		user_hash = hash_user_id(user)
		file_dir = get_requisition_file_path(user_hash)

		new_filename = os.path.join(file_dir, image_name + '.' + ext)  # 修改了上传的文件名
		os.remove(new_filename) # TODO: Check more
		image_file.save(new_filename)  # 保存文件到upload目录
		return "/files/{0}/{1}/{2}.{3}".format(DEVELOPER_REQUISITION_FILES, user_hash, image_name, ext)
	else:
		throw("{0}_file_type_error".format(image_name))


@frappe.whitelist(allow_guest=True)
def create():
	try:
		valid_auth_code()

		data = {
			"doctype": "App Developer Requisition",
			"user": frappe.session.user,
			'nickname': frappe.form_dict.nickname,
			'id_card': frappe.form_dict.id_card,
			'address': frappe.form_dict.address,
			'pay_bank': frappe.form_dict.pay_bank,
			'pay_account': frappe.form_dict.pay_account
		}

		id_card_image_file = frappe.request.files['id_card_image_file']  # 从表单的file字段获取文件，app_file为该表单的name值
		if not id_card_image_file:
			throw("business_licence_image_file_not_attached")
		id_card_image_file_path = save_image_file(frappe.session.user, id_card_image_file, 'id_card_image')
		data.update({
			'id_card_image': id_card_image_file_path
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
			"data": get_doc_as_dict("App Developer Requisition", name)
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

		if not frappe.get_value("App Developer Requisition", data.get("name"), "name"):
			throw("object_not_found")

		update_doc("App Developer Requisition", data)
		frappe.response.update({
			"ok": True,
			"message": "company_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update_id_card_image():
	try:
		valid_auth_code()
		name = frappe.form_dict.name
		if not frappe.get_value("App Developer Requisition", name, "name"):
			throw("object_not_found")

		f = frappe.request.files.get('file')  # 从表单的file字段获取文件，app_file为该表单的name值
		if not f:
			throw("id_card_image_file_not_attached")

		doc = frappe.get_doc("App Developer Requisition", name)
		file_path = save_image_file(doc.comp_name, f, 'id_card_image')
		doc.set("id_card_image", file_path)
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

