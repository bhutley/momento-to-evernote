#!/usr/bin/env python
#
# A script to upload Momento app diary entries to Evernote as notes
# within a specified folder.
# 
# Written by Brett Hutley <brett@hutley.net>
#
import os, sys
import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import cgi
import re

optp = OptionParser()
optp.add_option("-c", "--config", dest="config_file", metavar="FILE",
                default= os.path.join(os.path.expanduser("~"), ".momento-to-evernote.cfg"),
                help="Momento-to-Evernote configuration file")
optp.add_option("-d", "--momento-dir", dest="momento_dir", 
                default=".",
                help="Load files from the specified directory")
optp.add_option("-f", "--from-date", dest="from_date", 
                default=None,
                help="Load files on and after the specified date (YYYY-MM-DD format)")
optp.add_option("-n", "--notebook", dest="notebook", 
                default=None,
                help="Create new notes in the specified notebook")

opts, args = optp.parse_args()

if not os.path.exists(opts.config_file):
    error("config file '%s' doesn't exist" % opts.config_file)
    exit(1)

config_parser = SafeConfigParser()
config_parser.read(opts.config_file)

# Real applications authenticate with Evernote using OAuth, but for the
# purpose of exploring the API, you can get a developer token that allows
# you to access your own Evernote account. To get a developer token, visit
# https://sandbox.evernote.com/api/DeveloperToken.action

auth_token = config_parser.get('default', 'auth_token')

notebook_name = opts.notebook
if notebook_name is None:
    notebook_name = config_parser.get('default', 'notebook')


momento_dir = opts.momento_dir
from_date = opts.from_date

if not os.path.isdir(momento_dir):
    print("ERROR: %s is not a directory" % (momento_dir, ))
    exit(0)

attachments_dir = os.path.join(momento_dir, "Attachments")
attachments = {}

if os.path.isdir(attachments_dir):
    for f in os.listdir(attachments_dir):
        if f.endswith(".jpg"):
            dt = f.split('_')[2]
            dt = dt[:-4]
            attachments[dt] = os.path.join(attachments_dir, f)
    

client = EvernoteClient(token=auth_token, sandbox=False)

note_store = client.get_note_store()

notebook_guid = None
notebooks = note_store.listNotebooks()
print "Found ", len(notebooks), " notebooks:"
for notebook in notebooks:
    if notebook.name == notebook_name:
        notebook_guid = notebook.guid
        break

if notebook_guid is None:
    print("Failed to find '%s' notebook in Evernote" % (notebook_name, ))
    exit(0)

def diary_entry_to_html(filename):
    html = ''
    h1 = None
    got_underline = False
    f = open(filename, 'r')
    for line in f:
        line = line.strip()
        html += "%s<br/>\n" % (cgi.escape(line), )
    f.close()
        
    return html

momento_file_filter = re.compile(r'\d{4}\.\d{2}\.\d{2} - .*\.txt')
for f in os.listdir(momento_dir):
    if momento_file_filter.match(f) is not None:
        dt = f[0:10]

        title = dt.replace('.', '-')

        if from_date is not None and title < from_date:
            continue

        momento_filename = os.path.join(momento_dir, f)
        diary_content = diary_entry_to_html(momento_filename)

        note = Types.Note()
        note.title = title
        
        note.notebookGuid = notebook_guid
        
        note.content = '<?xml version="1.0" encoding="UTF-8"?>'
        note.content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += "<en-note>"
        note.content += diary_content
        
        #print("'%s'" % (dt, ))
        if dt in attachments:
            img_file = attachments[dt]
            image = open(img_file, 'rb').read()
            md5 = hashlib.md5()
            md5.update(image)
            hash = md5.digest()
        
            data = Types.Data()
            data.size = len(image)
            data.bodyHash = hash
            data.body = image
        
            resource = Types.Resource()
            resource.mime = 'image/png'
            resource.data = data
        
            note.resources = [resource]
        
            # To display the Resource as part of the note's content,
            # include an <en-media> tag in the note's ENML
            # content. The en-media tag identifies the corresponding
            # Resource using the MD5 hash.
            hash_hex = binascii.hexlify(hash)
            note.content += '<en-media type="image/png" hash="' + hash_hex + '"/>'
        
        note.content += "</en-note>"
        try:
            created_note = note_store.createNote(note)
            print "Successfully created a new note for %s: %s" % (title, created_note.guid, )
        except:
            print("**** Failed to create note for %s!" % (title, ))
            exit(0)

