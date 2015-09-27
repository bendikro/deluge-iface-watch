# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 bendikro bro.devel+ifacewatch@gmail.com
#
# This file is part of Iface Watch and is licensed under GNU General Public
# License 3.0, or later, with the additional special exception to link portions
# of this program with the OpenSSL library. See LICENSE for more details.
#

import datetime
import os
import sys

import pkg_resources
from deluge.event import DelugeEvent


def get_version():
    """
    Returns the program version from the egg metadata

    :returns: the version of Deluge
    :rtype: string

    """
    return pkg_resources.require("IfaceWatch")[0].version


def is_running_from_egg():
    egg = pkg_resources.require("IfaceWatch")[0]
    return egg.location.endswith(".egg")


def get_deluge_version():
    import deluge.common
    return deluge.common.get_version()


def get_resource(filename, path="data"):
    return pkg_resources.resource_filename("ifacewatch", os.path.join(path, filename))


def get_default_date():
    return datetime.datetime(datetime.MINYEAR, 1, 1, 0, 0, 0, 0)


def get_current_date():
    return datetime.datetime.now()


def get_current_date_in_isoformat():
    return get_current_date().strftime("%Y-%m-%dT%H:%M:%S")


def isodate_to_datetime(date_in_isoformat):
    try:
        return datetime.datetime.strptime(date_in_isoformat, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return get_default_date()


def string_to_unicode(string):
    if type(string) is unicode:
        # Already unicode
        return string
    try:
        return string.decode("utf-8")
    except:
        return string


def method_name():
    return sys._getframe(3).f_code.co_name


def filename(level=3):
    fname = sys._getframe(level).f_code.co_filename
    fname = os.path.splitext(os.path.basename(fname))[0]
    return fname


def linenumber(level=3):
    return sys._getframe(level).f_lineno


def get_exception_string():
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    return ''.join('!! ' + line for line in lines)


def dicts_equals(dict1, dict2, debug=False):
    """Compares two dictionaries, checking that they have the same key/values"""
    ret = True
    if not (type(dict1) is dict and type(dict2) is dict):
        print "dicts_equals: Both arguments are not dictionaries!"
        return False

    key_diff = set(dict1.keys()) - set(dict2.keys())
    if key_diff:
        if debug:
            print "dicts_equals: Keys differ:", key_diff
        return False
    for key in dict1.keys():
        if type(dict1[key]) is dict and type(dict2[key]) is dict:
            if not dicts_equals(dict1[key], dict2[key], debug=debug):
                ret = False
        else:
            # Compare values
            if dict1[key] != dict2[key]:
                if debug:
                    print "Value for key '%s' differs. Value1: '%s', Value2: '%s'" % (key, dict1[key], dict2[key])
                ret = False
    return ret


class IfaceWatchIPChangedEvent(DelugeEvent):
    """
    Emitted when a the listen_interface has changed.
    """
    def __init__(self, ip):
        """
        :param ip: the new IP
        """
        self._args = [ip]
