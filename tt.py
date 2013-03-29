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
STOP_TASK   = 'Paused'


def parse_time(time_string):
    parsed = pdt.Calendar().parse(time_string)
    time = datetime.fromtimestamp(mktime(parsed[0]))

    #sometimes this lib parses "ago" and sometimes it doesn't
    if time_string.strip().endswith('ago') and time > datetime.now():
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

def print_header(msg, width=72):
    print "*" * width
    print_boxed_line(msg, width)
    print "*" * width

def print_footer(width=72):
    print "*" * width

def print_boxed_line(msg, width=72, align='center'):
    ftn = getattr(msg, align)
    print "* %s *" % ftn(width-4)

def print_summary(summary, last_task, since):


    #todo - sort output

    lines = {}
    for task,elapsed in summary.iteritems():
        s = elapsed.seconds
        hours = int(s / 3600)
        s -= (hours * 3600)
        minutes = round(s/60)

        if task==last_task:
            lines[task] = "%02d:%02d+" % (hours, minutes)
        else:
            lines[task] = "%02d:%02d" % (hours, minutes)

    task_width = max([len(x) for x in lines.keys()])
    time_width = max([len(x) for x in lines.values()])

    header_msg = "Task Summary since {:%Y-%m-%d %H:%M:%S}".format(since)
    width = max(task_width + time_width + 6, len(header_msg) + 8)

    print_header("Task Summary since {:%Y-%m-%d %H:%M:%S}".format(since), width=width)
    for (task, elapsed) in lines.iteritems():
        line = ("%s" % task).ljust(task_width) + ": %s" % elapsed
        print_boxed_line(line, align='ljust',width=width)

    print_footer(width=width)


def parse_timestamp(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

def get_sorted_lines():
    handle = get_handle(True)
    lines = handle.read().splitlines()
    lines.sort()
    handle.close()
    return lines

def summarize(since):
    summary, last_task, first_time = get_summary(since)
    print_summary(summary, last_task, first_time)

def get_summary(since):

    CURRENT_TASK = '![current]!'

    lines = get_sorted_lines()

    if since is not None:
        #add a fake line @ since time
        lines.append(format_line(since, CURRENT_TASK).rstrip())
        lines.sort()

    data = {}

    last_time = None
    last_task = None
    first_time = since
    for line in lines:
        timestamp, task = line.split(" ", 1)
        if last_time is None:
            last_time = parse_timestamp(timestamp)

        current_time =  parse_timestamp(timestamp)

        if first_time is None:
            first_time = current_time

        if task==CURRENT_TASK:
            task = last_task

        time_interval = current_time - last_time

        if since is not None and current_time <= since:
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

    return (data, last_task, first_time)


def current():
    pass

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
    elif command==CURRENT:
        current(time)
    else:
        print "Invalid command"
        exit()


if __name__ == "__main__":
    main()





