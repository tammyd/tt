I suck at tracking the time I spend on things. Unfortunately, I have clients and managers
and projects who demand I do such a thing regardless. So I wrote a quick utility that allows
me to easily track what I'm working on via the command line, and provide some basic reports.

#Installation

```bash
$ git clone git://github.com/tammyd/tt.git
$ cd tt
$ python setup.py install
```

#Usage
##tt (Time Tracker) Help

* Start tracking a task   : tt start task description [-- time statement]
* Pause tracking:         : tt stop [-- time statement]
* Restart last task       : tt restart
* Show current task       : tt current
* Show a task summary     : tt summary [-- time statement]
* Show the task report    : tt report [-- time statement]
* Archive the current data: tt archive
* Show this help          : tt help

Additionally, several commands support "going back in time" to start or stop tasks,
or produce subset summaries/reports. The syntax for these commands is to end the
command with '-- some english time statement'. Type what you want in english and
there's a very good chance we'll figure it out.

Note that in the end all this application does is read and write the log file
stored at ~/.tt/log.txt. It's pretty straightforward, but if you go messing with
the file and this script breaks, don't blame me. Just delete or archive the file
and start again!

###Examples:

```bash
$ tt start Feature A
$ tt stop Feature A -- 10 minutes ago
$ tt restart
$ tt start Feature B -- 1 hour ago
$ tt start Feature A
$ tt summary -- 2 hours ago
```