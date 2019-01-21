import csv
import sqlite3 as db
from datetime import datetime
import os
import hashlib
import re

COMMENTS_MAX_COUNT = 44
ATTACH_MAX_COUNT = 30
ATTACH_DESCR_COUNT = 11


def csv_writer(data, path):
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


def check_none(s):
    if s is None:
        return ''
    else:
        return s


def make_comments(ticket):
    # "01/01/2012 10:10;Admin; This comment works"
    cur.execute(
        "SELECT time, author, newvalue FROM ticket_change where field = 'comment' and ticket = ? order by time;",
        (ticket,))
    res = []
    for i in range(COMMENTS_MAX_COUNT):
        r = cur.fetchone()
        if r is None or r['newvalue'] == '':
            t = ''
        else:
            t = get_date(r['time']) + ';' + r['author'] + ';' + r['newvalue']
        res.append(t)
    return res


_extension_re = re.compile(r'\.[A-Za-z0-9]+\Z')


def _get_hashed_filename(filename):
    hash = hashlib.sha1(filename.encode('utf-8')).hexdigest()
    match = _extension_re.search(filename)
    return hash + match.group(0) if match else hash


'''def _get_hashed_filename(filename):
    parts = os.path.splitext(filename)
    hash = hashlib.sha1(filename.encode('utf-8')).hexdigest()
    return hash + parts[1]'''


def _get_path(parent_id, filename):
    parent_realm = 'file://ticket/'
    hash = hashlib.sha1(parent_id.encode('utf-8')).hexdigest()
    path = '/'.join([hash[0:3], hash, _get_hashed_filename(filename)])
    path = parent_realm + path
    return path # os.path.normpath()


def make_attach(ticket):
    # "01/01/2012 13:10;Admin;image.png;file://image-name.png"
    cur.execute(
        "SELECT id, filename, time, description, author FROM attachment where type = 'ticket' and id = ? order by time;",
        (ticket,))
    res = []
    for i in range(ATTACH_MAX_COUNT):
        r = cur.fetchone()
        if r is None or r['filename'] == '':
            t = ''
        else:
            t = get_date(r['time']) + ';' + r['author'] + ';' + r['filename'] + ';' + _get_path(r['id'], r['filename'])
        res.append(t)
    return res


def make_attach_descr(ticket):
    cur.execute(
        '''SELECT type, id, filename, time, description, author 
           FROM attachment where description != '' and type = 'ticket' and id = ? order by time;''',
        (ticket,))
    res = []
    for i in range(ATTACH_DESCR_COUNT):
        r = cur.fetchone()
        if r is None:
            t = ''
        else:
            val = 'Вложение ' + r['filename'] + ' добавлено ​​с описанием: ' + r['description']
            t = get_date(r['time']) + ';' + r['author'] + ';' + val
        res.append(t)
    return res


def prepare_title():
    res = ['id', 'type', 'time', 'changetime', 'component', 'priority', 'owner', 'reporter', 'milestone', 'status', 'resolution', 'summary', 'description', 'labels']
    res.extend(['comment'] * COMMENTS_MAX_COUNT)
    res.extend(['attachment'] * ATTACH_MAX_COUNT)
    res.extend(['comment'] * ATTACH_DESCR_COUNT)
    return res


def prepare_row(row):
    lst = []
    lst.append(str(row['id']))
    lst.append(str(row['type']))
    lst.append(get_date(row['time']))
    lst.append(get_date(row['changetime']))
    lst.append(str(row['priority']))
    lst.append(str(row['component']))
    lst.append(str(row['owner']))
    lst.append(str(row['reporter']))
    lst.append(str(row['milestone']))
    lst.append(str(row['status']))
    lst.append(check_none(row['resolution']))
    lst.append(row['summary'])
    lst.append(check_none(row['description']))
    lst.append(str(row['keywords']))
    lst.extend(make_comments(row['id']))
    lst.extend(make_attach(row['id']))
    lst.extend(make_attach_descr(row['id']))

    return lst


def get_date(val):
    d = float(val) / 1000000
    res = datetime.fromtimestamp(d).strftime('%Y/%m/%d %H:%M:%S')
    return res


conn = db.connect('c:/trac.db')
conn.row_factory = db.Row
cur = conn.cursor()

f = open('c:/text.csv', 'w', encoding='utf-8-sig')
writer = csv.writer(f, delimiter=',')

t = prepare_title()
writer.writerow(t)

cur.execute("select id, type, time, changetime, component, priority, owner, reporter, milestone, status, resolution, summary, description, keywords from ticket")
for row in cur.fetchall():
        lst1 = prepare_row(row)
        writer.writerow(lst1)
        #print(lst1)

f.close()
