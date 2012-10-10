#!/usr/bin/python2.7

import sys
import os
import glob
import argparse
import operator

def list_all(patterns, item_filter, item_sort, expand_dirs):
    paths = sum([expand_pattern(pattern) for pattern in patterns], [])
    return [item_meta(path, item_filter, item_sort, expand_dirs) for path in paths]

def expand_pattern(pattern):
    return glob.glob(pattern) # TODO expand ~ and vars with os.path.expanduser()/expandvars()

def list_dir(path, item_filter, item_sort, expand_dirs=False):
    content = ([item_meta(os.path.join(path, item),
                          item_filter, item_sort,
                          expand_dirs=expand_dirs)
                for item in os.listdir(path)])
    return item_sort(item_filter(content))

def item_meta(item, item_filter, item_sort, expand_dirs=True):
    meta = {'name': os.path.basename(os.path.abspath(item))}
    if os.path.isfile(item):
        meta['type'] = 'file'
    elif os.path.isdir(item):
        meta['type'] = 'directory'
        if expand_dirs:
            # list content of this folder but not the ones on next level
            try:
                meta['content'] = list_dir(item, item_filter, item_sort)
            except OSError, e:
                meta['error'] = e
    elif os.path.islink(item):
        meta['type'] = 'link'
    else:
        meta['type'] = '' # mount/socket ?
    return meta 

def display_simple(content):
    show_title = len(content) > 1
    for path in content:
        if show_title and path.get('content'):
            print "\n" + get_title(path)
        else:
            print get_name_and_symbol(path)
        if path.get('error'):
            print >>sys.stderr, "%s\n" % path['error']
        else:
            for item in path.get('content', []):
                print get_name_and_symbol(item)

def display_long(content):
    pass

def get_title(item):
    item_symbol = {'directory': ':', 'link': '@'} 
    return item['name'] + item_symbol.get(item['type'], '')

def get_name_and_symbol(item):
    type_symbol = {'directory': '/', 'link': '@'}
    return item['name'] + type_symbol.get(item['type'], '')

def filter_none(items):
    return items

def filter_hidden(items):
    return [item for item in items if not item['name'].startswith('.')]

def sort_alphanum(items):
    return sorted(items, key=operator.itemgetter('name'))

def sort_mtime(items):
    pass

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ls", description="List information about the FILEs "
                               "(the current directory by default).")
    parser.set_defaults(
        filter=filter_hidden,
        sort=sort_alphanum)
    parser.add_argument(
        'pattern', metavar='path', nargs='*', default=[os.getcwd()],
        help='path(s) to list content of')
    parser.add_argument(
        '-a', '--all', dest='filter', action='store_const', const=filter_none,
        help='do not ignore entries starting with .')
    parser.add_argument(
        '-r', '--reverse', dest='reverse', action='store_const', const=True,
        default=False, help='reverse order while sorting')
    parser.add_argument(
        '-d', '--directory', dest='directory', action='store_const', const=True,
        default=False, help='list directory entries instead of contents, '
                            'and do not dereference symbolic links')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sort = args.sort if not args.reverse else lambda items: reversed(args.sort(items))
    display_simple(list_all(args.pattern,
                            item_filter=args.filter,
                            item_sort=sort,
                            expand_dirs=not args.directory))

