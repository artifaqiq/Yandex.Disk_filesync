import configparser, os, sys

class Configuration():
    def __init__(self, path_to_config):
        self.PATH = path_to_config
        if os.path.exists(self.PATH) == False:
            try:
                f = open(self.PATH, "r")
                f.close()
            except Exception as e:
                raise e

    @staticmethod
    def init_config_file(self, path_to_config):
        if os.path.exists(path_to_config):
            os.remove(path_to_config)
        print(" -- create configuration file " + self.PATH)
        try:
            f = open(self.PATH, "w")
            f.close()
        except Exception as e:
            print(" == error create configuration file : " + str(e) + "\n")
            raise e

        conf = Configuration(path_to_config)
        conf.set_option("disk", "oauth", " ")
        conf.set_option("disk", "app-dir", "/fsync")
        conf.set_option("daemon", "sleep", "5")
        conf.set_option("daemon", "sync-dir", ".")

    def set_option(self, section, option, value):
        try:
            config = configparser.SafeConfigParser()
            config.read(self.PATH)
            config.set(section, option, value)
            with open(self.PATH, "w") as f:
                config.write(f)
        except configparser.Error as e:
            return False
        else:
            return True

    def get_option(self, section, option):
        try:
            config = configparser.RawConfigParser()
            config.read(self.PATH)
            value = config.get("disk", "OAuth")
        except configparser.Error as e:
            return False
        else:
            return value
