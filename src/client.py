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
                self.disk.create_folder(dest_path)
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
        except YandexDiskRestClient as e:
            raise e

    def move(self, source_path, dest_path, mes=False):
        try:
            self.disk.move_folder_or_file(source_path, dest_path)
            if mes: print(
                " -- " + source_path + " successfully moved to " + dest_path)
        except YandexDiskException as e:
            raise e

    def show_fs(self):
        import os.path, json
        if os.path.exists("$fs.json") == False:
            print(" == $fs.json doesn't exists")
            return
        else:
            def print_fs(dict, depth=0):
                sys.stdout.write(" " * depth * 3)
                if dict['type'] == "file":
                    print(dict['name'])
                else:
                    print(dict['name'] + "/")
                    for x in dict['children']:
                        print_fs(x, depth + 1)

            with open("$fs.json", "r") as flocal:
                disk_json = flocal.read()
            disk = json.loads(disk_json)
            print(" -- ")
            print_fs(disk, 1)
            return


if __name__ == "__main__":
    import sys

    def usage():
        print("\n\tusage: " + sys.argv[0] + " command <args...>")
        print("\n\thelp\t\tshow this message")
        print("\n\tdownload <path>\t\tdownload file")
        print("\n\tupload <path>\t\tupload file")
        print("\n\tinfo\t\tshow disk meta info")
        print("\n\tmkdir <path>\t\tmake directory on disk")
        print("\n\tcopy <source_path> <dest_path>\t\tcopy file")
        print("\n\tremove <path>\t\tremove file or dir")
        print("")


    def main():
        try:
            try:
                conf = Configuration("conf.conf")
            except Exception as e:
                print(" == " + str(e))
                sys.exit()
            cli = Client(conf)
            from filesys import FileSystemImage
            filesys = FileSystemImage(conf.get_option("daemon", "home-dir"), conf.get_option("daemon", "app-dir"), cli)
            filesys.sync_disk_priority(True, True, True)
            sys.exit()

            if len(sys.argv) == 1:
                usage()
                return 0
            elif sys.argv[1] == "global":
                if sys.argv[2] in ["--set-oauth"] and len(
                        sys.argv) == 4:
                    conf.set_option("disk", "oauth", sys.argv[3])
                    print(
                        " -- new OAuth token : " + conf.get_option("disk",
                                                                   "oauth"))
                elif len(sys.argv) == 3 and sys.argv[2] in ["--get-oauth"]:
                    print(
                        " -- OAuth token: " + conf.get_option("disk", "oauth"))
                elif sys.argv[2] in ["--set-daemon-sleep-time",
                                     "--set-sleep",
                                     "--set-sleep-time"] and len(
                    sys.argv) == 4:
                    if not sys.argv[3].isdigit():
                        print(
                            " == enter the number of seconds, example : 5")
                    else:
                        conf.set_option("daemon", "sleep-time", sys.argv[3])
                        print(
                            " -- new daemon sleep time : " +
                            conf.get_option("daemon", "sleep-time") + " sec.")
                elif len(sys.argv) == 3 and sys.argv[2] in ["--get-sleep",
                                                            "--get-daemon-sleep",
                                                            "--get-sleep-time",
                                                            "--get-daemon-sleep-time"]:
                    print(
                        " -- daemon sleep time : " + conf.get_option("daemon",
                                                                     "sleep-time") + " sec")

                elif sys.argv[2] in ["info"]:
                    total, used, trash = cli.get_disk_info()
                    print(" -- total space : " + str(total) + " MB")
                    print(" -- used space  : " + str(used) + " MB")
                    print(" -- free space  : " + str(total - used))
                    print(" -- trash size  : " + str(trash) + " MB")

            elif sys.argv[1] in ["download", "dwnld", "get"] and len(
                    sys.argv) >= 3:
                optlen, r, m = 0, False, False
                if "-" in sys.argv[2]:
                    optlen = 1
                    if "r" in sys.argv[2]:
                        r = True
                    if "m" in sys.argv[2]:
                        m = True
                dest = os.path.basename(sys.argv[2 + optlen]) if len(
                    sys.argv) - optlen == 3 else sys.argv[3 + optlen]

                if r:
                    cli.download_dir_or_file(sys.argv[2 + optlen], dest, True,
                                             m)
                else:
                    cli.download_file(sys.argv[2 + optlen], dest, True, m)

            elif sys.argv[1] in ["upload", "upld", "put"] and len(
                    sys.argv) >= 3:
                optlen, r, m = 0, False, False
                if "-" in sys.argv[2]:
                    optlen = 1
                    if "r" in sys.argv[2]:
                        r = True
                    if "m" in sys.argv[2]:
                        m = True
                dest = os.path.basename(sys.argv[2 + optlen]) if len(
                    sys.argv) - optlen == 3 else sys.argv[3 + optlen]

                if r:
                    cli.upload_dir_or_file(sys.argv[2 + optlen], dest, True, m)
                else:
                    cli.upload_file(sys.argv[2 + optlen], dest, True, m)

            elif sys.argv[1] in ["remove", "rm", "rmv"] and len(sys.argv) == 3:
                cli.disk.remove_folder_or_file(sys.argv[2])
                print(" -- " + sys.argv[2] + " successfully removed")
            elif sys.argv[1] in ["mkdir"] and len(sys.argv) == 3:
                cli.mkdir(sys.argv[2])
                print(" -- " + sys.argv[2] + " successfully created")
            elif sys.argv[1] in ["cp", "cpy", "copy"] and len(sys.argv) == 4:
                cli.cp(sys.argv[2], sys.argv[3])
            elif sys.argv[1] in ["ls"] and len(sys.argv) == 3:
                files = cli.disk.get_content_of_folder(
                    sys.argv[2]).get_children()
                for f in files:
                    print(" -- " + f.name + (
                        "/" if type(f) is Directory else ""))
            elif sys.argv[1] in ["ls"] and len(sys.argv) == 2:
                cli.show_fs()
            elif sys.argv[1] in ["move", "mov"] and len(sys.argv) == 4:
                cli.move(sys.argv[2], sys.argv[3])
            elif sys.argv[1] in ["help"] and len(sys.argv) == 2:
                usage()
        except YandexDiskException as e:
            sys.stderr.write(" == " + str(e) + "\n")
        except configparser.Error as c:
            sys.stderr.write(
                " == config file exception\n == usage: " + sys.argv[
                    0] + " global --init\n")


    main()
