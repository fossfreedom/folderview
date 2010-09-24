#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import gobject
import gtk
import os
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

        self.entry_list = []
        
        self.g_client = gconf.client_get_default()
        self.library_location = urllib.unquote(self.g_client.get_list('/apps/rhythmbox/library_locations', gconf.VALUE_STRING)[0])
        log.info('FolderView')

        #for i in dir(rb):
        #    print i
        #print self.db.entry_type_get_by_name("song")

    def do_impl_activate(self):
        self.shell  = self.get_property('shell')
        self.db     = self.shell.get_property('db')
        self.entry_type=self.get_property('entry-type')
        rb.BrowserSource.do_impl_activate(self)

    def set_entry(self, uri):
        try:
            meta = rb.MetaData()
            meta.load(uri)
            metadata_list = [
                            #rb.METADATA_FIELD_TITLE,
                            rb.METADATA_FIELD_ARTIST,
                            rb.METADATA_FIELD_ALBUM,
                            rb.METADATA_FIELD_GENRE,
                            rb.METADATA_FIELD_TRACK_NUMBER,
                            rb.METADATA_FIELD_DISC_NUMBER,
                            rb.METADATA_FIELD_DATE,
                            rb.METADATA_FIELD_DURATION,
                            rb.METADATA_FIELD_BITRATE,
                            rb.METADATA_FIELD_TRACK_GAIN,
                            rb.METADATA_FIELD_TRACK_PEAK,
                            rb.METADATA_FIELD_ALBUM_GAIN,
                            rb.METADATA_FIELD_ALBUM_PEAK,
                            rb.METADATA_FIELD_MUSICBRAINZ_TRACKID,
                            rb.METADATA_FIELD_MUSICBRAINZ_ARTISTID,
                            rb.METADATA_FIELD_MUSICBRAINZ_ALBUMID,
                            rb.METADATA_FIELD_MUSICBRAINZ_ALBUMARTISTID,
                            rb.METADATA_FIELD_ARTIST_SORTNAME,
                            rb.METADATA_FIELD_ALBUM_SORTNAME
                            ]
            prop_list = [
                        #rhythmdb.PROP_TITLE,
                        rhythmdb.PROP_ARTIST,
                        rhythmdb.PROP_ALBUM,
                        rhythmdb.PROP_GENRE,
                        rhythmdb.PROP_TRACK_NUMBER,
                        rhythmdb.PROP_DISC_NUMBER,
                        rhythmdb.PROP_DATE,
                        rhythmdb.PROP_DURATION,
                        rhythmdb.PROP_BITRATE,
                        rhythmdb.PROP_TRACK_GAIN,
                        rhythmdb.PROP_TRACK_PEAK,
                        rhythmdb.PROP_ALBUM_GAIN,
                        rhythmdb.PROP_ALBUM_PEAK,
                        rhythmdb.PROP_MUSICBRAINZ_TRACKID,
                        rhythmdb.PROP_MUSICBRAINZ_ARTISTID,
                        rhythmdb.PROP_MUSICBRAINZ_ALBUMID,
                        rhythmdb.PROP_MUSICBRAINZ_ALBUMARTISTID,
                        rhythmdb.PROP_ARTIST_SORTNAME,
                        rhythmdb.PROP_ALBUM_SORTNAME
                        ]
            #log.info('%s:%s'%(uri,type(meta.get(rb.METADATA_FIELD_DURATION))))
            if meta.get(rb.METADATA_FIELD_DURATION) == 0:
                return
            entry = self.db.entry_new(self.entry_type,uri)
            if meta.get(rb.METADATA_FIELD_TITLE) == None:
                self.db.set(entry, rhythmdb.PROP_TITLE, os.path.split(uri)[1])
            else:
                self.db.set(entry, rhythmdb.PROP_TITLE, meta.get(rb.METADATA_FIELD_TITLE))
            for i in range(len(metadata_list)):
                tmp = meta.get(metadata_list[i])
                if tmp is not None:
                    self.db.set(entry, prop_list[i], meta.get(metadata_list[i]))
        except:
            pass

    def on_treeview_cursor_changed(self, widget):
        for row in self.props.query_model:
            entry = row[0]
            self.db.entry_delete(entry)
        
        model = widget.get_model()
        path = self.filebrowser.get_selected()
        for item in os.listdir(path):
            filename = os.path.join(path, item)
            if os.path.isfile(filename):
                self.set_entry(path_to_uri(filename))
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
    return 'file://'+path

gobject.type_register(FolderViewSource)
