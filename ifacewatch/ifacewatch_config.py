# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

import copy

import deluge.configmanager

CONFIG_FILENAME = "ifacewatch.conf"

__DEFAULT_PREFS = {
    "interface": "",
    "active": True,
    "update_interval": 10,
}


def default_prefs():
    return copy.deepcopy(__DEFAULT_PREFS)


class IfacewatchConfig(object):

    def __init__(self, logger, config=None, core_config=None, verify_config=True):
        self.log = logger
        self.config = config

        if config is None:
            self.config = deluge.configmanager.ConfigManager(CONFIG_FILENAME, default_prefs())
            self.config.save()

        if verify_config:
            self._verify_config()

    def save(self):
        self.config.save()

    def get_config(self):
        "returns the config dictionary"
        config = copy.copy(self.config.config)
        return config

    def set_config(self, config):
        """Replaces the config data in self.config with the available keys in config"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    def _verify_config(self):
        """Adding missing keys, in case a new version adds more config fields"""
        # Update config
        pass

    def run_for_each_dict_element(self, conf_dict, update_func):
        for key in conf_dict.keys():
            update_func(conf_dict[key])
