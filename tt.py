#!/usr/bin/env python

from datetime import datetime
from sys import argv
from os import path, makedirs
from time import mktime
import parsedatetime as pdt

START       = 'start'
STOP        = 'stop'
SUMMARIZE   = 'summarize'
CURRENT     = 'current'
FILENAME    = '.tt/log.txt'
STOP_TASK   = '!!!!'


def parse_time(time_string):
    parsed = pdt.Calendar().parse(time_string)
    time = datetime.fromtimestamp(mktime(parsed[0]))
    if time_string.strip().endswith('ago'):
        time = datetime.now() - (time - datetime.now())

    return time


def parse_input(args, default_time=datetime.now()):
    combine = " ".join(args[1:])

    try:
        text, english_time = [x.strip() for x in combine.split('--')]
        time = parse_time(english_time)
    except ValueError:
        text = combine.strip()
        time = default_time

    try:
        command, task = [x.strip() for x in text.split(' ', 1)]

    except ValueError:
        command = text.strip()
        task = None

    return (command, task, time)

def get_handle(read_only=False):
    home = path.expanduser("~")
    filename = "%s/%s" % (home,FILENAME)
    dir = path.dirname(filename)
    if not path.exists(dir):
        makedirs(dir)

    if read_only:
        return open(filename, 'r')
    else:
        return open(filename, 'a')

def format_line(time, message):
    return "{timestamp} {msg}\n".format(timestamp=datetime.isoformat(time), msg=message)

def record(time, message):
    line = format_line(time, message)
    handle = get_handle()
    handle.write(line)
    handle.close()

def start(time, task):
    record(time, task)

def stop(time):
    record(time, STOP_TASK)

def print_summary(summary):
    pass

def summarize(since):

    CURRENT_TASK = '![current]!'

    handle = get_handle(True)

    lines = handle.read().splitlines()

    if since is not None:
        #add a fake line @ since time
        lines.append(format_line(since, CURRENT_TASK).rstrip())

    lines.sort()

    data = {}

    last_time = None
    last_task = None
    for line in lines:
        print line

        timestamp, task = line.split(" ", 1)
        if last_time is None:
            last_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

        current_time =  datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

        if task==CURRENT_TASK:
            task = last_task

        time_interval = current_time - last_time

        if since is not None and current_time < since:
            pass
        elif last_task is not None:
            if last_task in data:
                data[last_task] += time_interval
            else:
                data[last_task] = time_interval

        last_time = current_time
        last_task = task

    if last_task is not None:
        time_interval = datetime.now() - last_time
        if last_task in data:
            data[last_task] += time_interval
        else:
            data[last_task] = time_interval

    #del data[STOP_TASK]
    for task,elapsed in data.iteritems():
        if task==last_task:
            print "%s %s+" % (task, elapsed)
        else:
            print "%s %s" % (task, elapsed)

    handle.close()

def usage():
    print "Usage goes here"

def main():
    (command, task, time) = parse_input(argv, )

    if command==START:
        if task is not None:
            start(time, task)
        else:
            usage()

    elif command==STOP:
        if task is not None:
            start(time, task)
        else:
            stop(time)
    elif command==SUMMARIZE:
        #reparse the time
        (command, task, time) = parse_input(argv, default_time=None)
        summarize(time)
    else:
        print "Invalid command"
        exit()


if __name__ == "__main__":
    main()





