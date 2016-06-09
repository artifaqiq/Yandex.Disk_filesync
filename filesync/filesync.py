#!/usr/bin/python3.4
from client import *
from synchronizer import *

import sys


def usage():
    print("\tusage: " + sys.argv[0] + " command <args...>")
    print("\n\tsetup\t\t\t\t\tinitial configuration\n")
    print("\n\thelp\t\t\t\t\tshow this message")
    print("\tinfo\t\t\t\t\tshow disk meta info")
    print("\tdownload [-rm] <path>\t\t\tdownload file")
    print("\tupload [-rm] <path>\t\t\tupload file")
    print("\tmkdir <path>\t\t\t\tmake directory on disk")
    print("\tcopy <source> <dest>\t\t\tcopy file")
    print("\tremove <path>\t\t\t\tremove file or dir")
    print("\tmove <source> <dest>\t\t\tmove from source to dest")
    print("\tls [-sr] <path>\t\t\t\tlist files")
    print("")

    print("\tstart\t\t\t\t\tstart sync daemon")
    print("\tstop\t\t\t\t\tstop sync daemon")
    print("\tstatus\t\t\t\t\tshow last sync files")
    print("")

    print("\tglobal")
    print("\t\t--set-oauth <new-token>\t\tset OAuth token")
    print("\t\t--get-oauth \t\t\tsee OAuth token")
    print("\t\t--set-daemon-sleep-time <sec>\tset sync-daemon sleep time")
    print("\t\t--get-daemon-sleep-time\t\tget sync-daemon sleep time")
    print("\t\t--set-home-dir <path>\t\tset sync home dir")
    print("\t\t--get-home-dir <path>\t\tget sync home dir")
    print("\t\t--set-app-dir <path>\t\tset application directory on disk")
    print(
        "\t\t--get-app-dir <path>\t\tget path to application directory on disk")
    print("")

    print("\tsync")
    print("\t\t--set-save-orig <true/false>\tsave " +
          "the conflicting files with the extension \"*.orig\"")
    print("\t\t--get-save-orig")
    print("\t\t--set-rm-exists <true/false>\tremove files do not conflict")
    print("\t\t--get-rm-exists")


def main():
    try:
        if len(sys.argv) >= 2 and sys.argv[1] == "setup":
            setup()
        conf = Configuration(CONFIG_PATH)
        if len(sys.argv) == 1:
            usage()
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
                if not os.path.exists(sys.argv[3]):
                    print(" == " + sys.argv[3] + " doens't exists")
                elif not os.path.isdir(sys.argv[3]):
                    print(" == " + sys.argv[3] + " is not a directory")
                else:
                    conf.set_option("daemon", "home-dir", sys.argv[3])
                    DaeomonLauncher().restart()
            elif len(sys.argv) == 3 and sys.argv[2] in ["--get-home-dir"]:
                print(
                    " -- home-dir : " + conf.get_option("daemon", "home-dir"))
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

        elif len(sys.argv) >= 2 and sys.argv[1] == "start":
            DaeomonLauncher().start()
        elif len(sys.argv) >= 2 and sys.argv[1] == "stop":
            DaeomonLauncher().stop()
        elif len(sys.argv) >= 2 and sys.argv[1] == "restart":
            DaeomonLauncher().restart()
        elif len(sys.argv) >= 2 and sys.argv[1] == "status":
            if os.path.exists(DAEMON_LOG_PATH):
                with open(LOG_PATH, "r") as fd:
                    lines = fd.readlines()
            sys.stdout.write(" -- last sync files: \n\n")
            for line in lines[-10:]:
                sys.stdout.write(" -- " + line)
            print("")

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
        elif len(sys.argv) == 3 and sys.argv[1] in ["ls"]:
            files = cli.disk.get_content_of_folder(
                sys.argv[2])
            if (files.type != 'dir'):
                print(" == " + sys.argv[2] + " is not a directory")
            else:
                for f in files.get_children():
                    print(" -- " + f.name + (
                        "/" if type(f) is Directory else ""))
        elif sys.argv[1] in ["ls"] and len(sys.argv) == 2:
            print(" -- /")
            cli.show_fs("/", all=False, depth=2)
        elif len(sys.argv) == 4 and sys.argv[1] == "ls":
            if not cli.disk.get_content_of_folder(sys.argv[3]).type == "dir":
                print(" == " + sys.argv[3] + " is not a directory")
            elif sys.argv[2][0] == "-":
                rec = "r" in sys.argv[2]
                s = "s" in sys.argv[2]
                if rec:
                    print(" -- " + sys.argv[3])
                    cli.show_fs(sys.argv[3], s, depth=2)
                else:
                    files = cli.disk.get_content_of_folder(
                        sys.argv[3])
                    for f in files.get_children():
                        if type(f) is Directory:
                            print(" -- " + f.name + "/")
                        else:
                            size = round(f.size / 1024 + .1, 1)
                            if size > 1000:
                                size = round(size / 1024 + .1, 1)
                                size = str(size) + " MB"
                            else:
                                size = str(size) + " KB"
                            print(" -- " + f.name + " " + ((40 - len(f.name)) * " ") + size)


        elif sys.argv[1] in ["move", "mov"] and len(sys.argv) == 4:
            cli.move(sys.argv[2], sys.argv[3], True)
        elif sys.argv[1] in ["help"] and len(sys.argv) == 2:
            usage()

    except YandexDiskException as e:
        sys.stderr.write(" == " + str(e) + "\n")
    except configparser.Error as c:
        sys.stderr.write(
            " == config file error\n == usage: " + sys.argv[
                0] + " setup\n")
    except FileNotFoundError as f:
        sys.stderr.write(" == usage " + sys.argv[0] + " setup\n")
    except Exception as e1:
        sys.stderr.write(" == no internet connection\n ")


def setup():
    try:
        from os.path import expanduser

        print(
            "If you don't have a Yandex account yet, get one at \nhttps://passport.yandex.com/passport?mode=register")
        print(
            "If you have Yandex account, go to\nhttps://oauth.yandex.ru/verification_code?ncrnd=6596#access_token=ARcFkTsAAxRsr1H0O0iQR5m52-_Yz3xJvQ&token_type=bearer&expires_in=31536000\nand copy token here")

        sys.stdout.write("Enter your OAuth token : ")
        token = input()

        default_home_path = expanduser("~") + os.path.sep + "filesync"
        while True:
            sys.stdout.write(
                "Enter path to Yandex.Disk folder (leave empty " +
                "to use default folder " + expanduser(
                    "~") + os.path.sep + "filesync): ")
            home_path = input()
            if len(home_path) == 0:
                home_path = default_home_path
                break
            if os.path.exists(os.path.pardir(home_path)) and os.path.isdir():
                break

        if os.path.exists(home_path):
            if os.path.isdir(home_path):
                shutil.rmtree(home_path)
            else:
                os.remove(home_path)
        os.mkdir(home_path)

        if os.path.exists(APP_OPT_PATH):
            if os.path.isdir(APP_OPT_PATH):
                shutil.rmtree(APP_OPT_PATH)
            else:
                os.remove(APP_OPT_PATH)
        os.mkdir(APP_OPT_PATH)

        Configuration.init_config_file(CONFIG_PATH)
        conf = Configuration(CONFIG_PATH)
        conf.set_option("daemon", "home-dir", home_path)
        conf.set_option("disk", "oauth", token)
        try:
            cli = Client(conf)
            cli.mkdir(conf.get_option("daemon", "app-dir"))
        except YandexDiskException as e:
            pass
        print("Setup was successful")
    except Exception as e:
        print(" == " + str(e))
        return


if __name__ == "__main__":
    main()
