# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later.
#

import gtk

from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component

from ifacewatch.util.logger import Logger
from ifacewatch.util.gtkui_log import GTKUILogger
from ifacewatch.util.common import get_resource


class GtkUI(GtkPluginBase):

    def enable(self):
        self.last_config = None
        self.create_ui()
        self.on_show_prefs()  # Necessary for the first time when the plugin is installed
        client.register_event_handler("IfaceWatchLogMessageEvent", self.cb_on_log_message_event)
        client.register_event_handler("IfaceWatchIPChangedEvent", self.cb_get_ip)

    def disable(self):
        self.last_config = None
        component.get("Preferences").remove_page("IfaceWatch")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)

    def create_ui(self):
        self.glade = gtk.glade.XML(get_resource("ifacewatch.glade"))
        self.ifacewatch_window = self.glade.get_widget('ifacewatch_window')
        box = self.glade.get_widget("ifacewatch_prefs_box")

        self.glade.signal_autoconnect({
            "on_checkbutton_active_toggled": self.on_checkbutton_active_toggled,
        })
        component.get("Preferences").add_page("IfaceWatch", box)
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        self.gtkui_log = GTKUILogger(self.glade.get_widget("textview_log"))
        self.log = Logger(gtkui_logger=self.gtkui_log)

###############################
# Update config and lists data
###############################

    def on_checkbutton_active_toggled(self, widget):
        active = self.glade.get_widget("checkbutton_active").get_active()
        client.ifacewatch.save_config({"active": active})

    def on_apply_prefs(self):
        """Called when the 'Apply' button is pressed"""
        iface = self.glade.get_widget("entry_interface").get_text()
        interval = self.glade.get_widget("spinbutton_update_interval").get_value()
        active = self.glade.get_widget("checkbutton_active").get_active()

        if self.last_config is not None:
            if self.last_config['interface'] != iface:
                self.log.info("New interface specified: '%s'" % iface)
            elif self.last_config['update_interval'] != interval:
                pass
            else:
                return
        client.ifacewatch.save_config({"interface": iface, "update_interval": int(interval),
                                       "active": active})

    def on_show_prefs(self):
        """Called when showing preferences window"""
        client.ifacewatch.get_config().addCallback(self.cb_get_config)
        client.ifacewatch.get_ip().addCallback(self.update_ip)

    def cb_on_log_message_event(self, message):
        """Callback function called on GtkUILogMessageEvent events"""
        self.gtkui_log.gtkui_log_message(message)

    def cb_get_config(self, config):
        """Callback function called after saving data to core"""
        if config is None:
            self.log.error("An error has occured. Cannot load data from config")
        else:
            self.last_config = config
            self.glade.get_widget("entry_interface").set_text(config['interface'])
            self.glade.get_widget("spinbutton_update_interval").set_value(int(config['update_interval']))
            self.glade.get_widget("checkbutton_active").set_active(config['active'])

    def cb_get_ip(self, ip):
        self.update_ip(ip)

    def update_ip(self, ip):
        label = self.glade.get_widget("label_IP_value")
        # May happen if the plugin is not actually enabled
        if label is None:
            return
        label.set_text(ip)
        main_prefs = component.get("Preferences")
        # Support both Deluge v1.3 and v2
        if hasattr(main_prefs, "glade"):
            main_prefs.glade.get_widget("entry_interface").set_text(ip)
        else:
            main_prefs.builder.get_object("entry_interface").set_text(ip)
