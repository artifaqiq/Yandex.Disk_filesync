#!/usr/bin/python3
from src.Configuration import Configuration
from src.yandex_disk_api import *
from src.SyncFiles import SyncFiles
from src.client import Client

import configparser
import sys
import time
from pathlib import Path

CONFIG_FNAME = "conf.conf"
SYNC_FILES_FNAME = "sync.files"


class Daemon:
    def __init__(self):
        self.sleep_time = Configuration().get_daemon_sleep_time()

    def run(self):
        print("Daemon.run()")
        try:
            files_sync = SyncFiles().get_paths(True)
            for x in files_sync:
                self.sync(x)

            files_init = SyncFiles().get_paths(False)
            for x in files_init:
                self.init_path(x)
        except EnvironmentError as e:
            sys.stderr.write(SYNC_FILES_FNAME + " doesn't exists")
            time.sleep(Configuration.get_daemon_sleep_time())
            self.run()
        except YandexDiskException as e:
            sys.stderr.write(str(e))
            time.sleep(Configuration.get_daemon_sleep_time())
            self.run();

    def sync(self, path):
        print("is sync method " + path)

    def sync_one_file(self, fname):
        import os, time
        local_exists, disk_exists = Path(fname).exists(), False
        local_modified, disk_modified = None, None

        import json, datetime
        try:
            dirname = os.path.dirname(fname)
            dirname = "/" + dirname
            cli = Client()
            for x in cli.disk.get_content_of_folder(dirname).get_children():
                if type(x) is File and x.name == fname.split("/")[-1]:
                    disk_modified = x.modified
                    disk_path = x.path
                    disk_exists = True

            if local_exists == True and disk_exists == False:
                print("upload " + fname)
                cli.upload(fname, dirname)
            elif local_exists == False and disk_exists == True:
                print("download " + fname)
                cli.download(fname, fname)
            elif local_exists == False and disk_exists == False:
                print(
                    "Warning: " + fname + " doesn't exists on Yandex.Disk and on local file system")
            else:
                local_modified = os.path.getmtime(fname)
                d = datetime.datetime.fromtimestamp(int(local_modified - 3 * 60 ** 2))
                local_modified = json.dumps(d.isoformat())
                local_modified = local_modified.split("\"")[1]

                print(local_modified + " " + disk_modified)


                print(local_modified[:13] + " " + disk_modified[:13])
                if local_modified[:13] > disk_modified[:13]:
                    print("removed " + disk_path + " on disk ..")
                    cli.disk.remove_folder_or_file(disk_path)
                    print("upload " + fname + " ...")
                    cli.upload(fname, dirname)
                elif local_modified[:13] < disk_modified[:13]:
                    print("removed local " + fname + " ...")
                    os.remove(fname)
                    print("download " + fname + " ...")
                    cli.download(disk_path)

        except YandexDiskException as e:
            print(e)
            sys.exit(1)


def main():
    daemon = Daemon()
    daemon.sync_one_file("_TEST2.txt")


if __name__ == "__main__":
    main()
