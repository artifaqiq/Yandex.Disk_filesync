from yandex_disk_api import *

import hashlib, os.path, shutil, logging

class FileSystemImage:
    def __init__(self, local_dir, disk_dir, client):
        self.local = self._get_local_fs_image(local_dir)
        self.disk = self._get_disk_fs_image(disk_dir, client)
        self.client = client
        self.exception_files = []

    @staticmethod
    def get_md5(path_to_file):
        hash_md5 = hashlib.md5()
        with open(path_to_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_local_fs_image(self, parent_dir):
        d = {'name': os.path.basename(parent_dir),
             'path': os.path.normpath(parent_dir)}
        if os.path.isdir(parent_dir):
            d['type'] = "dir"
            d['items'] = [
                self._get_local_fs_image(os.path.join(parent_dir, x))
                for x in os.listdir(parent_dir)]
        else:
            d['type'] = "file"
            d['size'] = os.path.getsize(parent_dir)
            d['md5'] = FileSystemImage.get_md5(parent_dir)

        return d

    def _get_disk_fs_image(self, parrent_dir, disk_client):
        try:
            meta = disk_client.disk.get_folder_meta_dict(parrent_dir)
        except YandexDiskException as e:
            raise e
        d = {'type': "dir",
             'path': meta['path'],
             'name': meta['path'].split('/')[-1],
             'items': []}
        for x in meta['items']:
            if x['type'] == "file":
                d['items'].append({'name': x['name'],
                                   'path': x['path'],
                                   'type': x['type'],
                                   'size': x['size'],
                                   'md5': x['md5']})
            else:
                d['items'].append(
                    self._get_disk_fs_image(x['path'], disk_client))
        return d

    def sync_local_priority(self, rm_exist=True, save_orig=False):
        self._sync_local_priority(self.local, self.disk, rm_exist, save_orig)

    def _sync_local_priority(self, local, disk, rm_exists, save_orig):
        if local['type'] == disk['type'] == "file":
            if local['name'] == disk['name']:
                if local['md5'] != disk['md5']:
                    if save_orig and ".orig" not in disk['path']:
                        logging.warning("move " + disk['path'] + " to " +
                                     disk['path'] + ".orig")
                        try:
                            self.client.move(disk['path'],
                                             disk['path'] + ".orig")
                        except:
                            pass
                    else:
                        logging.error("remove " + disk['path'])
                    logging.error("upload " + local['path'])
                    self.client.upload_dir_or_file(local['path'], disk['path'])

        elif local['type'] == disk['type'] == "dir":
            for x in local['items']:
                for y in disk['items']:
                    if x['name'] == y['name'] and x['type'] == y['type']:
                        self._sync_local_priority(x, y, rm_exists, save_orig)
                        break
                    elif x['name'] == y['name'] and not x['type'] == y['type']:
                        logging.error("upload " + x['path'])
                        self.client.upload_dir_or_file(x['path'], y['type'],
                                                       rm_exist=True)
                        break
                else:
                    logging.error("upload " + x['path'])
                    self.client.upload_dir_or_file(x['path'],
                                                   disk['path'] + "/" + x[
                                                       'name'], False)

            if rm_exists and not save_orig:
                for x in disk['items']:
                    for y in local['items']:
                        if x['name'] == y['name'] and x['type'] == y['type']:
                            break
                    else:
                        logging.error("remove " + x['path'])
                        self.client.disk.remove_folder_or_file(x['path'])

            elif rm_exists and save_orig:
                for x in disk['items']:
                    for y in local['items']:
                        if x['name'] == y['name'] and x['type'] == y[
                            'type']:
                            break
                    else:
                        if x['path'][-5:] != ".orig":
                            self.client.move(x['path'], x['path'] + ".orig")

    def sync_disk_priority(self, rm_exists=True, save_orig=False):
        self._sync_disk_priority(self.local, self.disk, rm_exists, save_orig)

    def _sync_disk_priority(self, local, disk, rm_exists, save_orig):
        if local['type'] == disk['type'] == "file" and local['name'] == disk[
            'name']:
            if local['md5'] != disk['md5']:
                if save_orig:
                    logging.error( "move " + local['path'] + " to " +
                        local['path'] + ".orig")
                    shutil.move(local['path'], local['path'] + ".orig")

                logging.error("download " + local['path'])
                self.client.download_dir_or_file(local['path'],
                                                 disk['path'], False, True)

        elif local['type'] == disk['type'] == "dir":
            for x in disk['items']:
                for y in local['items']:
                    if x['name'] == y['name'] and x['type'] == y['type']:
                        self._sync_disk_priority(y, x, rm_exists, save_orig)
                        break
                    elif x['name'] == y['name'] and not x['type'] == y['type']:
                        self.client.download_dir_or_file(x['path'], y['path'],
                                                         False, rm_exist=True)
                        break
                else:
                    logging.error("download " + x['path'])
                    self.client.download_dir_or_file(x['path'], os.path.join(
                        local['path'], x['name']), False, rm_exist=True)

            if rm_exists and not save_orig:
                for x in local['items']:
                    for y in disk['items']:
                        if x['name'] == y['name']:
                            break
                    else:
                        if x['name'] not in self.exception_files:
                            logging.error("remove " + x['path'])
                            if os.path.isdir(x['path']):
                                shutil.rmtree(x['path'])
                            else:
                                os.remove(x['path'])

            elif rm_exists and save_orig:
                for x in local['items']:
                    for y in disk['items']:
                        if x['name'] == y['name']:
                            break
                    else:
                        if x['path'][-5:] != ".orig":
                            logging.error( "move " + x['path'] + " to " + x[
                                    'path'] + ".orig")
                            shutil.move(x['path'], x['path'] + ".orig")
