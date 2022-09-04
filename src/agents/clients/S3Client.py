import os
from uuid import uuid4
import boto3
from botocore.exceptions import ClientError
from loguru import logger

class S3Client:
    def __init__(self) -> None:
        self.bucket = 'dataperf'

    def upload_file(self, file_name, object_name=None):
        # if object_name is not specified, use a random uuid-4 name
        if object_name is None:
            object_name = str(uuid4())

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, self.bucket, object_name)
        except ClientError as e:
            logger.error(e)
            return False, None
        return True, object_name