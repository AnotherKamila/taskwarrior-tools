#!/usr/bin/env python3
#############################################################################
# Timewarrior extension to print the currently tracked task in a more compact, one-line format
# Timewarrior extensions docs: https://taskwarrior.org/docs/timewarrior/tutorial.html#extensions
# Link to ~/.timewarrior/extensions/current.py
#############################################################################

import sys
import json
import subprocess
from datetime import datetime
from pprint import pprint

TW_DATEFORMAT  = '%Y%m%dT%H%M%SZ'

def parse_input():
    header, body = sys.stdin.read().split('\n\n')
    config = {}
    for line in header.split('\n'):
        k, v = line.split(':', 1)
        config[k.strip()] = v.strip()
    return config, json.loads(body)

def description(entry):
    """Tries to guess what is a good task description"""
    descs = [ t for t in entry['tags'] if ' ' in t ]  # select multi-word things, so I don't export random tags and stuff
    if not descs: descs = entry['tags']  # fallback
    return '; '.join(descs)  # do something not entirely unreasonable with it in case there are more

def format_timedelta(d):
    m, s = divmod(d.seconds, 60)
    return '{}:{:02}'.format(m, s)

def main():
    config, entries = parse_input()

    try:
        current_entry = [ e for e in entries if "end" not in e ][0]
    except IndexError:
        current_entry = None

    if not current_entry:
        return None  # no output

    t = datetime.now() - datetime.strptime(current_entry['start'], TW_DATEFORMAT)

    print('{} [{}]'.format(description(current_entry), format_timedelta(t)), end='')


if __name__ == '__main__':
    main()

