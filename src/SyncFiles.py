from pathlib import Path

SYNC_FILES_FNAME = "sync.files"

class SyncFiles:
    def __init__(self):
        self.FNAME = SYNC_FILES_FNAME
        if (Path(self.FNAME).exists() == False):
            f = open(self.FNAME, "w")
            f.close()

    def get_paths(self):
        paths = []
        try:
            with open(self.FNAME, "r") as file:
                for line in file:
                    paths.append(line[:-1])

        except EnvironmentError as e:
            import sys
            sys.stderr.write(SYNC_FILES_FNAME + " doesn't exists")
        else:
            return paths

    def remove_path(self, path):
        try:
            with open(self.FNAME, "r") as file:
                lines = file.readlines()
            with open(self.FNAME, "w") as file:
                for line in lines:
                    if path not in line:
                        file.write(line)
        except EnvironmentError as e:
            import sys
            sys.stderr.write(SYNC_FILES_FNAME + " doesn't exists")
            raise e

    def write_path(self, path):
        try:
            with open(self.FNAME, "a") as file:
                file.write(path + "\n")
        except EnvironmentError as e:
            import sys
            sys.stderr.write(SYNC_FILES_FNAME + " doesn't exists")
            raise e
