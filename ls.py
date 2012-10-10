#!/usr/bin/python2.7

import sys
import os
import glob
import argparse

def list_all(patterns, item_filter, item_sort):
    paths = sum([expand_pattern(pattern) for pattern in patterns], [])
    return [item_meta(path) for path in paths]

def expand_pattern(pattern):
    return glob.glob(pattern) # TODO expand ~ and vars with os.path.expanduser()/expandvars()

def list_dir(path, expand_dirs=False):
    return [item_meta(os.path.join(path, item), expand_dirs)
            for item in os.listdir(path)]

def item_meta(item, expand_dirs=True):
    meta = {'name': os.path.basename(os.path.abspath(item))}
    if os.path.isfile(item):
        meta['type'] = 'file'
    elif os.path.isdir(item):
        meta['type'] = 'directory'
        if expand_dirs:
            # list content of this folder but not the ones on next level
            try:
                meta['content'] = list_dir(item)
            except OSError, e:
                meta['error'] = e
    elif os.path.islink(item):
        meta['type'] = 'link'
    else:
        meta['type'] = '' # mount/socket ?
    return meta 

def display_simple(content):
    file_type_symbol = {'directory': '/', 'link': '@'}
    show_title = len(content) > 1
    for path in content:
        if show_title:
            print get_title(path)
        if path.get('error'):
            print >>sys.stderr, "%s\n" % path['error']
        else:
            for item in path.get('content', []):
                print item['name'] + file_type_symbol.get(item['type'], '')
        print ""

def display_long(content):
    pass

def get_title(item):
    item_symbol = {'directory': ':', 'link': '@'} 
    return item['name'] + item_symbol.get(item['type'], '')

def filter_none(items):
    return items

def filter_hidden(items):
    return [item for item in items if not item['name'].startswith('.')]

def sort_alphanum(items):
    pass

def sort_mtime(items):
    pass

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ls", description="List information about the FILEs "
                               "(the current directory by default).")
    parser.add_argument(
        'pattern', metavar='path', nargs='*', default=[os.getcwd()],
        help='path(s) to list content of')
    parser.add_argument(
        '-a', '--all', dest='filter', action='store_const', const=filter_none,
        default=filter_hidden, help='do not ignore entries starting with .')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
#    print args.accumulate(args.paths)
    display_simple(list_all(args.pattern, item_filter=args.filter, item_sort=None))

