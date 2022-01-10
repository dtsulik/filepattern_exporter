#!/bin/env python3

import re
import logging
import os
import glob
import zlib
import pprint
import numpy
from flask import Flask, request

stats = dict()

os.environ["WERKZEUG_RUN_MAIN"] = "true"

filepattern = os.getenv('FILEPATTERN', '*')
stringpattern = os.getenv('STRINGPATTERN', '(^.+ORA-\d+:.+)')
workdir = os.getenv('WORKDIR', '/app/files')
log_file = os.getenv('LOG_DEST', '/dev/stdout')

format = '[%(levelname)s][%(asctime)s]: %(message)s'
logging.basicConfig(format=format, filename=log_file, filemode='w', level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def slash():
    return f"""
<html>
<head><title>Log counter Exporter</title></head>
<body>
<h1>Log counter Exporter</h1>
<p><a href={request.base_url}metrics>Metrics</a></p>
</body>
</html>
"""

@app.route('/metrics')
def export_stats():
    find_files()
    reply = f""

    reply += write_metric_header("file_pattern_match", "gauge", "Number of times pattern was matched")
    for item in stats.items():
        # logging.debug(f"file_pattern_match{{match=\"{item[1]['string']}\"}} {item[1]['count']}")
        reply += write_metric("file_pattern_match", item)
        logging.debug(write_metric("file_pattern_match", item))

    return reply

def write_metric_header(name, type, desc):
    header = ''
    header += f"# HELP {name} {desc}\n"
    header += f"# TYPE {name} {type}\n"
    return header

def write_metric(name, metric_item):
    return f"{name}{{match=\"{metric_item[1]['string']}\", filename=\"{metric_item[1]['filename']}\"}} {metric_item[1]['count']}\n"

def find_files():
    logging.debug(f"changing to {workdir}")
    os.chdir(workdir)

    logging.debug(f"using pattern {filepattern}")
    for file in glob.glob(filepattern):
        read_log(file)

    logging.debug(f"stats {stats}")

# read file
def read_log(filename):
    logging.debug(f"reading files from {filename}")
    if not os.path.isfile(filename):
        return

    with open(filename) as f:
        lines = ''.join(f.readlines())

    m = re.findall(stringpattern, lines, re.M) # + re.S)
    values, counts = numpy.unique(m, return_counts=True)
    for value, count in zip(values, counts):
        item = dict()
        item["string"] = value
        item["count"] = count
        item["filename"] = filename
        stats[f"{zlib.crc32(value)}"] = item
        logging.debug(f"found {value} in {filename} {count} times")

if __name__ == '__main__':
    find_files()
