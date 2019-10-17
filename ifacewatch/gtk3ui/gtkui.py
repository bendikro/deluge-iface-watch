# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later.
#
import gi  # isort:skip
gi.require_version('Gdk', '3.0')  # noqa: F401
gi.require_version('Gtk', '3.0')  # noqa: F401
gi.require_version('PangoCairo', '1.0')  # noqa: F401

# isort:imports-thirdparty
from gi.repository import Gtk

import deluge.component as component
from deluge.plugins.pluginbase import Gtk3PluginBase
from deluge.ui.client import client

from ifacewatch.util.common import get_resource
from ifacewatch.util.gtkui_log import GTKUILogger
from ifacewatch.util.logger import Logger


class GtkUI(Gtk3PluginBase):

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

    def get_object(self, name):
        return self.builder.get_object(name)

    def create_ui(self):
        self.builder = Gtk.Builder.new_from_file(get_resource("ifacewatch.ui"))
        self.ifacewatch_window = self.get_object('ifacewatch_window')
        self.builder.connect_signals({
            "on_checkbutton_active_toggled": self.on_checkbutton_active_toggled,
        })
        box = self.get_object("ifacewatch_prefs_box")
        component.get("Preferences").add_page("IfaceWatch", box)
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        self.gtkui_log = GTKUILogger(self.get_object("textview_log"))
        self.log = Logger(gtkui_logger=self.gtkui_log)

###############################
# Update config and lists data
###############################

    def on_checkbutton_active_toggled(self, widget):
        active = self.get_object("checkbutton_active").get_active()
        client.ifacewatch.save_config({"active": active})

    def on_apply_prefs(self):
        """Called when the 'Apply' button is pressed"""
        iface = self.get_object("interface_combobox").get_active_text()
        interval = self.get_object("spinbutton_update_interval").get_value()
        active = self.get_object("checkbutton_active").get_active()

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
        client.ifacewatch.get_interfaces().addCallback(self.on_get_interfaces)

    def on_get_interfaces(self, ifaces):
        interface_combobox = self.get_object("interface_combobox")
        current_iface = self.last_config['interface']

        ifaces_in_model = []
        model = interface_combobox.get_model()
        for i in range(len(model)):
            it = model.get_iter(i)
            value = model.get_value(it, 0)
            ifaces_in_model.append(value)

        #  Add interfaces not already in the list
        for i, iface in enumerate(ifaces):
            if iface in ifaces_in_model:
                continue
            interface_combobox.append_text(iface)

        # Get the index of the active text
        active_index = -1
        for i in range(len(model)):
            it = model.get_iter(i)
            value = model.get_value(it, 0)
            if value == current_iface:
                active_index = i

        if active_index != -1:
            interface_combobox.set_active(active_index)

    def cb_on_log_message_event(self, message):
        """Callback function called on GtkUILogMessageEvent events"""
        self.gtkui_log.gtkui_log_message(message)

    def cb_get_config(self, config):
        """Callback function called after saving data to core"""
        if config is None:
            self.log.error("An error has occured. Cannot load data from config")
        else:
            self.last_config = config
            self.get_object("spinbutton_update_interval").set_value(int(config['update_interval']))
            self.get_object("checkbutton_active").set_active(config['active'])
            self.set_iface_value(config['interface'])

    def get_iface_value(self):
        interface_combobox = self.get_object("interface_combobox")
        text = interface_combobox.get_active_text()
        return text

    def set_iface_value(self, interface):
        interface_combobox = self.get_object("interface_combobox")
        model = interface_combobox.get_model()
        for i in range(len(model)):
            it = model.get_iter(i)
            v = model.get_value(it, 0)
            if v == interface:
                interface_combobox.set_active(i)
                return

        interface_combobox.append_text(interface)
        interface_combobox.set_active(0)

    def cb_get_ip(self, ip):
        self.update_ip(ip)

    def update_ip(self, ip):
        label = self.get_object("label_IP_value")
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
