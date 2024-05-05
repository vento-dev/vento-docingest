from google.cloud import storage
from google.auth import app_engine
# from oauth2client.service_account import ServiceAccountCredentials
import os

class GCloudStorage(object):

    def __init__(self):
        my_dir = os.listdir("config")
        self.client = storage.Client.from_service_account_json("config/vento-document-ingestion-1-decb6fa62638.json")
        
    def upload_to_bucket(self, blob_name, path_to_file, bucket_name):
        """ Upload data to a bucket"""
        
        # Explicitly use service account credentials by specifying the private key
        # file.
        # storage_client = storage.Client.from_service_account_json(
        #    'creds.json')

        #print(buckets = list(self.client.list_buckets())

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file)
        
        #returns a public url
        return blob.public_url


'''
credentials_dict = {
    'type' : 'service_account',
    'client_id': os.environ['BACKUP_CLIENT_ID'],
    'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
    'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
    'private_key': os.environ['BACKUP_PRIVATE_KEY'],
}
'''

