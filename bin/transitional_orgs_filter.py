#!/usr/bin/env python

"""
throw away all parts of an organization that we don't want to propagate
to another ckan instance.

Usage:

ckanapi dump organizations --all | ./transitional_orgs_filter.py > orgs.jsonl
"""

import sys
import json

EXTRAS = set([
    'department_number',
    'shortform',
    'shortform_fr',
    'ati_email',
    ])

for l in sys.stdin.readlines():
    o = json.loads(l)
    print json.dumps({
        "title": o["title"],
        "id": o["id"],
        "extras": [{"value": e["value"], "key": e["key"]}
            for e in o["extras"] if e["key"] in EXTRAS],
        "name": o["name"],
        })

