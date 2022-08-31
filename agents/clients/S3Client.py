import os
import boto3
from botocore.exceptions import ClientError
from loguru import logger

class S3Client:
    def __init__(self) -> None:
        self.bucket = 'dataperf'

    def upload_file(self, file_name, object_name=None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, self.bucket, object_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True