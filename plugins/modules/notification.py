#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.lucasheld.uptime_kuma.plugins.module_utils.common import object_changed, clear_params, common_module_args, get_notification_by_name

import traceback

from uptime_kuma_api import UptimeKumaApi, params_map_notification_provider, NotificationType

__metaclass__ = type


DOCUMENTATION = r'''
'''

EXAMPLES = r'''
- name: Add notification
  lucasheld.uptime_kuma.notification:
    api_url: http://192.168.1.10:3001
    api_username: admin
    api_password: secret
    name: Notification 1
    type: telegram
    default: false
    telegram_bot_token: 1111
    telegram_chat_id: 2222
    state: present

- name: Edit notification
  lucasheld.uptime_kuma.notification:
    api_url: http://192.168.1.10:3001
    api_username: admin
    api_password: secret
    name: Notification 1
    type: telegram
    default: false
    telegram_bot_token: 6666
    telegram_chat_id: 7777
    state: present

- name: Remove notification
  lucasheld.uptime_kuma.notification:
    api_url: http://192.168.1.10:3001
    api_username: admin
    api_password: secret
    name: Notification 1
    state: absent
'''

RETURN = r'''
'''


def build_provider_args():
    provider_args = {}
    for notification_provider_param in notification_provider_options:
        arg_data = dict(type="str")
        if "password" in notification_provider_param.lower():
            arg_data["no_log"] = True
        provider_args[notification_provider_param] = arg_data
    return provider_args


def run(api, params, result):
    # type -> type_
    params["type_"] = params.pop("type")

    name = params["name"]
    state = params["state"]
    options = clear_params(params)
    # remove unset notification provider options
    options = {k: v for k, v in options.items() if not (k in notification_provider_options and v is None)}

    notification = get_notification_by_name(api, name)

    if state == "present":
        if not notification:
            api.add_notification(**options)
            result["changed"] = True
        else:
            changed_keys = object_changed(notification, options)
            if changed_keys:
                api.edit_notification(notification["id"], **options)
                result["changed"] = True
    elif state == "absent":
        if notification:
            api.delete_notification(notification["id"])
            result["changed"] = True


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        type=dict(type="str", choices=notification_provider_types),
        default=dict(type="bool", default=False),
        state=dict(type="str", default="present", choices=["present", "absent"])
    )
    provider_args = build_provider_args()
    module_args.update(provider_args)
    module_args.update(common_module_args)

    module = AnsibleModule(module_args)
    params = module.params

    api = UptimeKumaApi(params["api_url"])
    api.login(params["api_username"], params["api_password"])

    result = {
        "changed": False
    }

    try:
        run(api, params, result)

        api.disconnect()
        module.exit_json(**result)
    except Exception as e:
        api.disconnect()
        error = traceback.format_exc()
        module.fail_json(msg=error, **result)


if __name__ == '__main__':
    notification_provider_types = list(NotificationType.__dict__["_value2member_map_"].keys())
    notification_provider_options = list(params_map_notification_provider.values())

    main()