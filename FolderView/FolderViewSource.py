#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import gobject
import gtk
import os
import gio
import copy
import urllib
import gconf
import rb,rhythmdb
import treefilebrowser
import logging,logging.handlers

log=logging.getLogger('FolderView')

class FolderViewSource(rb.BrowserSource):
    #__gproperties__ = {'plugin': (rb.Plugin, 'plugin', 'plugin', gobject.PARAM_WRITABLE|gobject.PARAM_CONSTRUCT_ONLY),}
    
    def __init__(self):
        rb.BrowserSource.__init__(self)

        self.shell = None
        
        self.g_client = gconf.client_get_default()
        self.library_location = urllib.unquote(self.g_client.get_list('/apps/rhythmbox/library_locations', gconf.VALUE_STRING)[0])
        log.info('FolderView')

    def do_impl_activate(self):
        log.info('Activate')
        if self.shell == None:
            self.shell  = self.get_property('shell')
            self.db     = self.shell.get_property('db')
        
        rb.BrowserSource.do_impl_activate(self)

    def set_entry(self, uri):
        entry = self.db.entry_lookup_by_location(uri)
        if entry != None:
            if self.db.entry_get(entry, rhythmdb.PROP_DURATION) != 0:
                self.props.base_query_model.add_entry(entry, 0)

    def on_treeview_cursor_changed(self, widget):
        for row in self.props.query_model:
            entry = row[0]
            self.props.query_model.remove_entry(entry)
        
        path = self.filebrowser.get_selected()
        for item in os.listdir(path):
            filename = os.path.join(path, item)
            if os.path.isfile(filename):
                self.set_entry(path_to_uri(filename))
        #query = self.db.query_new()
        #song_type = self.db.entry_type_get_by_name('song')
        #self.db.query_append(query, (rhythmdb.QUERY_PROP_EQUALS, rhythmdb.PROP_TYPE, song_type))
        #self.db.do_full_query_parsed(self.props.query_model, query)
        self.db.commit()

    def do_impl_pack_paned (self, paned):
        self.__paned_box = gtk.HPaned()
        self.filebrowser = treefilebrowser.TreeFileBrowser(self.library_location[7:])
        self.scrolled = self.filebrowser.get_scrolled()
        self.scrolled.set_size_request(200,-1)
        self.treeview = self.filebrowser.get_view()
        self.treeview.connect('cursor-changed', self.on_treeview_cursor_changed)
        self.pack_start(self.__paned_box)
        self.__paned_box.add1(self.scrolled)
        self.__paned_box.add2(paned)
        

def path_to_uri(path):
    gfile = gio.File(path)
    return gfile.get_uri()

gobject.type_register(FolderViewSource)
