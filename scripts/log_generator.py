#!/usr/bin/python
import time
import datetime
import pytz
import numpy
import random
import gzip
import zipfile
import sys
import argparse
import math
from faker import Faker
from random import randrange
from tzlocal import get_localzone
local = get_localzone()

parser = argparse.ArgumentParser(
    __file__, description="Fake Apache Log Generator")
parser.add_argument(
    "--output",
    "-o",
    dest='output_type',
    help="Write to a Log file, a gzip file or to STDOUT",
    choices=['LOG', 'GZ', 'CONSOLE'])
parser.add_argument(
    "--log-format",
    "-l",
    dest='log_format',
    help="Log format, Common or Extended Log Format ",
    choices=['CLF', 'ELF'],
    default="ELF")
parser.add_argument(
    "--num",
    "-n",
    dest='num_lines',
    help="Number of lines to generate (0 for infinite)",
    type=int,
    default=1)
parser.add_argument(
    "--prefix",
    "-p",
    dest='file_prefix',
    help="Prefix the output file name",
    type=str)
parser.add_argument(
    "--sleep",
    "-s",
    help="Sleep this long between lines (in seconds)",
    default=0.0,
    type=float)

args = parser.parse_args()

log_lines = args.num_lines
file_prefix = args.file_prefix
output_type = args.output_type
log_format = args.log_format

if not log_lines:
    log_lines = math.inf

faker = Faker()

timestr = time.strftime("%Y%m%d-%H%M%S")
otime = datetime.datetime.now()

outFileName = 'access_log_' + timestr + \
    '.log' if not file_prefix else file_prefix + '_access_log_' + timestr + '.log'

if output_type == 'LOG':
    f = open(outFileName, 'w')
if output_type == 'GZ':
    f = gzip.open(outFileName + '.gz', 'w')
else:
    f = sys.stdout

RESPONSES = ["200", "404", "500", "301"]

VERBS = ["GET", "POST", "DELETE", "PUT"]

RESOURCES = [
    "/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list",
    "/app/main/posts", "/posts/posts/explore", "/apps/cart.jsp?appID="
]

BROWSERS = [
    faker.firefox, faker.chrome, faker.safari, faker.internet_explorer,
    faker.opera
]

flag = True
while log_lines:
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    else:
        increment = datetime.timedelta(seconds=random.randint(30, 300))
    otime += increment

    ip = faker.ipv4()
    dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
    tz = datetime.datetime.now(local).strftime('%z')
    vrb = numpy.random.choice(VERBS, p=[0.6, 0.1, 0.1, 0.2])

    uri = random.choice(RESOURCES)
    if uri.find("apps") > 0:
        uri += str(random.randint(1000, 10000))

    resp = numpy.random.choice(RESPONSES, p=[0.9, 0.04, 0.02, 0.04])
    byt = int(random.gauss(5000, 50))
    referer = faker.uri()
    useragent = numpy.random.choice(BROWSERS, p=[0.5, 0.3, 0.1, 0.05, 0.05])()
    if log_format == "CLF":
        f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip, dt, tz, vrb,
                                                             uri, resp, byt))
    elif log_format == "ELF":
        f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' %
                (ip, dt, tz, vrb, uri, resp, byt, referer, useragent))
    f.flush()

    log_lines = log_lines - 1
    if args.sleep:
        time.sleep(args.sleep)
