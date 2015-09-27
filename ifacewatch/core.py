# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

import platform

import deluge.common
import deluge.component as component
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase
from twisted.internet.task import LoopingCall

import ifacewatch.util.common
import ifacewatch.util.logger
from ifacewatch.ifacewatch_config import IfacewatchConfig
from ifacewatch.lib.pyiface.iface import Interface
from ifacewatch.lib import ifcfg
from ifacewatch.util.common import IfaceWatchIPChangedEvent


class Core(CorePluginBase):

    def __init__(self, name):
        """Used for tests only"""
        if name is not "test":
            super(Core, self).__init__(name)
        else:
            # To avoid warnings when running tests
            self._component_name = name

        self.timer = None
        self.config = None
        self.ip = None
        self.log = ifacewatch.util.logger.Logger()
        self.log.info("Core init", gtkui=True)
        self.core = component.get("Core")
        self.core.config.register_set_function("listen_interface", self.interface_changed)

    def interface_changed(self, iface, ip):
        component.get("EventManager").emit(IfaceWatchIPChangedEvent(ip))

    def enable(self, config=None):
        if config is None:
            self.config = IfacewatchConfig(self.log)
        else:
            self.config = config
        self.log.info("Enabled Iface Watch %s" % ifacewatch.util.common.get_version())

        self.scheduler_timer()
        self.check_interface()

    def scheduler_timer(self):
        if self.timer:
            if self.timer.running:
                self.timer.stop()
        else:
            self.timer = LoopingCall(self.check_interface)

        interval = int(self.config.get_config()["update_interval"])
        if self.config.get_config()["active"]:
            self.timer.start(interval * 6, now=True)  # Multiply to get seconds
            self.log.info("Scheduling watch with interval %s." %
                          self.config.get_config()["update_interval"], gtkui=True)
        else:
            self.log.info("Watch mode disabled", gtkui=True)

    def disable(self):
        self.config.save()

    def update(self):
        pass

    def check_interface(self, *args, **kwargs):
        if self.config is None:
            return True
        prev_ip = self.ip
        self.ip = None
        iface = self.config.get_config()["interface"]

        if iface.strip():
            try:
                for interface in ifcfg.interfaces().itervalues():
                    if interface["device"] == iface:
                        self.ip = interface["inet"]
                        break
                if self.ip is None and platform.system() == "Linux":
                    iff = Interface(name=str(iface))
                    self.ip = iff.ip_str()
                if self.ip is not None and not deluge.common.is_ip(self.ip):
                    self.log.info("Invalid IP returned for interface '%s': %s" % (iface, self.ip), gtkui=True)
                    self.ip = None
            except TypeError as e:
                self.log.error("TypeError: %s" % e, gtkui=True)
                return True
        else:
            self.ip = ""
            iface = "<all>"

        if self.ip is None:
            return True

        has_changed = prev_ip != self.ip

        if prev_ip is not None and has_changed:
            self.log.info("IP from interface %s is new: %s -> %s" %
                          (iface, prev_ip, self.ip if self.ip else "0.0.0.0"), gtkui=True)
        if has_changed:
            self.log.info("Updating with IP '%s'" % (self.ip if self.ip else "0.0.0.0"), gtkui=True)
            self.core.set_config({"listen_interface": self.ip})

        return True

    @export
    def get_ip(self):
        """Returns the config dictionary"""
        return self.core.get_config_value("listen_interface")

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.get_config()

    @export
    def save_config(self, config):
        newiface = "interface" in config and config["interface"] != self.config.get_config()["interface"]
        newinterval = ("update_interval" in config and
                       config["update_interval"] != self.config.get_config()["update_interval"])
        newstate = config["active"] != self.config.get_config()["active"]
        self.config.set_config(config)
        if newstate and config["active"] is True:
            self.log.info("Watch mode enabled")
        if newiface:
            self.check_interface()
        if newinterval or newstate:
            self.scheduler_timer()
