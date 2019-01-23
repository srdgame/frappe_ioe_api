# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from ..helper import valid_auth_code, get_post_json_data, throw, update_doc, as_dict


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "gateway.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		# frappe.logger(__name__).debug("List Devices for user {0}").format(user)
		# Get Enteprise Devices
		ent_devices = []
		user = frappe.session.user
		groups = _list_user_groups(user)
		companies = list_user_companies(user)
		for g in groups:
			dev_list = [d[0] for d in frappe.db.get_values("IOT Device", {
				"owner_id": g.name,
				"owner_type": "Cloud Company Group"
			}, "name")]

			ent_devices.append({"group": g.name, "devices": dev_list, "role": g.role})

		# Get Shared Devices
		shd_devices = []
		for shared_group in [ d[0] for d in frappe.db.get_values("IOT ShareGroupUser", {"user": user}, "parent")]:
			# Make sure we will not having shared device from your company
			if frappe.get_value("IOT Share Group", shared_group, "company") in companies:
				continue
			role = frappe.get_value("IOT Share Group", shared_group, "role")

			dev_list = []
			for dev in [d[0] for d in frappe.db.get_values("IOT ShareGroupDevice", {"parent": shared_group}, "device")]:
				dev_list.append(dev)
			shd_devices.append({"group": shared_group, "devices": dev_list, "role": role})

		# Get Private Devices
		pri_devices = [d[0] for d in frappe.db.get_values("IOT Device", {"owner_id": user, "owner_type": "User"}, "name")]

		devices = {
			"company_devices": ent_devices,
			"private_devices": pri_devices,
			"shared_devices": shd_devices,
		}
		frappe.response.update({
			"ok": True,
			"data": devices
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def create(name, device_name, description, owner_type='User', owner_id=None):
	try:
		valid_auth_code()
		# Valid the device owner
		if owner_type == 'Cloud Company Group':
			if not owner_id:
				try:
					company = list_user_companies(frappe.session.user)[0]
					owner_id = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
				except Exception as ex:
					frappe.logger(__name__).error(ex)
					throw("owner_id_fetch_error")
			else:
				if owner_id not in _list_user_groups(frappe.session.user):
					throw("owner_id_invalid")
		else:
			# if owner_type == 'User':
			owner_id = frappe.session.user

		try:
			# Update device name, description and owner stuff
			iot_device = frappe.get_doc("IOT Device", name)

			if iot_device.owner_id:
				if iot_device.owner_id != owner_id or iot_device.owner_type != owner_type:
					throw("device_owner_error")

			iot_device.set("dev_name", device_name)
			iot_device.set("description", description)
			iot_device.update_owner(owner_type, owner_id)
			iot_device.save()
		except Exception as ex:
			frappe.logger(__name__).error(ex)
			throw("gateway_id_invalid")

		frappe.response.update({
			"ok": True,
			"message": "device_added"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def info(name):
	try:
		valid_auth_code()
		device = frappe.get_doc('IOT Device', name)
		if not device.has_permission("read"):
			throw("has_no_permission")

		frappe.response.update({
			"ok": True,
			"data": as_dict(device)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, info):
	try:
		valid_auth_code()
		update_doc("IOT Device", name, info)
		frappe.response.update({
			"ok": True,
			"message": "device_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def remove(*devices):
	try:
		warns = []
		devices = devices or (get_post_json_data()['name'])
		for sn in devices:
			try:
				doc = frappe.get_doc("IOT Device", sn)
				doc.update_owner("", None)
			except Exception as ex:
				warns.append(str(ex))

		if len(warns) > 0:
			frappe.response.update({
				"ok": True,
				"warning": warns
			})
		else:
			frappe.response.update({
				"ok": True,
			})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})



@frappe.whitelist(allow_guest=True)
def exec_result(id):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": 0 # TODO:
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
