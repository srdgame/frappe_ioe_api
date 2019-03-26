# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
from frappe.handler import logout as frappe_logout
from frappe.core.doctype.user.user import sign_up, reset_password as _reset_password, update_password as _update_password
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
from ioe_api.helper import valid_auth_code, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "user.test"
	})


@frappe.whitelist(allow_guest=True)
def valid_auth():
	try:
		valid_auth_code()
		frappe.response.update({
			"ok": True,
			"user": frappe.session.user,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create(email, full_name, redirect_to=None):
	try:
		ret, info = sign_up(email=email, full_name=full_name, redirect_to=redirect_to)

		frappe.response.update({
			"ok": True,
			"result": ret,
			"info": info
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": 'exception',
			"exception": str(ex),
		})


@frappe.whitelist()
def update_password(new_password, logout_all_sessions=0, key=None, old_password=None):
	try:
		user = frappe.session.user
		if user == 'Guest':
			if not key:
				throw("reset_key_required")
			user = frappe.db.get_value("User", {"reset_password_key": key})
			if not user:
				throw("reset_key_incorrect")

		ret = _update_password(new_password, logout_all_sessions, key, old_password)
		if frappe.local.login_manager.user != user:
			throw("update_password_failed")

		frappe.response.update({
			"ok": True,
			"result": ret,
			"info": info
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": 'exception',
			"exception": str(ex),
		})


@frappe.whitelist(allow_guest=True)
def reset_password(email):
	try:
		info = _reset_password(user=email)
		if info == 'not allowed':
			throw('not_allowed')
		if info == 'disabled':
			throw('user_disabled')
		if info == 'not found':
			throw('user_not_found')

		frappe.response.update({
			"ok": True,
			"info": 'password_reset_email_sent'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def login(username, password):
	try:
		frappe.local.login_manager.authenticate(username, password)
		if frappe.local.login_manager.user != username:
			throw("username_password_not_matched")

		frappe.local.login_manager.post_login()

		token = frappe.sessions.get_csrf_token()
		frappe.db.commit()

		companies = list_user_companies(username)
		groups = list_user_groups(username)
		doc = frappe.get_doc("User", frappe.session.user)

		frappe.response.update({
			"ok": True,
			"data": {
				"name": username,
				"csrf_token": token,
				"groups": groups,
				"companies": companies,
				"email": doc.email,
				"phone": doc.phone,
				"first_name": doc.first_name,
				"last_name": doc.last_name
			}
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def csrf_token():
	try:
		token = frappe.sessions.get_csrf_token()
		frappe.db.commit()

		frappe.response.update({
			"ok": True,
			"data": token
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def logout():
	try:
		frappe_logout()

		frappe.response.update({
			"ok": True,
			"data": csrf_token
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": "exception",
			"exception": str(ex)
		})


@frappe.whitelist()
def update(name, email, phone, first_name, last_name):
	try:
		if 'Guest' == frappe.session.user:
			throw("no_permission")

		user = frappe.get_doc("User", name)
		user.update({
			"email": email,
			"phone": phone,
			"first_name": first_name,
			"last_name": last_name
		})
		user.save()

		frappe.response.update({
			"ok": True,
			"info": "user_info_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def read():
	try:
		if 'Guest' == frappe.session.user:
			frappe.response.update({
				"ok": True,
				"data": {
					"name": frappe.session.user,
				}
			})
			return

		user = frappe.get_doc("User", frappe.session.user)
		companies = list_user_companies(frappe.session.user)
		groups = list_user_groups(frappe.session.user)

		frappe.response.update({
			"ok": True,
			"data": {
				"name": user,
				"csrf_token": csrf_token,
				"groups": groups,
				"companies": companies,
				"email": user.email,
				"phone": user.phone,
				"first_name": user.first_name,
				"last_name": user.last_name
			}
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})

