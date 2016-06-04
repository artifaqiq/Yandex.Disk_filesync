#!/usr/bin/python3.4
import sys, os, sys, logging, time

from client import Client
from filesys import FileSystemImage
from config import Configuration

APP_OPT_PATH = os.path.join(os.environ['HOME'], ".filesync")
CONFIG_PATH = os.path.join(APP_OPT_PATH, "config.ini")
LOG_PATH = os.path.join(APP_OPT_PATH, "synchronizer.log")
PID_PATH = os.path.join(APP_OPT_PATH, "synchronizer.pid")

from daemons.prefab import run

class Synchronizer(run.RunDaemon):
    def __init__(self, pidfile):
        super(type(self))
        self._pidfile = pidfile
        self.count_iteration = 0

    def run(self):
        os.system("notify-send \"daemon run!\"")
        time.sleep(10)
        while True:
            try:
                mes = True if len(sys.argv) >= 2 and sys.argv[
                                                         1] == "mes" else False
                config = Configuration(CONFIG_PATH)
                fs = FileSystemImage(config.get_option("daemon", "home-dir"),
                                     config.get_option("daemon", "app-dir"),
                                     Client(config))
                fs.exception_files.append(CONFIG_PATH)

                rm_exists = True if config.get_option("sync", "rm-exists")[
                                        0] == "T" else False
                save_orig = True if config.get_option("sync", "save-orig")[
                                        0] == "T" else False

                if self.count_iteration == 0:
                    fs.sync_disk_priority(rm_exists, save_orig, mes)
                else:
                    fs.sync_local_priority(rm_exists, save_orig, mes)

            except Exception as e:
                if mes: print(" == " + str(e))
            finally:
                try:
                    if mes: print(
                        " -- sleep " + config.get_option("daemon",
                                                         "sleep-time"))
                    time.sleep(
                        float(config.get_option("daemon", "sleep-time")))
                except UnboundLocalError as e:
                    sys.exit()
                except:
                    if mes: print(" == exit")
                    sys.exit()
                self.count_iteration += 1


if __name__ == '__main__':
    action = sys.argv[1]
    os.system("notify-send \"begin\"")

    logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
    synchronizer = Synchronizer(pidfile=PID_PATH)

    if action == "start":
        os.system("notify-send \"is start\"")
        synchronizer.start()

    elif action == "stop":
        synchronizer.stop()

    elif action == "restart":
        synchronizer.restart()
