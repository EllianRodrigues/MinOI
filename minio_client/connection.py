import os
from minio import Minio
from minio.error import S3Error


class MinioConnector:
    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        secure: bool | None = None,
    ) -> None:
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "password123")
        self.secure = (
            secure
            if secure is not None
            else os.getenv("MINIO_SECURE", "false").lower() == "true"
        )

    def connect(self) -> Minio:
        print(f"Tentando conectar ao MinIO em {self.endpoint}...")

        try:
            client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
            client.list_buckets()
            print("Conexao estabelecida com sucesso.")
            return client
        except S3Error as exc:
            raise ConnectionError("Erro de protocolo S3; revise as chaves de acesso.") from exc
        except Exception as exc:
            raise ConnectionError("Erro ao conectar; verifique se o servidor MinIO esta ativo.") from exc
