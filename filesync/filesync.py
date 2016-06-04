#!/usr/bin/python3.4
from client import *
from config import Configuration

import sys, subprocess

CONFIG_PATH = ".filesync.conf"

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
        if len(sys.argv) >= 2 and sys.argv[1] == "init":
            try:
                Configuration.init_config_file(CONFIG_PATH)
            except Exception as e:
                print(" == " + str(e))
            sys.exit()
        else:
            conf = Configuration(CONFIG_PATH)
        if len(sys.argv) == 1:
            usage()
            return 0
        elif sys.argv[1] == "global" and len(sys.argv) >= 3:
            if sys.argv[2] in ["--set-oauth"] and len(
                    sys.argv) == 4:
                conf.set_option("disk", "oauth", sys.argv[3])
                print(
                    " -- new OAuth token : " + conf.get_option("disk",
                                                               "oauth"))
            elif len(sys.argv) == 3 and sys.argv[2] in ["--get-oauth",
                                                        "--oauth"]:
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
            elif len(sys.argv) == 4 and sys.argv[2] in ["--set-app-dir"]:
                conf.set_option("daemon", "app-dir", sys.argv[3])
            elif len(sys.argv) == 3 and sys.argv[2] in ["--get-app-dir"]:
                print(
                    " -- app-dir : " + conf.get_option("daemon", "app-dir"))

            elif len(sys.argv) == 4 and sys.argv[2] in ["--set-home-dir"]:
                conf.set_option("daemon", "home-dir", sys.argv[3])
            elif len(sys.argv) == 3 and sys.argv[2] in ["--get-home-dir"]:
                print(
                    " -- app-dir : " + conf.get_option("daemon", "home-dir"))
            sys.exit()

        elif len(sys.argv) >= 3 and sys.argv[1] == "sync":
            if len(sys.argv) >= 4 and sys.argv[2] == "--set-save-orig":
                if sys.argv[3].upper() in ["true".upper(), 1]:
                    conf.set_option("sync", "save-orig", "True")
                elif sys.argv[3].upper() in ["false".upper(), 0]:
                    conf.set_option("sync", "save-orig", "False")
                else:
                    print(" == enter True or False")
            elif sys.argv[2] == "--get-save-orig":
                print(" -- " + conf.get_option("sync", "save-orig"))

            elif len(sys.argv) >= 4 and sys.argv[2] == "--set-rm-exists":
                if sys.argv[3].upper() in ["true".upper(), "1"]:
                    conf.set_option("sync", "rm-exists", "True")
                elif sys.argv[3].upper() in ["false".upper(), "0"]:
                    conf.set_option("sync", "rm-exists", "False")
                else:
                    print(" == enter True or False")
            elif sys.argv[2] == "--get-rm-exists":
                print(" -- " + conf.get_option("sync", "rm-exists"))
            elif sys.argv[2] == "start" and len(sys.argv) == 3:
                print(" -- start daemon")
                subprocess.call("python3.4 daemon.py &")
            elif sys.argv[2] == "start" and len(sys.argv) == 4 and sys.argv[3] == "mes":
                print(" -- start daemon")
                subprocess.call("python3.4 ../src/daemon.py mes &")


        cli = Client(conf)
        if sys.argv[1] in ["download", "dwnld", "get"] and len(
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

        elif sys.argv[1] in ["info"]:
            total, used, trash = cli.get_disk_info()
            print(" -- total space : " + str(total) + " MB")
            print(" -- used space  : " + str(used) + " MB")
            print(" -- free space  : " + str(total - used))
            print(" -- trash size  : " + str(trash) + " MB")

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
                0] + " init\n")
    except FileNotFoundError as f:
        sys.stderr.write(" == usage " + sys.argv[0] + " init\n")
    except Exception as e1:
        sys.stderr.write(" == " + str(e1))

if __name__ == "__main__":
    main()
