# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for wps integration wps.file
#


from __future__ import unicode_literals
import frappe
from frappe import throw, _
from time import time
from frappe.utils import get_datetime, get_fullname
from conf_center.api import get_latest_version, app_conf_data
from .helper import valid_weboffice_token
from ioe_api.helper import valid_auth_code


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "wps.file.test"
	})


@frappe.whitelist(allow_guest=True)
def info(_w_appid, _w_access_key, _w_conf_name, _w_conf_version, _w_conf_version_new, _w_signature):
	valid_auth_code(_w_access_key)
	_w_conf_name = _w_conf_name or frappe.get_request_header("x-weboffice-file-id")

	conf_doc = frappe.get_doc("IOT Application Conf", _w_conf_name)
	if conf_doc.public == 0 and conf_doc.developer != frappe.session.user:
		throw("has_no_permission")

	data = app_conf_data(conf_doc.name, _w_conf_version)
	creation = get_datetime(conf_doc.creation)
	modified = get_datetime((conf_doc.modified))


	params = "_w_appid=" + _w_appid + "&_w_conf_name=" + _w_conf_name + "&_w_conf_version=" + _w_conf_version + \
	         "&_w_conf_version_new=" + _w_conf_version_new + "&_w_access_key=" + _w_access_key

	file_info = {
		"id": _w_conf_name,
		"name": conf_doc.app + "-" + conf_doc.name + ".csv",
		"version": int(_w_conf_version_new),
		"size": len(data.get('data') or ''),
		"creator": conf_doc.owner,
		"create_time": int(creation.timestamp()),
		"modifier": conf_doc.developer,
		"modify_time": int(modified.timestamp()),
		"download_url": "https://cloud.thingsroot.com/v1/3rd/file/content?" + params
	}
	user_info = {
		"id": frappe.session.user,
		"name": get_fullname(frappe.session.user),
		"permission": "write" if conf_doc.developer == frappe.session.user else "read"
	}

	frappe.response.update({
		"file": file_info,
		"user": user_info
	})


@frappe.whitelist(allow_guest=True)
def save(_w_appid, _w_access_key, _w_conf_name, _w_conf_version, _w_conf_version_new, _w_signature):
	valid_auth_code(_w_access_key)

	conf_doc = frappe.get_doc("IOT Application Conf", _w_conf_name)

	if conf_doc.developer != frappe.session.user:
		throw("has_no_permission")

	uplaod_file = frappe.request.files['file']
	file_data = uplaod_file.stream.read().decode('utf-8')
	file_size = len(file_data)

	ver = frappe.get_value("IOT Application Conf Version", filters={"conf": _w_conf_name, "version": int(version)})
	if ver:
		doc = frappe.get_doc("IOT Application Conf Version", ver)
		doc.set("data", file_data)
		doc.save()
	else:
		version_data = {
			"doctype": "IOT Application Conf Version",
			"conf": _w_conf_name,
			"version": _w_conf_version_new,
			"comment": "Save from WPS",
			"data": file_data
		}
		doc = frappe.get_doc(version_data).insert()

	params = "_w_appid=" + _w_appid + "&_w_conf_name=" + _w_conf_name + "&_w_conf_version=" + _w_conf_version + \
	         "&_w_conf_version_new=" + _w_conf_version_new + "&_w_access_key=" + _w_access_key

	frappe.response.update({
		"file": {
			"id": _w_conf_name,
			"version": _w_conf_version_new,
			"size": file_size,
			"download_url": "https://cloud.thingsroot.com/v1/3rd/file/content?" + params
		}
	})


def fire_raw_content(content, status=200, content_type='text/html'):
	"""
	I am hack!!!
	:param content:
	:param content_type:
	:return:
	"""
	frappe.response['http_status_code'] = status
	frappe.response['filename'] = ''
	frappe.response['filecontent'] = content
	frappe.response['content_type'] = content_type
	frappe.response['type'] = 'download'


@frappe.whitelist(allow_guest=True)
def content(_w_appid, _w_access_key, _w_conf_name, _w_conf_version, _w_conf_version_new):
	valid_auth_code(_w_access_key)

	conf_doc = frappe.get_doc("IOT Application Conf", _w_conf_name)
	if conf_doc.public == 0 and conf_doc.developer != frappe.session.user:
		throw("has_no_permission")

	data = app_conf_data(conf_doc.name, _w_conf_version)
	return fire_raw_content(data.get("data") or "")


@frappe.whitelist(allow_guest=True)
def online(_w_appid, _w_access_key, _w_conf_name, _w_conf_version, _w_conf_version_new, _w_signature):
	return True


@frappe.whitelist(allow_guest=True)
def version(_w_appid, _w_access_key, _w_conf_name, _w_conf_version, _w_conf_version_new, _w_signature):
	throw("no_implementation")


@frappe.whitelist(allow_guest=True)
def rename():
	throw("no_implementation")


@frappe.whitelist(allow_guest=True)
def history():
	throw("no_implementation")


@frappe.whitelist(allow_guest=True)
def new():
	throw("no_implementation")


