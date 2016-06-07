import configparser, os

class Configuration():
    def __init__(self, path_to_config):
        self.path = path_to_config
        if os.path.exists(self.path) == False:
            try:
                f = open(self.path, "r")
                f.close()
            except Exception as e:
                raise e

    @staticmethod
    def init_config_file(path_to_config):
        if os.path.exists(path_to_config):
            os.remove(path_to_config)
        f = open(path_to_config, "w")
        f.close()

        conf = Configuration(path_to_config)
        conf.set_option("disk", "oauth", " ")
        conf.set_option("daemon", "app-dir", "/fsync")
        conf.set_option("daemon", "sleep-time", "5")
        conf.set_option("daemon", "home-dir", ".")
        conf.set_option("sync", "rm-exists", "True")
        conf.set_option("sync", "save-orig", "False")


    def set_option(self, section, option, value):
        try:
            config = configparser.SafeConfigParser()
            config.read(self.path)
            if not section in config.sections():
                config.add_section(section)
            config.set(section, option, value)
            with open(self.path, "w") as f:
                config.write(f)
        except configparser.Error as e:
            raise e
        else:
            return True

    def get_option(self, section, option):
        try:
            config = configparser.RawConfigParser()
            config.read(self.path)
            return config.get(section, option)
        except configparser.Error as e:
            raise e

