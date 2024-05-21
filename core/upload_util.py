import os
from core.oss_tool import OSS_Tool
entry_point = os.getenv('ENTRY_POINT')
entry_point_upload = os.getenv('ENTRY_POINT_UPLOAD')
access_key_id = os.getenv('ACCESS_KEY_ID')
access_key_secret = os.getenv('ACCESS_KEY_SECRET')
bucket_name = os.getenv('BUCKET_NAME')
TEMPLATE_HOME = os.getenv('TEMPLATE_HOME')
DOWNLOAD_OSS_TOOL = OSS_Tool(entry_point, access_key_id, access_key_secret, bucket_name)
UPLOAD_OSS_TOOL = OSS_Tool(entry_point_upload, access_key_id, access_key_secret, bucket_name)