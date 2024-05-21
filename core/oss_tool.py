#coding=utf-8

import json
import os
import oss2
import cv2
import numpy as np
from itertools import islice


import logging
logging.basicConfig(level=logging.INFO,
          format='%(asctime)s|%(levelname)s|Uploader|%(message)s',
          datefmt='%a, %d %b %Y %H:%M:%S')
logger = logging.getLogger(__name__)


class OSS_Tool():
    def __init__(self, entry_point, access_key_id, access_key_secret, bucket_name):
        self.entry_point = entry_point
        self.bucket_name = bucket_name
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.entry_point, self.bucket_name)

    def download_to_dir(self, bucket_path="", download_local_save_prefix="./"):
        next_key_marker = None
        next_versionid_marker = None
        while True:
            result = self.bucket.list_object_versions(prefix=bucket_path, key_marker=next_key_marker,
                                                 versionid_marker=next_versionid_marker)

            for version_info in result.versions:
                fname = version_info.key.split(bucket_path)[-1]
                dd = "/".join(fname.split('/')[:-1])
                ff = fname.split('/')[-1]
                if len(ff)==0: continue
                os.makedirs(os.path.join(download_local_save_prefix, dd), exist_ok=True)
                self.bucket.get_object_to_file(version_info.key, os.path.join(download_local_save_prefix, dd, ff))

            is_truncated = result.is_truncated

            if is_truncated:
                next_key_marker = result.next_key_marker
                next_versionid_marker = result.next_versionid_marker
            else:
                break
    def download_to_file(self, oss_path, local_path):
        self.bucket.get_object_to_file(oss_path, local_path)

    def get_object_stream(self, object_path):
        '''
        bucket.get_object的返回值是一个类文件对象（File-Like Object），同时也是一个可迭代对象（Iterable）。
        :param object_path:
        :return:
        '''

        object_stream = self.bucket.get_object(object_path)
        return object_stream


    def get_txt(self, oss_path):
        object_stream = self.get_object_stream(oss_path.replace("oss://" + self.bucket_name + "/", ""))
        data = str(object_stream.read(), encoding="utf-8").split()
        return data

    def get_json(self, oss_path):
        object_stream = self.get_object_stream(oss_path.replace("oss://" + self.bucket_name + "/", ""))
        data = json.loads(str(object_stream.read(), encoding="utf-8"))

        return data

    def get_img(self, oss_path):
        object_stream = self.get_object_stream(oss_path.replace("oss://" + self.bucket_name + "/", ""))
        img = cv2.imdecode(np.asarray(bytearray(object_stream.read()), dtype="uint8"), cv2.IMREAD_COLOR)
        return img

    # def upload_data(self, data, filename, uid, taskid):
    #     try:
    #       oss_path = self.oss_prefix + "/" + str(uid) + "/task/" + str(taskid) + "/" + filename
    #       self.bucket.put_object(oss_path, data)
    #     except Exception as e:
    #       logger.error("upload data error: {}".format(e))

    def upload_file(self, file_path, oss_path):
        try:
          with open(file_path, 'rb') as file:
            self.bucket.put_object(oss_path, file.read())
        except Exception as e:
          logger.error("upload file error: {}".format(e))

    def sign_url(self, file_key):
        url = self.bucket.sign_url('GET', file_key, 60*60*48)
        return url

if __name__ == '__main__':
    pass
