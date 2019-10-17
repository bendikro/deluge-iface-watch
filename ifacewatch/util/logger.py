# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

from OpenSSL.SSL import Error as SSLError
from twisted.internet import reactor

import deluge.component as component
from deluge.log import LOG as log  # NOQA

from . import common
from .gtkui_log import IfaceWatchLogMessageEvent


class Logger(object):

    def __init__(self, gtkui_logger=None):
        self.gtkui_logger = gtkui_logger

    def handle_gtkui_log(self, message, gtkui):
        if not gtkui:
            return
        # On gtkui client
        if self.gtkui_logger:
            self.gtkui_logger.gtkui_log_message(message)
        else:  # On deluge daemon
            self.gtkui_log_message_event(message)

    def debug(self, message, gtkui=True):
        log.debug(self._msg(message))
        self.handle_gtkui_log(message, gtkui)

    def info(self, message, gtkui=True):
        log.info(self._msg(message))
        self.handle_gtkui_log(message, gtkui)

    def warn(self, message, gtkui=True):
        log.warn(self._msg(message))
        self.handle_gtkui_log(message, gtkui)

    def error(self, message, gtkui=True):
        log.error(self._msg(message))
        self.handle_gtkui_log(message, gtkui)

    def _msg(self, msg):
        return "%s.%s:%s: %s" % ("IfaceWatch", common.filename(), common.linenumber(), msg)

    def gtkui_log_message_event(self, message):
        try:
            # Tests throws KeyError for EventManager when running this method, so wrap this in try/except
            eventmanager = component.get("EventManager")
            reactor.callLater(1, eventmanager.emit, IfaceWatchLogMessageEvent(message))
        except KeyError:
            pass
        except SSLError:
            log.info("Caught OpenSSL.SSL.Error in gtkui_log_message_event")
