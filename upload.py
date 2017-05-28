#coding: utf-8

import json
import sys
import re
#from glob import glob
from os import listdir
from os.path import isfile, isdir, join, splitext, basename

#import codecs

import cloudinary
import cloudinary.uploader
import cloudinary.api

#r'C:\srv\htdocs\projects\hosted-at-gd\assets\jk\photos\pics'
CONFIG_PATH = r'L:\Documents\Data\_cloudinary.json'

#EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png']
EXTENSIONS = ['.jpg', '.gif', '.png']

DATA_FILE_NAME = 'upload-data.txt'

MAX_WIDTH = None

PAT_ALPHANUM = re.compile(r"^[a-z0-9]+(?:-*[a-z0-9]+)*$", re.I)
PAT_CLEAN = re.compile(r"[^a-z0-9]+", re.I)

def get_config():
    if not isfile(CONFIG_PATH):
        print "Configuration file not found: '%s'" % CONFIG_PATH
        return
    with open(CONFIG_PATH, 'r') as f:
        return json.loads(f.read())


def read_input():
    '''
    Command line parameters:
    - source directory path
    - destination folder ('-' to leave unset)
    - max. width (optional)
    - max. height (optional, same as max. width by default)
    '''
    input = sys.argv[1:]
    size = len(input)
    data = {}
    data['dir'] = input[0] if size > 0 else ''
    data['dest'] = input[1] if size > 1 and input[1] != '-' else ''
    data['max_w'] = int(input[2]) if size > 2 else MAX_WIDTH
    data['max_h'] = int(input[3]) if size > 3 else data['max_w']
    return data


def is_image(fpath):
    return True if fpath and splitext(fpath)[1].lower() in EXTENSIONS and isfile(fpath) else False


def get_name_type(fpath):
    parts = splitext(basename(fpath))
    fname = PAT_CLEAN.sub(' ', parts[0]).strip().replace(' ', '-').lower()
    ext = parts[1].replace('.', '').lower()
    return fname, ext



def read_directory(dirpath):
    if dirpath and isdir(dirpath):
        #print "Checking directory '%s'" % dirpath
        return [f for f in listdir(dirpath) if is_image(join(dirpath, f))]



def upload_dir():
    param = read_input()
    print "Parameters: %s" % str(param)
    dir_path = param['dir']
    pic_list = read_directory(dir_path)
    if pic_list is None:
        print "Invalid directory: '%s'" % dir_path
        return
    size = len(pic_list)
    if size == 0:
        print "No valid images found in '%s'" % dir_path
        return
    print "%d images found in '%s'" % (size, dir_path)

    folder_name = param['dest'] or basename(dir_path)
    print "Target folder: %s" % folder_name
    conf = get_config()
    if conf is None:
        print "Configuration failed!"
        return
    #print conf
    cloudinary.config(**conf)
    print "Cloudinary configured"

    # process images
    for fname in pic_list:
        fpath = join(dir_path, fname)
        new_name, type = get_name_type(fname)
        options = {
            'public_id': new_name,
            'folder': folder_name,
            'tags': folder_name
        }
        if param['max_w'] is not None:
            eager = {}
            eager['width'] = param['max_w']
            eager['height'] = param['max_h']
            eager['crop'] = 'scale'
            options['eager'] = eager

        print "Uploading %s with options %s" % (fpath, str(options))

        try:
            with open(fpath, 'rb') as fh:
                content = 'data:image/%s;base64,%s' % (type, fh.read().encode('base64'));
                result = cloudinary.uploader.upload(content, **options)
        except:
            print "Error uploading %s" % fpath
            continue

        result_str = repr(result)
        try:
            json_obj = json_loads(result_str)
            result_str = json_dumps(json_obj, indent=4)
        except:
            print "Could not convert result to JSON!"
        print result_str
        with open(DATA_FILE_NAME, 'a') as f:
            f.write(result_str + '\n')

upload_dir()

