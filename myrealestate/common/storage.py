from django.conf import settings
from django.core.cache import cache
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StorageHealthCheck:
    """Storage health monitoring system for MinIO/S3"""
    
    CACHE_KEY = 'storage_health_status'
    CACHE_TIMESTAMP_KEY = 'storage_health_last_check'
    CACHE_DURATION = 300  # 5 minutes
    
    @classmethod
    def get_storage_client(cls):
        """Create boto3 client for MinIO/S3"""
        try:
            return boto3.client('s3',
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=boto3.session.Config(signature_version='s3v4'),
                region_name='us-east-1'  # Required for MinIO
            )
        except Exception as e:
            logger.error(f"Failed to create storage client: {str(e)}")
            return None

    @classmethod
    def perform_health_check(cls, force_check=False):
        """
        Perform health check on storage system
        Returns tuple (is_healthy: bool, timestamp: datetime)
        """
        # Check cache first unless force check is requested
        if not force_check:
            cached_status = cache.get(cls.CACHE_KEY)
            cached_timestamp = cache.get(cls.CACHE_TIMESTAMP_KEY)
            if cached_status is not None and cached_timestamp is not None:
                return cached_status, cached_timestamp

        is_healthy = False
        timestamp = datetime.now()
        test_key = '_health_check_test'

        try:
            client = cls.get_storage_client()
            if client is None:
                raise Exception("Could not initialize storage client")

            # Test 1: Check if bucket exists
            client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)

            # Test 2: Try to write a test file
            client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key,
                Body='health check'
            )

            # Test 3: Try to read the test file
            client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key
            )

            # Test 4: Try to delete the test file
            client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key
            )

            is_healthy = True
            logger.info("Storage health check passed successfully")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Storage health check failed with error {error_code}: {str(e)}")
        except Exception as e:
            logger.error(f"Storage health check failed: {str(e)}")

        # Cache the results
        cache.set(cls.CACHE_KEY, is_healthy, cls.CACHE_DURATION)
        cache.set(cls.CACHE_TIMESTAMP_KEY, timestamp, cls.CACHE_DURATION)

        return is_healthy, timestamp

    @classmethod
    def get_status(cls):
        """Get current storage status"""
        return cls.perform_health_check(force_check=False)