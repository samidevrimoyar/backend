import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

load_dotenv()

class MinIOUploader:
    def __init__(self):
        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False
        )
        self.bucket_name = "dictionary-images"

    def ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file_path: str, file_content: bytes) -> str:
        self.ensure_bucket_exists()

        # Benzersiz dosya adı oluştur
        file_ext = os.path.splitext(file_path)[1]
        object_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"

        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_content,
                length=len(file_content)
            return f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            print(f"MinIO Error: {e}")
            raise