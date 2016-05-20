import configparser
import os, sys
CONFIG_FNAME = "conf.conf"

class Configuration():

    def __init__(self):
        self.FNAME = CONFIG_FNAME
        if os.path.exists(self.FNAME) == False:
            print(" -- create configuration file " + self.FNAME)
            try:
                f = open(self.FNAME, "wb")
                f.close()
            except Exception as e:
                print(" == error create configuration file : " + str(e) + "\n")
                sys.exit()

    def set_oauth(self, oauth):
        try:
            config = configparser.SafeConfigParser()
            config.read(CONFIG_FNAME)
            config.set("disk", "OAuth", oauth)
            with open(CONFIG_FNAME, "w") as f:
                config.write(f)
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file exception: " + str(e) + "\n")
            sys.exit()

    def get_oauth(self):
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FNAME)
            token = config.get("disk", "OAuth")
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file error. OAuth not defined.\n\
                use cli global --set_oauth <token>\n")
            sys.exit()
        else:
            return token

    def set_daemon_sleep_time(self, sec):
        try:
            config = configparser.SafeConfigParser()
            config.read(CONFIG_FNAME)
            config.set("daemon", "sleep_time", str(sec))
            with open(CONFIG_FNAME, "w") as f:
                config.write(f)
        except configparser.Error as e:
            sys.stderr.write(" == configuration file exception : " + str(e))
            sys.exit()

    def get_daemon_sleep_time(self):
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FNAME)
            sleep_time = config.get("daemon", "sleep_time")
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file exception. Daemon sleep time not defined\n")
            sys.stderr.write(" == use cli global --set_sleep_time <sec>")
            sys.exit()
        else:
            return sleep_time

    def set_home_dir(self, path):
        try:
            config = configparser.SafeConfigParser()
            config.read(CONFIG_FNAME)
            config.set("daemon", "home_dir", str(path))
            with open(CONFIG_FNAME, "w") as f:
                config.write(f)
        except configparser.Error as e:
            sys.stderr.write(" == configuration file exception : " + str(e))
            sys.exit()

    def get_home_dir(self):
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FNAME)
            sleep_time = config.get("daemon", "home_dir")
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file exception. Daemon sleep time not defined\n")
            sys.stderr.write(" == use cli global --set-sleep-time <sec>")
            sys.exit()
        else:
            return sleep_time

    def set_fs_image_file(self, path):
        try:
            config = configparser.SafeConfigParser()
            config.read(CONFIG_FNAME)
            config.set("daemon", "file_system_image_file", path)
            with open(CONFIG_FNAME, "w") as f:
                config.write(f)
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file exception: " + str(e) + "\n")
            sys.exit()

    def get_fs_image_file(self):
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FNAME)
            fs_img_file = config.get("daemon", "file_system_image_file")
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file error. file system image file not defined.\nuse cli\
                 global --set-fs-image-file <path>\n")
            sys.exit()
        else:
            return fs_img_file

    def set_app_dir(self, path):
        try:
            config = configparser.SafeConfigParser()
            config.read(CONFIG_FNAME)
            config.set("disk", "app-dir", path)
            with open(CONFIG_FNAME, "w") as f:
                config.write(f)
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file exception: " + str(e) + "\n")
            sys.exit()

    def get_app_dir(self):
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FNAME)
            app_dir = config.get("disk", "app-dir")
        except configparser.Error as e:
            sys.stderr.write(
                " == configuration file error. Application dir not defined.\n/"
                "use cli global --set-app-dir <path>\n")
            sys.exit()
        else:
            return app_dir

