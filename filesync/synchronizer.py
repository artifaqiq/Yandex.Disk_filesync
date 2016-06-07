#!/usr/bin/python3.4
import os, sys, logging, time

from client import Client
from filesys import FileSystemImage
from config import Configuration
from daemon import runner
import codecs

APP_OPT_PATH = os.path.join(os.environ['HOME'], ".filesync")
CONFIG_PATH = os.path.join(APP_OPT_PATH, "config.ini")
DAEMON_LOG_PATH = os.path.join(APP_OPT_PATH, "daemon.log")
DAEMON_PID_PATH = os.path.join(APP_OPT_PATH, "daemon.pid")
LOG_PATH = os.path.join(APP_OPT_PATH, "sync.log")

NO_NETWORK_EXCEPTION_SLEEP = 10

class Synchronizer(object):
    def __init__(self):
        self.stdin_path = '/dev/null' if not "win" in sys.platform else "Nul"
        self.stdout_path = DAEMON_LOG_PATH
        self.stderr_path = DAEMON_LOG_PATH
        self.pidfile_path = DAEMON_PID_PATH
        self.pidfile_timeout = 5

        self.encoder = codecs.getencoder('utf-8')
        self.first_run = True

    def run(self):
        while True:
            try:
                config = Configuration(CONFIG_PATH)
                client = Client(config)
                fs = FileSystemImage(config.get_option("daemon", "home-dir"),
                                     config.get_option("daemon", "app-dir"),
                                     client)

                rm_exists = True if config.get_option("sync",
                                                      "rm-exists").upper() \
                                    == "TRUE" else False
                save_orig = True if config.get_option("sync",
                                                      "save-orig").upper() \
                                    == "TRUE" else False
                sleep_time = int(
                    float(config.get_option("daemon", "sleep-time")))

                if self.first_run == True:
                    fs.sync_disk_priority(rm_exists, save_orig)
                    self.first_run = False
                else:
                    fs.sync_local_priority(rm_exists, save_orig)
            except Exception as e:
                print(str(e))
                time.sleep(NO_NETWORK_EXCEPTION_SLEEP)
            finally:
                time.sleep(sleep_time)


class DaeomonLauncher(object):
    def start(self):
        if len(sys.argv) >= 2:
            sys.argv[1] = "start"
        elif len(sys.argv) == 0:
            sys.argv.append("")
            sys.argv.append("start")
        else:
            sys.argv.append("start")
        self._do_action()

    def stop(self):
        if len(sys.argv) >= 2:
            sys.argv[1] = "stop"
        elif len(sys.argv) == 0:
            sys.argv.append("")
            sys.argv.append("stop")
        else:
            sys.argv.append("stop")
        self._do_action()

    def restart(self):
        if len(sys.argv) >= 2:
            sys.argv[1] = "restart"
        elif len(sys.argv) == 0:
            sys.argv.append("")
            sys.argv.append("restart")
        else:
            sys.argv.append("restart")

        self._do_action()

    def _do_action(self):
        logging.basicConfig(filename=LOG_PATH,
                            format=u'[%(asctime)s] %(message)s',
                            level=logging.ERROR)

        fhdl = logging.FileHandler(LOG_PATH)
        logging.getLogger().addHandler(fhdl)

        sync = Synchronizer()
        daemon_runner = runner.DaemonRunner(sync)
        daemon_runner.daemon_context.files_preserve = [fhdl.stream]
        daemon_runner.do_action()
