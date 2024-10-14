import boto3
import sqlite3
import os
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from atlassian import Confluence

class StorageConnector:
    def connect(self):
        raise NotImplementedError("Connect method not implemented")

    def read(self, path):
        raise NotImplementedError("Read method not implemented")

    def write(self, path, data):
        raise NotImplementedError("Write method not implemented")

class LocalStorageConnector(StorageConnector):
    def connect(self):
        print("Local storage does not require a connection setup.")

    def read(self, path):
        with open(path, 'r') as file:
            return file.read()

    def write(self, path, data):
        with open(path, 'w') as file:
            file.write(data)

class SQLStorageConnector(StorageConnector):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)

    def read(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def write(self, query, data):
        cursor = self.connection.cursor()
        cursor.execute(query, data)
        self.connection.commit()

class S3StorageConnector(StorageConnector):
    def __init__(self, aws_access_key, aws_secret_key, bucket_name):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.bucket_name = bucket_name
        self.s3_client = None

    def connect(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

    def read(self, path):
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=path)
        return obj['Body'].read().decode('utf-8')

    def write(self, path, data):
        self.s3_client.put_object(Bucket=self.bucket_name, Key=path, Body=data)

class SharePointConnector(StorageConnector):
    def __init__(self, site_url, client_id, client_secret):
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.ctx = None

    def connect(self):
        ctx_auth = AuthenticationContext(self.site_url)
        if ctx_auth.acquire_token_for_app(self.client_id, self.client_secret):
            self.ctx = ClientContext(self.site_url, ctx_auth)
        else:
            raise Exception("Authentication failed")

    def read(self, path):
        file = self.ctx.web.get_file_by_server_relative_path(path).execute_query()
        with open('downloaded_file', 'wb') as local_file:
            file.download(local_file).execute_query()
        with open('downloaded_file', 'r') as local_file:
            return local_file.read()

    def write(self, path, data):
        target_folder = self.ctx.web.get_folder_by_server_relative_url(path)
        name = os.path.basename(path)
        with open(name, 'w') as file:
            file.write(data)
        with open(name, 'rb') as file:
            target_folder.upload_file(name, file.read()).execute_query()

class ConfluenceConnector(StorageConnector):
    def __init__(self, url, username, api_token):
        self.url = url
        self.username = username
        self.api_token = api_token
        self.confluence = None

    def connect(self):
        self.confluence = Confluence(
            url=self.url,
            username=self.username,
            password=self.api_token
        )

    def read(self, page_id):
        return self.confluence.get_page_by_id(page_id, expand='body.storage')['body']['storage']['value']

    def write(self, space_key, title, content):
        self.confluence.create_page(space=space_key, title=title, body=content)