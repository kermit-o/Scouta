import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import zipfile
import io
from typing import Dict, List, Optional
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.config import Config
import logging

logger = logging.getLogger(__name__)

class FileStorageService:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "forge-saas-projects")
        self.init_s3_client()

    def init_s3_client(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3 client initialized")
        except (NoCredentialsError, ClientError):
            logger.warning("S3 credentials not available, using local storage")
            self.s3_client = None

    def upload_project_files(self, project_id: str, files: Dict[str, str]) -> bool:
        try:
            if self.s3_client:
                for file_path, content in files.items():
                    s3_key = f"projects/{project_id}/{file_path}"
                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=s3_key,
                        Body=content.encode('utf-8'),
                        ContentType=self._get_content_type(file_path)
                    )
                logger.info(f"Uploaded {len(files)} files to S3")
            else:
                os.makedirs(f"local_storage/projects/{project_id}", exist_ok=True)
                for file_path, content in files.items():
                    full_path = f"local_storage/projects/{project_id}/{file_path}"
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                logger.info(f"Saved {len(files)} files locally")
            return True
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
            return False

    def _get_content_type(self, file_path: str) -> str:
        extension = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.md': 'text/markdown'
        }
        return content_types.get(extension, 'application/octet-stream')

# Global instance
file_storage_service = FileStorageService()
from backend.app.core.config.paths import setup_paths; setup_paths()
from backend.app.core.config.paths import setup_paths; setup_paths()
