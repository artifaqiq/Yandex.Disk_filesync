#!/usr/bin/python3.4
from config import Configuration
from yandex_disk_api import *

import requests, sys, os.path, shutil, configparser

class Client:
    def __init__(self, conf):
        try:
            token = conf.get_option("disk", "oauth")
        except Exception as e:
            raise YandexDiskException(0, "configuration file exception")
        self.disk = YandexDiskRestClient(token)

    def get_disk_info(self, devider=1024 ** 2):
        try:
            meta = self.disk.get_disk_metadata()
            return (meta.total_space // devider,
                    meta.used_space // devider,
                    meta.trash_size // devider)
        except YandexDiskException as e:
            raise e

    def mkdir(self, path, mes=False, rm_exist=False):
        try:
            if rm_exist:
                try:
                    self.disk.get_content_of_folder(path)
                except:
                    pass
                else:
                    if mes: print(" -- remove " + path)
                    self.disk.remove_folder_or_file(path)
            if mes: print(" -- mkdir " + path)
            self.disk.create_folder(path)
        except YandexDiskException as e:
            raise e

    def download_file(self, source_path, dest_path, mes=False, rm_exist=False):
        if os.path.exists(dest_path) and not rm_exist:
            if mes: print(" == " + dest_path + " already exists")
            return False
        elif os.path.exists(dest_path) and rm_exist and mes:
            print(" -- remove " + dest_path)
        try:
            if self.disk.get_content_of_folder(source_path).type == "dir":
                if mes: print(" == " + dest_path + " is a directory")
                return False

            href = self.disk.get_download_link_to_file(source_path)['href']
            fname = source_path.split("/")[
                -1] if dest_path == None else dest_path

            BUFF_SIZE = 1024 * 128
            source = requests.get(href, stream=True)
            if mes: print(" -- downloading " + fname + " ...")

            with open(fname, "wb") as dest:
                downloaded = 0;
                for chunk in source.iter_content(chunk_size=BUFF_SIZE):
                    if chunk:
                        dest.write(chunk)
                        downloaded += BUFF_SIZE
                        if mes == True:
                            print(" -- <<< {0}  MB downloaded ...".format(
                                round(downloaded // 1024 / 1024, 1)), end="\r")
            if mes: print(
                " -- " + fname + " successfully downloaded")
        except YandexDiskException as e:
            raise e
        else:
            return True

    def download_dir_or_file(self, source_path, dest_path, mes=False,
                             rm_exist=False):
        if os.path.exists(dest_path):
            if rm_exist:
                if mes: print(" -- remove -rf " + dest_path)
                if os.path.isfile(dest_path):
                    os.remove(dest_path)
                else:
                    shutil.rmtree(dest_path)
            else:
                if mes: print(" == " + dest_path + " already exists")
                return False
        try:
            meta = self.disk.get_content_of_folder(source_path)
        except:
            if mes: print(" == " + source_path + " doesn't exists")
            return False
        try:
            if meta.type == "file":
                self.download_file(source_path, dest_path, mes)
            else:
                if mes: print(" -- mkdir " + dest_path)
                os.mkdir(dest_path)
                for x in meta.get_children():
                    self.download_dir_or_file(x.path,
                                              os.path.join(dest_path, x.name),
                                              mes)
        except YandexDiskException as e:
            print(source_path)
            raise e

    def upload_file(self, source_path, dest_path, mes=False, rm_exist=False):
        try:
            self.disk.get_content_of_folder(dest_path)
        except YandexDiskException as e:
            pass
        else:
            if rm_exist:
                if mes: print(" -- remove " + dest_path)
                self.disk.remove_folder_or_file(dest_path)
            else:
                if mes: print(" == " + dest_path + " already exists")
                return False

        if not os.path.exists(source_path):
            if mes: print(" == " + source_path + " doesn't exists")
            return False
        if not os.path.isfile(source_path):
            if mes: print(" == " + source_path + " is not a file")
            return False
        try:
            if mes: sys.stdout.write(" -- uploading " + source_path + " ...\r")
            self.disk.upload_file(source_path, dest_path)
            if mes: print(
                " -- " + source_path + " successfully uploaded to " + dest_path)
        except YandexDiskException as e:
            raise e
        else:
            return True

    def upload_dir_or_file(self, source_path, dest_path, mes=False,
                           rm_exist=False):
        if not os.path.exists(source_path):
            if mes: print(" == " + source_path + " doesn't exists")
            return False
        try:
            if rm_exist:
                try:
                    self.disk.get_content_of_folder(dest_path)
                except YandexDiskException:
                    pass
                else:
                    if mes: print(" -- remove " + dest_path)
                    self.disk.remove_folder_or_file(dest_path)

            if os.path.isfile(source_path):
                self.upload_file(source_path, dest_path, mes, False)
            else:
                if mes: print(" -- mkdir " + dest_path)
                self.disk. create_folder(dest_path)
                for x in os.listdir(source_path):
                    self.upload_dir_or_file(os.path.join(source_path, x),
                                            dest_path + "/" + x, mes, False)

        except YandexDiskException as e:
            raise e

    def upload_from_url(self, source_url, dest_path, mes=False):
        fname = source_url.split("/")[-1]
        try:
            self.disk.upload_file_from_url(source_url, dest_path)
            if mes: print(fname + "successfully uploaded to " + dest_path)
        except YandexDiskException as e:
            raise e

    def cp(self, source_path, dest_path, mes=False):
        try:
            self.disk.copy_folder_or_file(source_path, dest_path)
            if mes: print(
                " -- " + source_path + " successfully copied to " + dest_path)
        except YandexDiskException as e:
            raise e

    def move(self, source_path, dest_path, mes=False):
        try:
            self.disk.move_folder_or_file(source_path, dest_path)
            if mes: print(
                " -- " + source_path + " successfully moved to " + dest_path)
        except YandexDiskException as e:
            raise e

    def show_fs(self, path, all=False, depth = 0):
        try:
            files = self.disk.get_folder_meta_dict(path)
        except YandexDiskException as e:
            raise e

        for x in files['items']:
            if x['type'] == "file":
                size = "" if not all else round(x['size'] / 1024, 1)
                if not size == "":
                    if size > 1000:
                        size = round(size /1024, 1)
                        size = str(size) + " MB"
                    else:
                        size = str(size) + " KB"
                print((" " * 3 * depth) + x['name'] + ((60 - depth * 3 - len(x['name'])) * " ") + " " + size)
            else:
                print((" " * 3 * depth) + x['name'] + "/")
                self.show_fs(x['path'], all, depth + 1)