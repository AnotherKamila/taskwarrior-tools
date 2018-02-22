#!/usr/bin/env python3
#############################################################################
# Timewarrior extension to export Timewarrior data to [ctt](https://www.nico.schottelius.org/software/ctt/)
# Timewarrior extensions docs: https://taskwarrior.org/docs/timewarrior/tutorial.html#extensions
# Link to ~/.timewarrior/extensions/ctt.py
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
