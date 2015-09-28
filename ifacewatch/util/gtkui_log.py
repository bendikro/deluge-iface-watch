# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

from deluge.event import DelugeEvent

from ifacewatch.util.common import get_current_date_in_isoformat
from twisted.internet import reactor

import gtk


class GTKUILogger(object):
    """This class handles messages going to the GTKUI log message pane"""

    def __init__(self, textview):
        self.textview = textview

    def gtkui_log_message(self, message):
        def add_msg(message):
            time = get_current_date_in_isoformat()
            buf = self.textview.get_buffer()
            msg_to_append = "(%s): %s\n" % (time, message)
            buf.insert(buf.get_end_iter(), msg_to_append)
            return False
        # Must use callLater to avoid UI freezing in classic mode.
        #reactor.callLater(1, add_msg, message)
        import gobject  # Do not import on top as only the client needs to have this package
        gobject.idle_add(add_msg, message)


class IfaceWatchLogMessageEvent(DelugeEvent):
    """
    Emitted when a message has been written to the log.
    """
    def __init__(self, message):
        """
        :param message: the message to be logged
        """
        self._args = [message]
