#!/usr/bin/python3.4
from select import select

from src.Configuration import Configuration
from src.yandex_disk_api import *
from src.client import Client

import sys, json, time, os
from pathlib import Path

CONFIG_FNAME = "conf.conf"
SYNC_FILES_FNAME = "sync.files"


class FileSystem:
    def __init__(self):
        self.home_dir = Configuration().get_home_dir()

    def _get_fs_tree(self, parent_dir):
        d = {'path': os.path.abspath(parent_dir),
             'name': os.path.basename(parent_dir),
             'modified': os.path.getmtime(parent_dir),
             'created': os.path.getctime(parent_dir)}
        if os.path.isdir(parent_dir):
            d['type'] = "dir"
        else:
            d['type'] = "file"
            d['size'] = os.path.getsize(parent_dir)

        if os.path.isdir(parent_dir):
            d['children'] = [self._get_fs_tree(os.path.join(parent_dir, x))
                             for x in os.listdir(parent_dir)]
        return d

    def get_fs(self):
        return self._get_fs_tree(self.home_dir)


class Daemon:
    def __init__(self):
        self.config = Configuration()
        self.sleep_time = self.config.get_daemon_sleep_time()
        try:
            self.client = Client()
        except YandexDiskException as e:
            print(" == " + str(e))
            sys.exit(2)

    def download_or_create_fs_file(self):
        try:
            if self.client.download(self.config.get_app_dir() + "/"
                                                    + self.config.get_fs_image_file(),
                                            "$" + self.config.get_fs_image_file(),
                                            True) == True: pass
            else:
                self.client.mkdir(self.config.get_app_dir())
                fs = FileSystem().get_fs()
                with open(self.config.get_fs_image_file(), "w") as f:
                    json.dump(fs, f, indent=2)
                self.client.upload(self.config.get_fs_image_file(),
                                   self.config.get_app_dir() + "/fs.json")

        except YandexDiskException as e:
            print(" == " + str(e))
            sys.exit()

    def run(self):
        self.download_or_create_fs_file()
        

def main():
    daemon = Daemon()
    daemon.run()


if __name__ == "__main__":
    main()
