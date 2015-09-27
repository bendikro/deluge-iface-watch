# -*- coding: utf-8 -*-
#
# Copyright (C) 2012-2015 bendikro bro.devel+yarss2@gmail.com
#
# Based on work by:
# Copyright (C) 2009 Camillo Dell'mour <cdellmour@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# This file is part of YaRSS2 and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

import sys

import pkg_resources
from deluge.plugins.init import PluginInitBase

import ifacewatch.util.logger

log = ifacewatch.util.logger.Logger()


def load_libs():
    egg = pkg_resources.require("IfaceWatch")[0]
    for name in egg.get_entry_map("ifacewatch.libpaths"):
        ep = egg.get_entry_info("ifacewatch.libpaths", name)
        location = "%s/%s" % (egg.location, ep.module_name.replace(".", "/"))
        sys.path.append(location)
        log.info("Appending to sys.path: '%s'" % location)


class CorePlugin(PluginInitBase):
    def __init__(self, plugin_name):
        load_libs()
        from core import Core as CorePluginClass
        self._plugin_cls = CorePluginClass
        super(CorePlugin, self).__init__(plugin_name)


class GtkUIPlugin(PluginInitBase):
    def __init__(self, plugin_name):
        load_libs()
        from gtkui.gtkui import GtkUI as GtkUIPluginClass
        self._plugin_cls = GtkUIPluginClass
        super(GtkUIPlugin, self).__init__(plugin_name)
