#!/usr/bin/env python

from datetime import datetime
from sys import argv
from os import path, makedirs
from time import mktime
import parsedatetime as pdt
from prettytable import PrettyTable
from os.path import  join, exists
from shutil import move


FILENAME    = '.tt/log.txt'
STOP_TASK   = 'Paused'

def parse_time(time_string):
    parsed = pdt.Calendar().parse(time_string)
    time = datetime.fromtimestamp(mktime(parsed[0]))

    #sometimes this lib parses "ago" and sometimes it doesn't
    if time > datetime.now():
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

def get_full_filename():
    home = path.expanduser("~")
    return join(home, FILENAME)

def log_exists():
    src = get_full_filename()
    return exists(src)

def get_handle(read_only=False):
    filename = get_full_filename()
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

def parse_summary_elapsed(elapsed):
    seconds = elapsed.seconds
    hours = int(seconds / 3600)
    seconds -= (hours * 3600)
    minutes = round(seconds/60)
    seconds -= (minutes * 60)

    return hours, minutes, seconds

def display_elapsed(elapsed):
    h,m,s = parse_summary_elapsed(elapsed)
    return display_hms(h,m,s)

def display_hms(hour, min, seconds):
    return "%02d:%02d:%02d" % (hour, min, seconds)

def print_summary(summary, last_task, since):
    #todo - sort output

    table = PrettyTable(["Task", "Elapsed", "Current"])
    table.align["Task"] = 'l'
    table.header = True

    for task,elapsed in summary.iteritems():
        current = 'X' if task==last_task else "-"
        row = [task, display_elapsed(elapsed), current]
        table.add_row(row)

    header_text = "Task summary since {:%b %d %I:%M %p}".format(since)
    heading = make_title_table(table,header_text)

    print heading
    print table.get_string(sortby="Elapsed")

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

def make_title_table(body_table, title):
    body_table.__str__() #force width calc
    table = PrettyTable()
    max_length = len(body_table._hrule)
    pad_left = int((max_length - 2 - len(title))/2)
    pad_right = max_length - 2 - len(title) - pad_left
    table.left_padding_width = max(1,pad_left)
    table.right_padding_width = max(1,pad_right)
    table.add_row([title])
    table._set_max_width(max_length-4)
    table.header = False

    return table


def print_report(records, since):

    table = PrettyTable(["Task", "Elapsed", "Start", "End"])
    table.align["Task"] = 'l'
    table.header = True

    for i,record in enumerate(records):
        try:
            x = records[i+1]
            row = [record['task'],
                   display_elapsed(record['elapsed']),
                   datetime.strftime(record['start'], '%b %d, %I:%M %p'),
                   datetime.strftime( record['end'],"%b %d, %I:%M %p")
            ]
        except:
            #last iteration
            row = [record['task'],
                   "--",
                   datetime.strftime(record['start'], '%b %d, %I:%M %p'),
                   "--"
            ]


        table.add_row(row)

    header_text = "Tasks since {:%b %d %I:%M %p}".format(since)
    heading = make_title_table(table,header_text)

    print heading
    print table


def report(since):
    report, first_time = get_report(since)
    print_report(report, first_time)

def get_report(since):
    CURRENT_TASK = '![current]!'

    lines = get_sorted_lines()

    if since is not None:
        #add a fake line @ since time
        lines.append(format_line(since, CURRENT_TASK).rstrip())
        lines.sort()

    last_time = None
    last_task = None
    first_time = since
    records = []
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
        elif len(records) > 0 and task==last_task:
            #just update the last record
            records[-1]['end'] = current_time
            records[-1]['elapsed']+=time_interval
        elif last_task is not None:
            record = {'task':last_task, 'start':last_time, 'end':current_time, 'elapsed':time_interval}
            records.append(record)

        last_time = current_time
        last_task = task

    if len(records) > 0 and task==records[-1]['task']:
        records[-1]['end'] = None
        records[-1]['elapsed']=None
    elif last_task is not None:
        record = {'task':last_task, 'start':last_time, 'end':None, 'elapsed':None}
        records.append(record)

    return records, first_time

def get_nth_entry_from_end(n, since):
    report, first_time = get_report(since)
    return report[-1*n]

def restart_last():

    paused = get_nth_entry_from_end(1, None)
    if paused['task'] != STOP_TASK:
        current(None) #already working on a task
        return

    n = 2
    while(True):
        try:
            event = get_nth_entry_from_end(n, None)
            if event['task'] != STOP_TASK:
                last_event = get_nth_entry_from_end(n, None)
                start(datetime.now(), last_event['task'])
                print "Restarted %s" % last_event['task']
                return

        except:
            print "Unable to find a task to restart"
            return

        n+=1

def current(since):
    event = get_nth_entry_from_end(1, since)
    time_interval = datetime.now() -event['start']
    hours, minutes, sec = parse_summary_elapsed(time_interval)

    print "You've been working on '%s' for %s." % (event['task'], display_hms(hours, minutes, sec))

def archive():
    print "Are you sure? [Y|N]"
    confirm = raw_input('--> ')

    if confirm.upper() not in ['Y', 'YES']:
        print "Ok - nothing changed"
        return

    src = get_full_filename()
    dir = join(path.dirname(src), 'archive/')
    if not path.exists(dir):
        makedirs(dir)


    new_filename = "log.{:%Y%m%dT%H%M%S}.txt".format(datetime.now())
    dst = join(dir, new_filename)
    move(src, dst)

    print "Moved %s to %s" % (src,dst)



def usage():
    usage = '''
tt (Time Tracker) Help
-----------------------------------------------------------------------------------

Start tracking a task   : {0} start task description [-- time statement]
Pause tracking:         : {0} stop [-- time statement]
Restart last task       : {0} restart
Show current task       : {0} current
Show a task summary     : {0} summary [-- time statement]
Show the task report    : {0} report [-- time statement]
Archive the current data: {0} archive
Show this help          : {0} help

Additionally, several commands support "going back in time" to start or stop tasks,
or produce subset summaries/reports. The syntax for these commands is to end the
command with '-- some english time statement'. Type what you want in english and
there's a very good chance we'll figure it out.

Note that in the end all this application does is read and write the log file
stored at ~/.tt/log.txt. It's pretty straightforward, but if you go messing with
the file and this script breaks, don't blame me. Just delete or archive the file
and start again!

Examples:

$ {0} start Feature A
$ {0} stop Feature A -- 10 minutes ago
$ {0} restart
$ {0} start Feature B -- 1 hour ago
$ {0} start Feature A
$ {0} summary -- 2 hours ago

'''.format(argv[0])

    print usage


def check_log():
    if not log_exists():
        print "No entries yet!"
        return False

    return True


def main():
    START       = 'start'
    STOP        = 'stop'
    SUMMARIZE   = 'summary'
    CURRENT     = 'current'
    REPORT      = 'report'
    ARCHIVE     = 'archive'
    RESTART     = 'restart'
    HELP        = 'help'

    (command, task, time) = parse_input(argv)

    if command==HELP:
        usage()
    elif command==START:
        if task is not None:
            start(time, task)
        else:
            #TODO: restart last task before paused
            restart_last()
    elif command==RESTART:
        restart_last()
    elif command==STOP:
        if not check_log():
            return

        if task is not None:
            start(time, task)
        else:
            stop(time)
    elif command==SUMMARIZE:
        if not check_log():
            return
        #reparse the time
        (command, task, time) = parse_input(argv, default_time=None)
        summarize(time)
    elif command==CURRENT:
        if not check_log():
            return
        (command, task, time) = parse_input(argv, default_time=None)
        current(time)
    elif command==REPORT:
        if not check_log():
            return
        (command, task, time) = parse_input(argv, default_time=None)
        report(time)
    elif command==ARCHIVE:
        if not check_log():
            return
        archive()
    else:
        usage()




if __name__ == "__main__":
    main()





