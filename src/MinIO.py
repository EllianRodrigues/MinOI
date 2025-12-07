import os
from datetime import timedelta
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
        self.client: Minio | None = None

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
            self.client = client
            return client
        except S3Error as exc:
            raise ConnectionError("Erro de protocolo S3; revise as chaves de acesso.") from exc
        except Exception as exc:
            raise ConnectionError("Erro ao conectar; verifique se o servidor MinIO esta ativo.") from exc

    def create_bucket(self, bucket_name: str) -> None:
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")

        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' criado.")
            else:
                print(f"Bucket '{bucket_name}' ja existe; seguindo em frente.")
        except S3Error as exc:
            raise ConnectionError("Falha ao criar bucket no MinIO.") from exc

    def upload_file(self, bucket_name: str, file_path: str, object_name: str | None = None) -> str:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not file_path:
            raise ValueError("O caminho do arquivo nao pode ser vazio.")

        object_key = object_name or os.path.basename(file_path)

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            result = self.client.fput_object(bucket_name, object_key, file_path)
            print(f"Arquivo enviado para bucket '{bucket_name}' como '{object_key}'.")
            return result.object_name
        except S3Error as exc:
            raise ConnectionError("Falha ao enviar arquivo ao MinIO.") from exc

    def list_buckets(self) -> list[str]:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")

        try:
            buckets_response = self.client.list_buckets()
            bucket_list = [bucket.name for bucket in buckets_response]
            if bucket_list:
                print(f"Buckets encontrados: {', '.join(bucket_list)}")
            else:
                print("Nenhum bucket encontrado.")
            return bucket_list
        except S3Error as exc:
            raise ConnectionError("Falha ao listar buckets no MinIO.") from exc

    def list_files(self, bucket_name: str) -> list[str]:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            objects_response = self.client.list_objects(bucket_name)
            file_list = [obj.object_name for obj in objects_response]
            if file_list:
                print(f"Arquivos no bucket '{bucket_name}': {', '.join(file_list)}")
            else:
                print(f"Bucket '{bucket_name}' esta vazio.")
            return file_list
        except S3Error as exc:
            raise ConnectionError(f"Falha ao listar arquivos do bucket '{bucket_name}'.") from exc

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> str:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not object_name:
            raise ValueError("O nome do arquivo nao pode ser vazio.")
        if not file_path:
            raise ValueError("O caminho de destino nao pode ser vazio.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            self.client.fget_object(bucket_name, object_name, file_path)
            print(f"Arquivo '{object_name}' baixado de '{bucket_name}' para '{file_path}'.")
            return file_path
        except S3Error as exc:
            raise ConnectionError(f"Falha ao baixar arquivo '{object_name}' do bucket '{bucket_name}'.") from exc

    def generate_presigned_url(self, bucket_name: str, object_name: str, expiration_hours: int = 1) -> str:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not object_name:
            raise ValueError("O nome do arquivo nao pode ser vazio.")
        if expiration_hours <= 0:
            raise ValueError("O tempo de expiracao deve ser maior que zero.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            url = self.client.get_presigned_url(
                "GET",
                bucket_name,
                object_name,
                expires=timedelta(hours=expiration_hours)
            )
            print(f"Link temporario gerado para '{object_name}' (expira em {expiration_hours}h):")
            print(f"URL: {url}")
            return url
        except S3Error as exc:
            raise ConnectionError(f"Falha ao gerar link temporario para '{object_name}'.") from exc

    def get_file_metadata(self, bucket_name: str, object_name: str) -> dict:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not object_name:
            raise ValueError("O nome do arquivo nao pode ser vazio.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            stat_result = self.client.stat_object(bucket_name, object_name)
            metadata = {
                "nome": stat_result.object_name,
                "tamanho_bytes": stat_result.size,
                "data_modificacao": stat_result.last_modified,
                "tipo_conteudo": stat_result.content_type,
                "etag": stat_result.etag,
                "metadados_customizados": stat_result.metadata if stat_result.metadata else {}
            }
            print(f"Metadados de '{object_name}':")
            for chave, valor in metadata.items():
                print(f"  {chave}: {valor}")
            return metadata
        except S3Error as exc:
            raise ConnectionError(f"Falha ao obter metadados de '{object_name}'.") from exc

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")
        if not object_name:
            raise ValueError("O nome do arquivo nao pode ser vazio.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            self.client.remove_object(bucket_name, object_name)
            print(f"Arquivo '{object_name}' deletado do bucket '{bucket_name}'.")
        except S3Error as exc:
            raise ConnectionError(f"Falha ao deletar arquivo '{object_name}' do bucket '{bucket_name}'.") from exc

    def delete_bucket(self, bucket_name: str) -> None:
        if not self.client:
            raise RuntimeError("Conecte primeiro chamando connect().")
        if not bucket_name:
            raise ValueError("O nome do bucket nao pode ser vazio.")

        try:
            if not self.client.bucket_exists(bucket_name):
                raise FileNotFoundError(f"Bucket '{bucket_name}' nao existe.")

            self.client.remove_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' deletado com sucesso.")
        except S3Error as exc:
            raise ConnectionError(f"Falha ao deletar bucket '{bucket_name}'.") from exc
