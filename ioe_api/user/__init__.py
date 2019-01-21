# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.user.user import sign_up, reset_password as _reset_password
from frappe.utils.password import update_password as _update_password
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
from ..helper import valid_auth_code, throw


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
def register(email, full_name, redirect_to=None):
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
		ret, info = _update_password(new_password, logout_all_sessions, key, old_password)

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
def reset_password():
	try:
		info = _reset_password(user=frappe.session.user)
		if info == 'not allowed':
			throw('not_allowed')
		if info == 'disabled':
			throw('user_disabled')
		if info == 'not found':
			throw('user_not_found')

		frappe.response.update({
			"ok": True,
			"info": 'password_reset_email_has_been_sent'
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def login(user, password):
	try:
		frappe.local.login_manager.authenticate(user, password)
		if frappe.local.login_manager.user != user:
			throw("username_password_not_matched")

		csrf_token = frappe.sessions.get_csrf_token()
		frappe.db.commit()

		companies = list_user_companies(user)
		groups = list_user_groups(user)

		frappe.response.update({
			"ok": True,
			"data": {
				"user": user,
				"csrf_token": csrf_token,
				"groups": groups,
				"companies": companies
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
		csrf_token = frappe.sessions.get_csrf_token()
		frappe.db.commit()

		frappe.response.update({
			"ok": True,
			"data": csrf_token
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist()
def update(name, email, phone, first_name, last_name):
	try:
		if 'Guest' == frappe.session.user:
			throw("have_no_permission")

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
def info():
	try:
		if 'Guest' == frappe.session.user:
			frappe.response.update({
				"ok": True,
				"user": frappe.session.user,
			})
			return

		user = frappe.get_doc("User", frappe.session.user)
		companies = list_user_companies(frappe.session.user)
		groups = list_user_groups(frappe.session.user)

		frappe.response.update({
			"ok": True,
			"data": {
				"user": user,
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

