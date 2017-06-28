import os
import csv
from   os.path import islink as islink
import re
import textwrap

#  Set the trees themselves, [ 'supporting unit', tree ]
module_trees = [ ['arc',   '/sw/arc/centos7/modulefiles'],
                 ['arcts', '/sw/arcts/centos7/modulefiles'],
                 ['coe',   '/sw/coe/centos7/modulefiles'],
                 ['lsa',   '/sw/lsa/centos7/modulefiles'],
                 ['med',   '/sw/med/centos7/modulefiles'],
                 ['sph',   '/sw/sph/centos7/modulefiles'],
                 ['arcts', '/sw/oncampus/arc/centos7/modulefiles'],
                 ['coe',   '/sw/oncampus/coe/centos7/modulefiles']
               ]

#  Regular expressions to pick out the files we need information from
module_re = re.compile('^[0-9a-zA-Z].*.lua$')
pkgInfo_re = re.compile('^\.pkgInfo.lua$')

#  Function to get information from a module version file
def process_module(root, file):
    root = root.replace(tree+'/', '')
    file = file.replace('.lua', '')
    info = root.split('/')
    info.append(file)
    module = info[0]
    version = info[1]
    if len(info) > 2:
        deps = []
        for i in range(2, len(info)-1, 2):
            deps.append(info[i] + '/' + info[i+1])
            deps.reverse()
        deps = ' '.join(deps)
        return module, version, deps
    else:
        return module, version, ' '

#  Function to get information from a module .pkgInfo.lua file
def process_pkgInfo(root, file):
    pkgInfo = {}
    # Regular expressions to extract fields from whatis() entries
    whatis_patterns = {
        'pkg_name'   : re.compile('whatis\("Name: (.*)\"\)'),
        'pkg_desc'   : re.compile('whatis\("Description: (.*)\"\)'),
        'pkg_url'    : re.compile('whatis\("Package website: (.*)\"\)'),
        'license'    : re.compile('whatis\("License information: (.*)\"\)'),
        'arc_ex'     : re.compile('whatis\("ARC examples: (.*)\"\)'),
        'categories' : re.compile('whatis\("Category: (.*)\"\)'),
        'docs'       : re.compile('whatis\("Package documentation: (.*)\"\)')
    }
    pkgInfoFile = '/'.join([root, file])
    with open(pkgInfoFile, "r") as module_file:
        raw = module_file.readlines()
        for line in raw:
            for pattern in whatis_patterns:
                match = ''
                match = whatis_patterns[pattern].match(line)
                try:
                    pkgInfo[pattern] = match.group(1)
                except:
                    pass
    return pkgInfo
    
#  Function to deal with default version files
def process_default(path):
    print "Found a default file\n%s/%s" % (path, file)

#  Create a dictionary for module information

modInfo = {}

#  Start processing for each of the module trees
for tree in module_trees:
    tree = tree[1]
    #  We really only use root, for dirname, and files for filenames
    for root, dirs, files in os.walk(tree):
        for file in files:
            if root.find('.git') > 0:
                continue
            module = root.replace(tree+'/', '')
            module = module.split('/')[0]
            if module not in modInfo:
                modInfo[module] = {'versions': [], 'pkgInfo': {}}
            if module_re.match(file):
                module, version, deps = process_module(root, file)
                if len(deps) > 1:
                    modInfo[module]['versions'].append(version+" with "+deps)
                else:
                    modInfo[module]['versions'].append(version)
            elif pkgInfo_re.match(file):
                if islink('/'.join([root,file])):
                    pass
                else:
                    modInfo[module]['pkgInfo'] = process_pkgInfo(root, file)
            elif file == "default":
                pass
            else:
                pass

#  Print out what we have for human consumpition
# for key in sorted(modInfo.keys(), key=str.lower):
#     print "==============================================="
#     print "\n", key
#     print "\t", "Versions: ", "; ".join(modInfo[key]['versions']).strip()
#     print "\t", "Description: ", modInfo[key]['pkgInfo']['pkg_desc']
#     if 'license' in modInfo[key]['pkgInfo']:
#         print "\t", "License: ", modInfo[key]['pkgInfo']['license']
#     if 'pkg_url' in modInfo[key]['pkgInfo']:
#         print "\t", "Package web site: ", modInfo[key]['pkgInfo']['pkg_url']
#     if 'categories' in modInfo[key]['pkgInfo']:
#         print "\t", "Categories: ", modInfo[key]['pkgInfo']['categories']
# print "==============================================="

def item_label(label):
    return '{:<14}'.format(label)

def wrapped_item(item):
    return textwrap.fill(item, width=76,
                         initial_indent = '',
                         subsequent_indent = 14*' ')

def print_catalog():
    #  Print out what we have for the catalog page
    for key in sorted(modInfo.keys(), key=str.lower):
        print 2*"\n", key
        print 78*"="
        print wrapped_item(item_label("Description:") + modInfo[key]['pkgInfo']['pkg_desc'])
        print wrapped_item(item_label("Versions:") + "; ".join((modInfo[key]['versions'])))
        if 'license' in modInfo[key]['pkgInfo']:
            print wrapped_item(item_label("License:") + modInfo[key]['pkgInfo']['license'])
        if 'categories' in modInfo[key]['pkgInfo']:
            print wrapped_item(item_label("Categories:") + modInfo[key]['pkgInfo']['categories'])
        print 78*"="

def print_csv():
    with open('/afs/umich.edu/group/f/flux/Public/html/modules/sw_catalog.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["Module Name", "Description", "Versions", "License Information", "Categories"])
        for key in sorted(modInfo.keys(), key=str.lower):
            module_info = []
            module_info.append(key)
            module_info.append(modInfo[key]['pkgInfo']['pkg_desc'])
            module_info.append("; ".join((modInfo[key]['versions'])))
            if 'license' in modInfo[key]['pkgInfo']:
                module_info.append(modInfo[key]['pkgInfo']['license'])
            if 'categories' in modInfo[key]['pkgInfo']:
                module_info.append(modInfo[key]['pkgInfo']['categories'])
            csv_writer.writerow(module_info)

def print_all():
    #  Print out what we have for human consumption
    for key in sorted(modInfo.keys(), key=str.lower):
        print "\n", "Key: ", key,
        print "\t", "Versions: ", key+"/".join(modInfo[key]['versions'])
        for mod_info in modInfo[key]['pkgInfo'].keys():
            print "\t", mod_info, ": ", modInfo[key]['pkgInfo'][mod_info]

print_catalog()
print_csv()
