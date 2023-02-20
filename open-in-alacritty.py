# -*- coding: UTF-8 -*-
# fork of: https://github.com/gnunn1/tilix/blob/master/data/nautilus/open-tilix.py


from gettext import gettext, textdomain

from subprocess import PIPE, call
try:
    from urllib import unquote
    from urlparse import urlparse
except ImportError:
    from urllib.parse import unquote, urlparse


from gi import require_version
require_version('Gtk', '4.0')
require_version('Nautilus', '4.0')
from gi.repository import Gio, GObject, Gtk, Nautilus


TERMINAL = "alacritty"

REMOTE_URI_SCHEME = ['ftp', 'sftp']

textdomain("alacritty")
_ = gettext

def _checkdecode(s):
    """Decode string assuming utf encoding if it's bytes, else return unmodified"""
    return s.decode('utf-8') if isinstance(s, bytes) else s

def open_terminal_in_file(filename):
    if filename:
        call('{0} --working-directory "{1}" &'.format(TERMINAL, filename), shell=True)
    else:
        call("{0} &".format(TERMINAL), shell=True)


class OpenAlacrittyExtension(GObject.GObject, Nautilus.MenuProvider):

    def _open_terminal(self, file_):
        if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
            result = urlparse(file_.get_uri())
            if result.username:
                value = 'ssh -t {0}@{1}'.format(result.username,
                                                result.hostname)
            else:
                value = 'ssh -t {0}'.format(result.hostname)
            if result.port:
                value = "{0} -p {1}".format(value, result.port)
            if file_.is_directory():
                value = '{0} cd "{1}" ; $SHELL'.format(value, result.path)

            call('{0} -e "{1}" &'.format(TERMINAL, value), shell=True)
        else:
            filename = Gio.File.new_for_uri(file_.get_uri()).get_path()
            open_terminal_in_file(filename)

    def _menu_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def _menu_background_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def get_file_items(self, *args):
        files = args[-1]

        if len(files) != 1:
            return
        items = []
        file_ = files[0]

        if file_.is_directory():
            if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
                uri = _checkdecode(file_.get_uri())
                item = Nautilus.MenuItem(name='NautilusPython::open_remote_item',
                                         label=_(u'Open in Remote Terminal'),
                                         tip=_(u'Open Remote Terminal In {}').format(uri))
                item.connect('activate', self._menu_activate_cb, file_)
                items.append(item)

            filename = _checkdecode(file_.get_name())
            item = Nautilus.MenuItem(name='NautilusPython::open_file_item',
                                     label=_(u'Open in Terminal'),
                                     tip=_(u'Open Terminal in {}').format(filename))
            item.connect('activate', self._menu_activate_cb, file_)
            items.append(item)

        return items

    def get_background_items(self, *args):
        file_ = args[-1]

        items = []
        if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
            item = Nautilus.MenuItem(name='NautilusPython::open_bg_remote_item',
                                     label=_(u'Open in Remote Terminal'),
                                     tip=_(u'Open Remote Terminal in this directory'))
            item.connect('activate', self._menu_activate_cb, file_)
            items.append(item)

        item = Nautilus.MenuItem(name='NautilusPython::open_bg_file_item',
                                 label=_(u'Open in Terminal'),
                                 tip=_(u'Open Terminal in this directory'))
        item.connect('activate', self._menu_background_activate_cb, file_)
        items.append(item)
        return items
