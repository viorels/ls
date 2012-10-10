#!/usr/bin/python2.7

import argparse
import os
import glob

def list_all(patterns, item_filter, item_sort):
    paths = sum([expand_pattern(pattern) for pattern in patterns], [])
    return [list_path(path) for path in paths]

def expand_pattern(pattern):
    return glob.glob(pattern) # TODO expand ~ and vars with os.path.expanduser()/expandvars()

def list_path(path, expand_dirs=True):
    return item_meta(path)

def list_dir(path, expand_dirs=True):
    return [item_meta(os.path.join(path, item), list=expand_dirs) 
            for item in os.listdir(path)]

def item_meta(item, list=True):
    meta = {'name': os.path.basename(item)}
    if os.path.isfile(item):
        meta['type'] = 'file'
    elif os.path.isdir(item):
        meta['type'] = 'directory'
        if list:
            meta['content'] = list_dir(item, expand_dirs=False)
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
        for item in path.get('content', []):
            print item['name'] + file_type_symbol.get(item['type'], '')

def get_title(item):
    item_symbol = {'directory': ':', 'link': '@'} 
    return item['name'] + item_symbol.get(item['type'], '')

def filter_none(items):
    return items

def filter_hidden(items):
    return [item for item in items if not item['name'].startswith('.')]

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

