import os

from b2sdk.v2 import B2Api
from b2sdk.v2 import InMemoryAccountInfo
from io import BytesIO


class B2Client:
    def __init__(self,
                 application_key_id=os.getenv('B2_KEY_ID'),
                 application_key=os.getenv('B2_KEY'),
                 bucket_name=os.getenv('B2_BUCKET')
                 ):
        self.api = self._init_api(application_key_id, application_key)
        self.bucket = self.api.get_bucket_by_name(bucket_name)

    def _init_api(self, application_key_id, application_key):
        account_info = InMemoryAccountInfo()
        api = B2Api(account_info)
        api.authorize_account("production", application_key_id, application_key)
        return api

    def upload_file(self, local_path, remote_path=None):
        if not remote_path:
            remote_path = os.path.basename(local_path)
        self.bucket.upload_local_file(local_path, remote_path)

    def download_file(self, remote_path, local_path=None):
        if not local_path:
            local_path = os.path.basename(remote_path)
        file = self.bucket.download_file_by_name(remote_path)
        with open(local_path, 'wb') as f:
            file.save(f)

    def read_file(self, remote_path) -> BytesIO:
        file = self.bucket.get_file_info_by_name(remote_path)
        f = BytesIO()
        downloaded = self.bucket.download_file_by_id(file.id_)
        downloaded.save(f)
        f.seek(0)
        return f

    def delete_file(self, remote_path):
        file = self.bucket.get_file_info_by_name(remote_path)
        file_version = file.id_
        self.bucket.delete_file_version(file_version, remote_path)
