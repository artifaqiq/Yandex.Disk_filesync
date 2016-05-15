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
                " == configuration file error. OAuth not defined.\nuse cli global --set_oauth <token>\n")
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
