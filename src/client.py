from yandex_disk_api import *
from Configuration import Configuration

import requests
from pathlib import Path

CONFIG_FNAME = "conf.conf"


class Client:
    def __init__(self):
        self.token = Configuration().get_oauth()
        self.disk = YandexDiskRestClient(self.token)

    def get_disk_info(self, devider=1024 ** 2):
        try:
            meta = self.disk.get_disk_metadata()
            return (meta.total_space // devider,
                    meta.used_space // devider,
                    meta.trash_size // devider)
        except YandexDiskException as e:
            raise e

    def mkdir(self, path):
        try:
            self.disk.create_folder(path)
        except YandexDiskException as e:
            print(e)
            return False
        else:
            return True

    def download(self, source_path, dest_path=None, mes=False):
        try:
            href = self.disk.get_download_link_to_file(source_path)['href']
            fname = source_path.split("/")[
                -1] if dest_path == None else dest_path

            BUFF_SIZE = 1024 ** 2
            source = requests.get(href, stream=True)
            print("Downloaded " + fname + " ...")

            with open(fname, "wb") as dest:
                downloaded = 0;
                for chunk in source.iter_content(chunk_size=BUFF_SIZE):
                    if chunk:
                        dest.write(chunk)
                        downloaded += BUFF_SIZE
                        if (mes == True):
                            print(" <<< {0} +  MB downloaded".format(
                                downloaded // 1024 / 1024), end="\r")
            if (mes == True): print(fname + " successfully downloaded")
        except YandexDiskException as e:
            return False
        else:
            return True

    def upload(self, source_path, dest_path):
        fname = source_path.split("/")[-1]
        from pathlib import Path
        if (Path(source_path).exists() == False):
            print(source_path + " don't exists")
            return False
        if (Path(source_path).is_file() == False):
            print(source_path + " is not a file")
            return False

        try:
            if dest_path[-1] == "/":
                self.disk.upload_file(source_path, dest_path + fname)
            else:
                self.disk.upload_file(source_path, dest_path + "/" + fname)
            print(fname + " successfully uploaded in " + dest_path)
        except YandexDiskException as e:
            raise e

    def upload_from_url(self, source_url, dest_path):
        fname = source_url.split("/")[-1]
        try:
            if dest_path[-1] == "/":
                self.disk.upload_file_from_url(source_url, dest_path + fname)
            else:
                self.disk.upload_file_from_url(source_url,
                                               dest_path + "/" + fname)
            print(fname + "successfully uploaded in " + dest_path)
        except YandexDiskException as e:
            raise e

    def cp(self, source_path, dest_path):
        source_fname = source_path.split("/")[-1]
        try:
            self.disk.copy_folder_or_file(source_path, dest_path)
            print(source_fname + " successfully copied to " + dest_path)
        except YandexDiskRestClient as e:
            raise e

    def move(self, source_path, dest_path):
        try:
            self.disk.move_folder_or_file(source_path, dest_path)
            print(source_path + " successfully moved to " + dest_path)
        except YandexDiskException as e:
            raise e

    def download_dir(self, source_path, current_path=""):
        path = Path(source_path.split("/")[-1])
        if current_path == "": current_path = str(path)
        print("make directory " + current_path)
        if path.exists():
            print(
                "removing existing local directory " + current_path + "/ ...")
            try:
                print(" ::: " + path.absolute())
                import shutil
                shutil.rmtree(path.absolute())
            except Exception:
                print(
                    "local directory " + current_path + "/ can not be removed")
                return False
        Path(current_path).mkdir()
        try:
            files = self.disk.get_content_of_folder(source_path)
            for f in files.get_children():
                if type(f) is Directory:
                    self.download_dir(source_path + "/" + f.name,
                                      current_path + "/" + f.name)
                elif type(f) is File:
                    self.download(source_path + "/" + f.name,
                                  current_path + "/" + f.name)
        except YandexDiskRestClient as e:
            raise e;


if __name__ == "__main__":
    import sys


    def usage():
        print("usage: cli command <args...>")


    def main():
        try:
            cli = Client()

            if len(sys.argv) == 1:
                usage()
                return 0
            if sys.argv[1] == "global":
                if sys.argv[2] in ["--set_oauth"] and len(
                        sys.argv) >= 4:
                    Configuration().set_oauth(sys.argv[3])
                    print(
                        " -- set a new OAuth token : " + Configuration().get_oauth())
                elif len(sys.argv) >= 3 and sys.argv[2] in ["--get_oauth"]:
                    print(" -- OAuth token: " + Configuration().get_oauth())
                elif sys.argv[2] in ["--set_daemon_sleep_time",
                                     "--set_sleep",
                                     "--set_sleep_time"] and len(
                    sys.argv) >= 4:
                    if sys.argv[3].isdigit() == False:
                        print(
                            " == enter the number of seconds, example : 5")
                    else:
                        Configuration().set_daemon_sleep_time(
                            float(sys.argv[3]))
                        print(
                            " -- set a new daemon sleep time : " +
                            Configuration().get_daemon_sleep_time())
                elif len(sys.argv) >= 3 and sys.argv[2] in ["--get_sleep",
                                                            "--get_daemon_sleep",
                                                            "--get_sleep_time",
                                                            "--get_daemon_sleep_time"]:
                    print(
                        " -- daemon sleep time : " + Configuration().get_daemon_sleep_time())
        except YandexDiskException as e:
            sys.stderr.write(str(e))


    main()
