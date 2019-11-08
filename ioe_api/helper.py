# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt
#
# RESTFul API for IOT User which has his/her auth code
#

from __future__ import unicode_literals
import frappe
import json
from frappe import throw, _dict, _
from frappe.model import default_fields


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


class ApiError(Exception):
	http_status_code = 200


def throw(err):
	raise ApiError(err)


def as_dict(doc, keep_modified=True, keep_owner=False, keep_creation=True):
	keep_data = _dict({
		"name": doc.name
	})
	if keep_modified:
		keep_data['modified'] = doc.modified
	if keep_owner:
		keep_data['owner'] = doc.owner
	if keep_creation:
		keep_data['creation'] = doc.creation

	return doc.as_dict(no_default_fields=True).update(keep_data)


def get_doc_as_dict(doc_type, name, keep_modified=True, keep_owner=False, keep_creation=True):
	doc = None
	try:
		doc = frappe.get_doc(doc_type, name)
	except Exception as ex:
		throw("object_not_found")

	return as_dict(doc, keep_modified=keep_modified, keep_owner=keep_owner, keep_creation=keep_creation)


def update_doc(doc_type, d):
	if frappe.request.method != "POST":
		throw("method_must_be_post")

	d = _dict(d)
	if not d.name:
		throw("object_name_not_found")
	doc = None
	try:
		doc = frappe.get_doc(doc_type, d.name)
	except Exception as ex:
		throw("object_not_found")

	for key in default_fields:
		if key in d:
			del d[key]

	return doc.update(d).save()


def get_tags(doctype, name):
	tags = [tag.tag for tag in frappe.get_all("Tag Link", filters={
			"document_type": doctype,
			"document_name": name
		}, fields=["tag"])]

	return ",".join([tag for tag in tags])
# def get_tags(doctype, name):
# 	return [tag.tag for tag in frappe.get_all("Tag Link", filters={
# 			"document_type": doctype,
# 			"document_name": name
# 		}, fields=["tag"])]


def update_tags(doc, tags):
	from frappe.desk.doctype.tag.tag import update_tags as _update_tags
	return _update_tags(doc, tags)