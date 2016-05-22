#!/usr/bin/python3.4
from select import select

from src.Configuration import Configuration
from src.yandex_disk_api import *
from src.client import Client

import sys, json, time, os, hashlib, shutil

CONFIG_FNAME = "conf.conf"


class FileSystem:
    def __init__(self):
        pass

    @staticmethod
    def get_md5(path_to_file):
        hash_md5 = hashlib.md5()
        with open(path_to_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_fs_dict(parent_dir):
        d = {'name': os.path.basename(parent_dir),
             'path': os.path.normpath(parent_dir)}
        if os.path.isdir(parent_dir):
            d['type'] = "dir"
        else:
            d['type'] = "file"
            d['size'] = os.path.getsize(parent_dir)
            d['md5'] = FileSystem.get_md5(parent_dir)

        if os.path.isdir(parent_dir):
            d['items'] = [
                FileSystem.get_fs_dict(os.path.join(parent_dir, x))
                for x in os.listdir(parent_dir)]
        return d


class Daemon:
    def __init__(self):
        self.config = Configuration()
        self.sleep_time = self.config.get_daemon_sleep_time()
        self.local_fs_fname = self.config.get_fs_image_file()
        self.disk_fs_fname = "$" + self.local_fs_fname
        try:
            self.client = Client()
        except YandexDiskException as e:
            print(" == " + str(e))
            sys.exit(2)

    def download_or_create_fs_file(self):
        '''
        after this methon on disk - filesync/fs.json
        and local - fs.json and $fs.json
        '''
        fs = FileSystem.get_fs_dict(".")
        with open(self.config.get_fs_image_file(), "w") as f:
            json.dump(fs, f, indent=2)
        try:
            with open("$" + self.config.get_fs_image_file(), "w") as f:
                json.dump(self.client.disk.get_folder_meta_dict(
                    self.config.get_app_dir()), f, indent=2)
        except YandexDiskException as e:
            print(" == " + str(e))
            sys.exit()

    def get_local_and_disk_fs_dict(self, path_to_local_fs, path_to_disk_fs):
        fs = FileSystem()
        with open(path_to_local_fs, "r") as flocal:
            local_json = flocal.read()
        with open(path_to_disk_fs, "r") as fdisk:
            disk_json = fdisk.read()

        local = json.loads(local_json)
        disk = json.loads(disk_json)
        return (local, disk)

    def sync_init(self, local, disk):
        if disk == local:
            print(disk['name'] + "==" + local['name'])
        elif disk['type'] == local['type'] == "dir" and disk['name'] == local[
            'name']:
            for x in disk['children']:
                for y in local['children']:
                    if y['name'] == x['name']:
                        self.sync_init(x, y)
                        break
                else:
                    self.client.download_dir_or_file(
                        self.config.get_app_dir() + "/" + x['path'][1:],
                        x['path'], True)
        else:
            self.client.download_dir_or_file("/" + disk['path'][1:],
                                             disk['path'], True)

    def sync_local_priority(self, local, disk):
        print(local)
        print(disk)
        if disk == local:
            print(disk['name'] + "==" + local['name'])
        elif local['type'] == "file":
            try:
                self.client.disk.remove_folder_or_file(
                    self.config.get_app_dir() + "/" + local['path'])
            except:
                pass
            self.client.upload_dir_or_file(local['path'],
                                           self.config.get_app_dir() + "/" +
                                           local['path'])
        else:
            for x in local['children']:
                for y in disk['children']:
                    if y['name'] == x['name']:
                        self.sync_local_priority(x, y)
                        break;
                else:
                    try:
                        self.client.disk.remove_folder_or_file(
                            self.config.get_app_dir() + "/" +
                            x['path'])
                    except:
                        pass
                    self.client.upload_dir_or_file(x['path'],
                                                   self.config.get_app_dir() + "/" +
                                                   x['path'])

    def comp(self, local, disk):
        '''Предусмотреть одноименность файла и дира'''
        if local['type'] == disk['type'] == "file":
            if local['name'] == disk['name']:
                if local['md5'] == disk['md5']:
                    print(local['name'] + " == " + disk['name'] + " <<< files")
                else:
                    print(local['name'] + " != (md5) " + disk['name'] + " <<< files")
        elif local['type'] == disk['type'] == "dir":
            for x in local['items']:
                for y in disk['items']:
                    if x['name'] == y['name'] and x['type'] == y['type']:
                        self.comp(x, y)
                        break
                else:
                    print(x['name'] + " doesn't exists on disk")
            

            pass


    def run(self):
        self.download_or_create_fs_file()
        local, disk = self.get_local_and_disk_fs_dict(self.local_fs_fname,
                                                      self.disk_fs_fname)
        print(disk)
        # self.sync_local_priority(local, disk)


def main():
    daemon = Daemon()
    daemon.run()


if __name__ == "__main__":
    main()
