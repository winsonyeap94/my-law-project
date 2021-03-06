"""
CloudFileConnector script includes reading and writing to Azure Blob Storage and AWS S3 Bucket.
"""
import os
import boto3
import pandas as pd
from conf import Logger
from azure.storage.blob import BlobServiceClient
from src.data_connectors.PandasFileConnector import PandasFileConnector
from io import StringIO

class AzureBlobStorage:

    def __init__(self, azure_storage_conn_string):
        self._logger = Logger().logger
        self.blob_service_client = BlobServiceClient.from_connection_string(azure_storage_conn_string)

    def load(self, container_name, blob_name=''):
        """
        Load all blob files in a container name given to local path and append to a dataframe, works only for blob files with same file format
        
        3 types of credentials:
        1) Azure Active Directory (AAD)
        2) Shared Access Signature (SAS) token
        3) Storage Account Shared Key (currently coded)
        
        Args:
            container_name ([str]): [container name]
            blob_name ([str]): [blob name aka file name, if blob name is not given, download all blobs inside the container]
        """
        try:
            self._logger.debug("[AzureBlobStorage] Load initiated.")
            compiled_azure_df = pd.DataFrame()
            container_client = self.blob_service_client.get_container_client(container_name)
            my_blobs = container_client.list_blobs(blob_name)
            if not list(my_blobs):
                raise Exception(
                    f"[AzureBlobStorage] Failed to download blob files from Azure Blob Storage | Error: Blob name has typos."
                )
            my_blobs = container_client.list_blobs(blob_name) # reloading the blob
            for blob in my_blobs:
                self._logger.debug(f"[AzureBlobStorage] Loading blob {blob.name}.")
                downloaded_blob = container_client.download_blob(blob)
                azure_df = PandasFileConnector.load(StringIO(downloaded_blob.content_as_text()), file_type=PandasFileConnector._check_filetype(blob.name))
                compiled_azure_df = pd.concat([compiled_azure_df, azure_df], axis=0).reset_index(drop=True)
            return compiled_azure_df

        except Exception as error:
            self._logger.exception(
                f"[AzureBlobStorage] Failed to download blob files from Azure Blob Storage | Error: {error}"
            )

    def download(self, local_filepath_to_download, container_name, blob_name=''):
        """
        Download all blob files in a container name given to local path, need to use PandasFileConnector to load
        the file to model depending on file format 
        
        3 types of credentials:
        1) Azure Active Directory (AAD)
        2) Shared Access Signature (SAS) token
        3) Storage Account Shared Key (currently coded)
        
        Args:
            local_filepath_to_download ([str]): [file path to load the file to]
            container_name ([str]): [container name]
            blob_name ([str]): [blob name aka file name, if blob name is not given, download all blobs inside the container. Default = none]
        """

        try:
            self._logger.debug("[AzureBlobStorage] Download initiated.")
            container_client = self.blob_service_client.get_container_client(container_name)
            my_blobs = container_client.list_blobs(blob_name)
            if not list(my_blobs):
                raise Exception(
                    f"[AzureBlobStorage] Failed to download blob files from Azure Blob Storage | Error: Blob name has typos."
                )
            my_blobs = container_client.list_blobs(blob_name) # reloading the blob
            for blob in my_blobs:
                bytes = container_client.get_blob_client(blob).download_blob().readall()
                download_file_path = os.path.join(local_filepath_to_download, blob.name)
                with open(download_file_path, "wb") as file:
                    file.write(bytes)
            self._logger.debug("[AzureBlobStorage] Download complete.")

        except Exception as error:
            self._logger.exception(
                f"[AzureBlobStorage] Failed to download blob files from Azure Blob Storage | Error: {error}"
            )

    def save(self, local_file_to_upload, container_name, blob_name):
        """
        Save a single file from local path to azure blob storage by creating new container (if not exists) and
        new blob name.

        Args:
            local_file_to_upload ([str]): [file path to save or push the file to Azure Blob Storage]
            container_name ([str]): [container name]
            blob_name ([str]): [blob name aka file name]
        """

        try:

            # Instantiate a new ContainerClient
            container_client = self.blob_service_client.get_container_client(container_name)
            # Pass if container exists
            if not (container_client.exists()):
                # Create new Container in the service
                container_client.create_container()
            blob_client = container_client.get_blob_client(blob_name)
            # Upload content to block blob
            with open(local_file_to_upload, "rb") as data:
                    blob_client.upload_blob(data, blob_type="BlockBlob")

        except Exception as error:
            self._logger.exception(
                f"[AzureBlobStorage] Failed to save file to Azure Blob Storage | Error: {error}"
            )


class AWSS3Bucket:

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str):
        self._logger = Logger().logger
        self.s3_resource = boto3.resource('s3',
                                          aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)

    def load(self, bucket_name, filepath_aws):
        """
        Load and append files from filepath_aws as a pd.DataFrame using PandasFileConnector. Works only for all files withs same file format type.

        Args:
            bucket_name ([str]): [aws bucket name]
            filepath_aws ([st]): [filepath in aws to download file from]
        """

        try:
            self._logger.debug("[AWSS3Bucket] Load initiated.")
            compiled_aws_df = pd.DataFrame()
            for obj in self.s3_resource.Bucket(bucket_name).objects.filter(Prefix=filepath_aws):
                if obj.key.endswith('/'):
                    continue
                self._logger.debug(f"[AWSS3Bucket] Loading file {obj.key}.")
                aws_df = PandasFileConnector.load(obj.get()['Body'],
                                                  file_type=PandasFileConnector._check_filetype(obj.key))
                compiled_aws_df = pd.concat([compiled_aws_df, aws_df], axis=0)
            self._logger.debug("[AWSS3Bucket] Load complete.")
            return compiled_aws_df

        except Exception as error:
            self._logger.exception(
                f"[AWSS3Bucket] Failed to load file from AWS S3 Storage | Error: {error}"
            )

    def download(self, bucket_name, filepath_aws, local_dir='data/01_raw'):
        """
        Load file from filepath_aws given and save a copy to local filepath, need to use PandasFileConnector to load
        the file to model depending on file format

        Args:
            bucket_name ([str]): [aws bucket name]
            filepath_aws ([st]): [filepath in aws to download file from]
            filepath_local ([str]): [filepath in local to save the file to]
        """

        try:
            self._logger.debug("[AWSS3Bucket] Download initiated.")
            for obj in self.s3_resource.Bucket(bucket_name).objects.filter(Prefix=filepath_aws):
                target = os.path.join(local_dir, os.path.relpath(obj.key, filepath_aws))
                if not os.path.exists(os.path.dirname(target)):
                    os.makedirs(os.path.dirname(target))
                if obj.key[-1] == '/':
                    continue
                self.s3_resource.Bucket(bucket_name).download_file(obj.key, target)
            self._logger.debug("[AWSS3Bucket] Download complete.")
        except Exception as error:
            self._logger.exception(
                f"[AWSS3Bucket] Failed to download file from AWS S3 Storage | Error: {error}"
            )
    
    def save(self, bucket_name, filename_inAWS, filepath_local):
        """
        Args:
            bucket_name ([str]): [bucket name]
            filename_inAWS ([str]): [filename to be saved as in AWS S3 Bucket]
            filepath_local ([str]): [filepath in local that host the file to be uploaded to AWS S3 bucket]
        """

        try:
            self._logger.debug("[AWSS3Bucket] Save initiated.")
            session = boto3.session.Session()
            current_region = session.region_name

            # create a bucket with the bucket name given, it will either create or just return the existing bucket
            self.s3_resource.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': current_region}
            )
            self.s3_resource.Object(bucket_name, filepath_local).upload_file(Filename=filename_inAWS)
            self._logger.debug("[AWSS3Bucket] Save complete.")
        except Exception as error:
            self._logger.exception(
                f"[AWSS3Bucket] Failed to save file to AWS S3 Storage | Error: {error}"
            )