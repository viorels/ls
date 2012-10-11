#!/usr/bin/python2.7

import sys
import os
import glob
import argparse
import operator
import pwd, grp
import time

def list_all(patterns, item_filter, item_sort, expand_dirs):
    paths = sum([expand_pattern(pattern) for pattern in patterns], [])
    return [item_meta(path, item_filter, item_sort, expand_dirs) for path in paths]

def expand_pattern(pattern):
    return glob.glob(os.path.expanduser(pattern))

def list_dir(path, item_filter, item_sort, expand_dirs=False):
    content = ([item_meta(os.path.join(path, item),
                          item_filter, item_sort,
                          expand_dirs=expand_dirs)
                for item in ['.', '..'] + os.listdir(path)])
    return item_sort(item_filter(content))

def item_meta(item, item_filter, item_sort, expand_dirs=True):
    if item.endswith('/'):
        name = os.path.dirname(item)
    else:
        name = os.path.basename(item)
    meta = {'name': name}
    if os.path.isdir(item):
        meta['type'] = 'directory'
        meta['stat'] = os.stat(item)
        if expand_dirs:
            # list content of this folder but not the ones on next level
            try:
                meta['content'] = list_dir(item, item_filter, item_sort, expand_dirs=False)
            except OSError, e:
                meta['error'] = e
    elif os.path.islink(item):
        meta['type'] = 'link'
        meta['stat'] = os.lstat(item)
    elif os.path.isfile(item):
        meta['type'] = 'file'
        meta['stat'] = os.stat(item)
    else:
        meta['type'] = '' # mount/socket ?
        meta['stat'] = os.stat(item)
    return meta 

def display_simple(content):
    several_paths = len(content) > 1
    for path in content:
        if several_paths:
            if path.get('content'):
                print "\n" + get_title(path)
            else:
                print get_name(path)
        if path.get('error'):
            print >>sys.stderr, "%s\n" % path['error']
        else:
            for item in path.get('content', []):
                print get_name(item)

def display_long(content):
    several_paths = len(content) > 1
    for path in content:
        if several_paths:
            if path.get('content'):
                print "\n" + get_title(path)
            else:
                print get_name(path)
        if path.get('error'):
            print >>sys.stderr, "%s\n" % path['error']
        else:
            path_content = path.get('content', [])
            fmt, widths = format_long(path_content)
            for item in path_content:
                print fmt.format(**dict(item, **widths))

def format_long(content):
    item_type_letter = {'directory': 'd', 'link': 'l'} # TODO: get more info from stat.st_mode
    for item in content:
        stat = item['stat']
        item['mode'] = (item_type_letter.get(item['type'], '-') +
                        get_perms_text(stat.st_mode))
        item['nlink'] = stat.st_nlink
        item['user'] = pwd.getpwuid(stat.st_uid).pw_name
        item['group'] = grp.getgrgid(stat.st_gid).gr_name
        item['size'] = stat.st_size
        item['time'] = time.strftime('%b %d %Y %H:%M', time.localtime(stat.st_mtime))

    variable_width_fields = 'nlink user group size time'.split()
    widths = dict(("%s_width" % key, max(len(unicode(item[key])) for item in content))
                  for key in variable_width_fields)
    fmt = ("{mode} {nlink: >{nlink_width}} {user: >{user_width}} {group: >{group_width}} "
           "{size: >{size_width}} {time: >{time_width}} {name}")
    return fmt, widths
                                    
def get_perms_text(mode):
    octal = oct(mode)[-3:]
    perms = ''
    for octdigit in octal:
        intdigit = int(octdigit)
        perms += 'r' if intdigit & 4 else '-'
        perms += 'w' if intdigit & 2 else '-'
        perms += 'x' if intdigit & 1 else '-'
    return perms

def get_title(item):
    return get_name_with_symbol(item, {'directory': ':', 'link': '@'})

def get_name(item):
    return get_name_with_symbol(item, {'directory': '/', 'link': '@'})

def get_name_with_symbol(item, symbols):
    return item['name'] + symbols.get(item['type'], '')

def filter_none(items):
    return items

def filter_hidden(items):
    return [item for item in items if not item['name'].startswith('.')]

def sort_none(items, reverse):
    return items if not reverse else reversed(items)

def sort_alphanum(items, reverse):
    return sorted(items, key=operator.itemgetter('name'), reverse=reverse)

def sort_time(items, reverse):
    return sorted(items, key=lambda item: item['stat'].st_mtime, reverse=not reverse)

def sort_size(items, reverse):
    return sorted(items, key=lambda item: item['stat'].st_size, reverse=not reverse)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ls", description="List information about the FILEs "
                               "(the current directory by default).")
    parser.set_defaults(
        filter=filter_hidden,
        sort=sort_alphanum,
        display=display_simple)
    parser.add_argument(
        'pattern', metavar='path', nargs='*', default=[os.getcwd()],
        help='path(s) to list content of')
    parser.add_argument(
        '-a', '--all', dest='filter', action='store_const', const=filter_none,
        help='do not ignore entries starting with .')
    parser.add_argument(
        '-l', dest='display', action='store_const', const=display_long,
        help='use a long listing format')
    parser.add_argument(
        '-d', '--directory', dest='directory', action='store_const', const=True,
        default=False, help='list directory entries instead of contents, '
                            'and do not dereference symbolic links')
    parser.add_argument(
        '-U', dest='sort', action='store_const', const=sort_none,
        help='do not sort; list entries in directory order')
    parser.add_argument(
        '-S', dest='sort', action='store_const', const=sort_size,
        help='sort by file size')
    parser.add_argument(
        '-t', dest='sort', action='store_const', const=sort_time,
        help='sort by modification time, newest first')
    parser.add_argument(
        '-r', '--reverse', dest='reverse', action='store_const', const=True,
        default=False, help='reverse order while sorting')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sort = lambda items: args.sort(items, reverse=args.reverse)
    args.display(list_all(args.pattern,
                          item_filter=args.filter,
                          item_sort=sort,
                          expand_dirs=not args.directory))

