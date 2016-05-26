import hashlib, os.path

class FileSystemImage:
    def __init__(self):
        pass

    @staticmethod
    def get_md5(path_to_file):
        hash_md5 = hashlib.md5()
        with open(path_to_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_local_fs_image(parent_dir):
        d = {'name': os.path.basename(parent_dir),
             'path': os.path.normpath(parent_dir)}
        if os.path.isdir(parent_dir):
            d['type'] = "dir"
        else:
            d['type'] = "file"
            d['size'] = os.path.getsize(parent_dir)
            d['md5'] = FileSystemImage.get_md5(parent_dir)

        if os.path.isdir(parent_dir):
            d['items'] = [
                FileSystemImage.get_local_fs_image(os.path.join(parent_dir, x))
                for x in os.listdir(parent_dir)]
        return d

    def get_disk_fs_image(self, disk_client):
        pass