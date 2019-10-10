# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for gateway
#

from __future__ import unicode_literals
import frappe
import redis
import json
import uuid
from six import text_type, string_types
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import is_user_in_group as _is_user_in_group
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, update_doc, as_dict
from iot.device_api import send_action, get_action_result


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
def create(name, dev_name, description, owner_type='User', owner_id=None):
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
				if not _is_user_in_group(owner_id, frappe.session.user):
					throw("owner_id_invalid")
		else:
			# if owner_type == 'User':
			owner_id = frappe.session.user

		iot_device = None
		try:
			# Update device name, description and owner stuff
			iot_device = frappe.get_doc("IOT Device", name)
		except Exception as ex:
			frappe.logger(__name__).error(ex)
			throw("gateway_id_invalid")

		if iot_device.owner_id:
			if iot_device.owner_id != owner_id or iot_device.owner_type != owner_type:
				throw("device_owned_by_others")

		iot_device.set("dev_name", dev_name)
		iot_device.set("description", description)
		iot_device.update_owner(owner_type, owner_id, ignore_permissions=True)

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
def read(name):
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
def update():
	try:
		valid_auth_code()
		data = get_post_json_data()
		update_doc("IOT Device", data)
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
def remove():
	try:
		valid_auth_code()

		warns = []
		devices = (get_post_json_data()['name'])
		if isinstance(devices, string_types):
			devices = [devices]
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

		try:
			result = get_action_result(id)
		except Exception as ex:
			frappe.response.update({
				"ok": False,
				"error": "exception",
				"exception": str(ex)
			})

		frappe.response.update({
			"ok": True,
			"data": result
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


def fire_action(id, action, gateway, data):
	try:
		if id is None:
			id = str(uuid.uuid1()).upper()
		return send_action("sys", action=action, id=id, device=gateway, data=data)
	except Exception as ex:
		throw("exception")


@frappe.whitelist(allow_guest=True)
def upgrade(name, version=None, no_ack=1, skynet_version=None, id=None):
	try:
		if not version and not skynet_version:
			throw("version_missing")

		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		data = {
			"no_ack": no_ack,
		}
		if version is not None:
			data.update({
				"version": version
			})
		if skynet_version is not None:
			data.update({
				"skynet": {"version": skynet_version}
			})

		ret = fire_action(id=id, action="upgrade", gateway=name, data=data)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def upgrade_ack(name, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="upgrade/ack", gateway=name, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable_data(name, enable=1, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/data", gateway=name, data=enable)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable_data_one_short(name, duration=60, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/data_one_short", gateway=name, data=duration)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def data_snapshot(name, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="data/snapshot", gateway=name, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def data_flush(name, id=None):
	'''
	Force flush buffered data
	'''
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="data/flush", gateway=name, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable_log(name, duration=60, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/log", gateway=name, data=duration)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable_comm(name, duration=60, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/comm", gateway=name, data=duration)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def enable_stat(name, enable=1, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/stat", gateway=name, data=enable)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


# Enable/Disable event upload, disable if min_level is minus number or it is the minimum event level
@frappe.whitelist(allow_guest=True)
def enable_event(name, min_level=1, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="enable/event", gateway=name, data=min_level)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


# Enable/Disable event upload, disable if min_level is minus number or it is the minimum event level
@frappe.whitelist(allow_guest=True)
def run_batch_script(name, script, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="batch_script", gateway=name, data=script)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def restart(name, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="restart", gateway=name, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def reboot(name, id=None):
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="reboot", gateway=name, data={})

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def cloud_conf(name, data, id=None):
	'''
	Change IOT Device Cloud Settings, data example: {"ID": "IDIDIDIDIDID", "HOST": "ioe.symgrid.com", ...}
		Valid keys: ID/CLOUD_ID/HOST/PORT/TIMEOUT/PKG_HOST_URL/CNF_HOST_URL/DATA_UPLOAD/DATA_UPLOAD_PERIOD/COV/COV_TTL
	:return:
	'''
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		ret = fire_action(id=id, action="cloud_conf", gateway=name, data=data)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def download_cfg(name, cfg_name, host=None, id=None):
	'''
	Download IOT Device CFG, data example: {"name": "deab2776ef", "host": "ioe.symgrid.com"}  host is optional
	:return:
	'''
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		data={"name": cfg_name}
		if host is not None:
			data.update({"host": host})
		ret = fire_action(id=id, action="cfg/download", gateway=name, data=data)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def upload_cfg(name, host=None, id=None):
	'''
	Download IOT Device CFG, data example: {"host": "ioe.symgrid.com"}  host is optional
	:return:
	'''
	try:
		valid_auth_code()
		doc = frappe.get_doc('IOT Device', name)
		if not doc.has_permission("write"):
			throw("has_no_permission")

		data = {}
		if host is not None:
			data.update({"host": host})
		ret = fire_action(id=id, action="cfg/upload", gateway=name, data=data)

		frappe.response.update({
			"ok": True,
			"data": ret
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
