# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for applications.versions
#

from __future__ import unicode_literals
import os
import frappe
import shutil
from frappe.utils import get_files_path
from werkzeug.utils import secure_filename
from app_center.app_center.doctype.iot_application_version.iot_application_version import get_latest_version
from ioe_api.helper import valid_auth_code, throw, as_dict, get_doc_as_dict


ALLOWED_EXTENSIONS = set(['csv', 'CSV', 'zip', 'ZIP', 'gz', 'GZ', 'tgz', 'TGZ'])


def allowed_file(filename):
	# 用于判断文件后缀
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_app_release_path(app):
	basedir = get_files_path('app_center_files')
	file_dir = os.path.join(basedir, app)
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)

	return file_dir


def get_app_release_filepath(app, version):
	file_dir = get_app_release_path(app)
	ext = frappe.get_value("IOT Application", app, "app_ext")
	filename = str(version) + '.' + ext
	return os.path.join(file_dir, filename)


def valid_app_owner(app):
	if frappe.session.user == 'Administrator':
		return
	if "App Manager" in frappe.get_roles():
		return
	if frappe.get_value('IOT Application', app, 'developer') != frappe.session.user:
		raise frappe.PermissionError(_("You are not owner of application {0}").format(app))


def remove_version_file(app, version):
	valid_app_owner(app)
	try:
		os.remove(get_app_release_filepath(app, version))
		os.remove(get_app_release_filepath(app, version) + ".md5")
	except Exception as ex:
		frappe.logger(__name__).error(repr(ex))


def copy_to_latest(app, version, beta=1):
	valid_app_owner(app)

	from_file = get_app_release_filepath(app, version)
	to_file = get_app_release_filepath(app, "latest.beta" if beta == 1 else "latest")

	shutil.copy(from_file, to_file)
	shutil.copy(from_file + ".md5", to_file + ".md5")


def remove_app_folder(app):
	valid_app_owner(app)
	shutil.rmtree(get_app_release_path(app) + "/.editor")
	shutil.rmtree(get_app_release_path(app))


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "app.tags.test"
	})


@frappe.whitelist(allow_guest=True)
def list(app, beta=1, start_version=0):
	try:
		valid_auth_code()
		version_list = []
		filters = {
			"app": app
		}
		if int(beta) == 0:
			filters.update({"beta": 0})
		if int(start_version) > 0:
			filters.update({"version": ['>=', int(start_version)]})

		for d in frappe.get_all("IOT Application Version", "name", filters, order_by="version desc"):
			version_list.append(as_dict(frappe.get_doc("IOT Application Version", d.name)))

		frappe.response.update({
			"ok": True,
			"data": version_list
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
		if frappe.request.method != "POST":
			throw("method_must_be_post")

		version = int(frappe.form_dict.version)
		app = frappe.form_dict.app
		comment = frappe.form_dict.comment or "Unknown comment"

		valid_app_owner(app)

		if not version:
			throw("version_not_found")

		if not app:
			throw("application_not_found")

		if not frappe.request.files:
			throw("file_not_found")

		if frappe.get_value("IOT Application Version", {"app": app, "version":version}, "name"):
			throw("version_duplicated")

		f = frappe.request.files['app_file']  # 从表单的file字段获取文件，app_file为该表单的name值
		fname = secure_filename(repr(f.filename))

		if f and allowed_file(fname):  # 判断是否是允许上传的文件类型
			file_dir = get_app_release_path(app)

			ext = fname.rsplit('.', 1)[1].lower()  # 获取文件后缀
			ext_wanted = frappe.get_value("IOT Application", app, "app_ext")
			if ext != ext_wanted and ext_wanted != "tar.gz":
				throw("extension_incorrect")

			new_filename = os.path.join(file_dir, str(version) + '.' + ext_wanted)  # 修改了上传的文件名
			f.save(new_filename)  # 保存文件到upload目录

			'''
			Check version file (and automatically correct it?) Only for user application
			'''
			if ext_wanted == 'zip':
				from app_center.editor import editor_revert, editor_worksapce_version, editor_release
				editor_revert(app, version, False)
				got_ver = editor_worksapce_version(app)
				if got_ver != version:
					os.remove(new_filename)
					return editor_release(app, version, comment)

			data = {
				"doctype": "IOT Application Version",
				"app": app,
				"version": version,
				"beta": 1,
				"comment": comment,
			}

			doc = None
			try:
				doc = frappe.get_doc(data).insert()
				os.system("md5sum " + new_filename + " > " + new_filename + ".md5")
			except Exception as ex:
				os.remove(new_filename)
				throw("creation_failed")

			copy_to_latest(app, version)

			frappe.response.update({
				"ok": True,
				"data": as_dict(doc)
			})
		else:
			throw("file_not_allowed!")
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
			"data": get_doc_as_dict("IOT Application Version", name)
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

		# TODO: remove application not implemented so far
		throw("contact_admin")

		frappe.response.update({
			"ok": True,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def latest(app, beta=0):
	try:
		valid_auth_code()
		ver = get_latest_version(app=app, beta=beta)
		frappe.response.update({
			"ok": True,
			"data": ver
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def beta(app, version):
	try:
		valid_auth_code()
		beta = frappe.get_value('IOT Application Version', {"app": app, "version": version}, "beta")
		frappe.response.update({
			"ok": True,
			"data": beta
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def copy_app_release_file(from_app, to_app, version, beta=None):
	from_file = get_app_release_filepath(from_app, version)
	to_file = get_app_release_filepath(to_app, version)
	shutil.copy(from_file, to_file)
	shutil.copy(from_file + ".md5", to_file + ".md5")

	if beta is None:
		beta = frappe.get_value('IOT Application Version', {"app": from_app, "version": version}, "beta")
	copy_to_latest(to_app, version, beta)


def copy_app_icon_file(from_app, to_app):
	from_icon = os.path.join(get_app_release_path(from_app), "icon.png")
	if not os.path.exists(from_icon):
		return
	to_icon = os.path.join(get_app_release_path(to_app), "icon.png")
	shutil.copy(from_icon, to_icon)


def copy_forked_app_files(from_app, to_app, version):
	comment = frappe.get_value('IOT Application Version', {"app": from_app, "version": version}, "comment")
	beta = frappe.get_value('IOT Application Version', {"app": from_app, "version": version}, "beta")
	frappe.get_doc({
		"doctype": "IOT Application Version",
		"app": to_app,
		"version": version,
		"comment": comment,
		"beta": beta
	}).insert()
	copy_app_release_file(from_app, to_app, version, beta)
	copy_app_icon_file(from_app, to_app)
