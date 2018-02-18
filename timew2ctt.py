#!/usr/bin/env python3
#############################################################################
# Timewarrior extension to export Timewarrior data to [ctt](https://www.nico.schottelius.org/software/ctt/)
# Timewarrior extensions docs: https://taskwarrior.org/docs/timewarrior/tutorial.html#extensions
#############################################################################

import sys
import json
import subprocess
from datetime import datetime
from pprint import pprint

TW_DATEFORMAT  = '%Y%m%dT%H%M%SZ'
CTT_DATEFORMAT = '%Y-%m-%d-%H%M'

def exit(status, *args):
    for msg in args:
        print(msg, file=sys.stderr)
    sys.exit(status)

def parse_input():
    header, body = sys.stdin.read().split('\n\n')
    config = {}
    for line in header.split('\n'):
        k, v = line.split(':', 1)
        config[k.strip()] = v.strip()
    return config, json.loads(body)

def has_project(entry, project):
    return project in entry["tags"] or any(t.startswith(project+'.') for t in entry["tags"])

def main():
    config, entries = parse_input()

    project = config["reports.ctt.project"]
    if not project:
        exit(1, "Set reports.ctt.project to the project you want to export:",
                "  $ timew config reports.ctt.project my_proj")
    print("Exporting for taskwarrior project: {}".format(project))

    ctt_project = config["reports.ctt.ctt_project"] or project
    print("Importing under ctt project {}".format(ctt_project))
    print("(set timewarrior config reports.ctt.ctt_project to change)")

    entries = filter(lambda e: has_project(e, project), entries)

    print()

    for entry in entries:
        if "end" not in entry: continue  # ignore incomplete entries
        start = datetime.strftime(datetime.strptime(entry['start'], TW_DATEFORMAT), CTT_DATEFORMAT)
        end   = datetime.strftime(datetime.strptime(entry['end'],   TW_DATEFORMAT), CTT_DATEFORMAT)
        descs = [ t for t in entry['tags'] if ' ' in t ]  # select multi-word things, so I don't export random tags and stuff
        desc  = '; '.join(descs)  # do something not entirely unreasonable with it in case there are more

        cmd = ['ctt', 'track', '--start', start, '--end', end, ctt_project]

        subprocess.run(cmd, input=desc.encode('utf-8'), check=True)
        print(" - {}".format(desc))

    print()
    print("Import completed.")

if __name__ == '__main__':
    main()

# def formatSeconds(seconds):
#   ''' Convert seconds: 3661
#       To formatted:    1:01:01
#   '''
#   hours   = int(seconds / 3600)
#   minutes = int(seconds % 3600) / 60
#   seconds =     seconds % 60
#   return '%4d:%02d:%02d' % (hours, minutes, seconds)



# # Extract the configuration settings.
# header = 1
# configuration = dict()
# body = ''
# for line in sys.stdin:
#   if header:
#     if line == '\n':
#       header = 0
#     else:
#       fields = line.strip().split(': ', 2)
#       if len(fields) == 2:
#         configuration[fields[0]] = fields[1]
#       else:
#         configuration[fields[0]] = ''
#   else:
#     body += line

# # Sum the second tracked by tag.
# totals = dict()
# j = json.loads(body)
# for object in j:
#   start = datetime.datetime.strptime(object['start'], DATEFORMAT)

#   if 'end' in object:
#     end = datetime.datetime.strptime(object['end'], DATEFORMAT)
#   else:
#     end = datetime.datetime.utcnow()

#   tracked = end - start

#   for tag in object['tags']:
#     if tag in totals:
#       totals[tag] += tracked
#     else:
#       totals[tag] = tracked

# # Determine largest tag width.
# max_width = 0
# for tag in totals:
#   if len(tag) > max_width:
#     max_width = len(tag)

# start = datetime.datetime.strptime(configuration['temp.report.start'], DATEFORMAT)
# end   = datetime.datetime.strptime(configuration['temp.report.end'],   DATEFORMAT)
# if max_width > 0:
#   # Compose report header.
#   print '\nTotal by Tag, for %s - %s\n' % (start, end)

#   # Compose table header.
#   if configuration['color'] == 'on':
#     print '[4m%-*s[0m [4m%10s[0m' % (max_width, 'Tag', 'Total')
#   else:
#     print '%-*s %10s' % (max_width, 'Tag', 'Total')
#     print '-' * max_width, '----------'

#   # Compose table rows.
#   grand_total = 0
#   for tag in sorted(totals):
#     formatted = formatSeconds(totals[tag].seconds)
#     grand_total += totals[tag].seconds
#     print '%-*s %10s' % (max_width, tag, formatted)

#   # Compose total.
#   if configuration['color'] == 'on':
#     print ' ' * max_width, '[4m          [0m'
#   else:
#     print ' ' * max_width, '----------'

#   print '%-*s %10s' % (max_width, 'Total', formatSeconds(grand_total))

# else:
#   print 'No data in the range %s - %s' % (start, end)

