## Projeto MinIO

Projeto para a cadeira de Banco De Dados
Slide : https://docs.google.com/presentation/d/1K0w-D7NTC3NwqS6ETHfKkeTsRP0FogI_q-sxb-dGAJs/edit?usp=sharing

### Requisitos
- Docker instalado **e rodando**.
- Python >= 3 instalado.
- Ports liberadas: `9000` (API MinIO) e `9001` (Console Web).

### Subir o MinIO com Docker Compose
1) Na raiz do projeto:
	```bash
	docker compose up -d
	```
2) Console Web: http://localhost:9001 (usuário `admin`, senha `password123`).
3) API: http://localhost:9000.

### Ambiente Python (opcional, mas recomendado)
```bash
# criar venv
python -m venv .venv
# ativar (Windows PowerShell)
./.venv/Scripts/Activate.ps1
# instalar dependências
pip install -r requirements.txt
```

### Classe utilitária (`src/MinIO.py`)
`MinioConnector` oferece:
- `connect()`
- `create_bucket(bucket_name)`
- `upload_file(bucket_name, file_path, object_name=None)`
- `list_buckets()`
- `list_files(bucket_name)`
- `download_file(bucket_name, object_name, file_path)`
- `generate_presigned_url(bucket_name, object_name, expiration_hours=1)`
- `get_file_metadata(bucket_name, object_name)`
- `delete_file(bucket_name, object_name)`
- `delete_bucket(bucket_name)`

Variáveis de ambiente suportadas (opcionais): `MINIO_ENDPOINT` (padrão `localhost:9000`), `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_SECURE` (`true|false`).

### Passo a passo do `main.py`
```python
connector = MinioConnector()                      # cria o helper configurável via env
connector.connect()                               # abre conexão e testa ping ao servidor

bucket_name = "grupo-10"                         # nome do bucket (use hifens em vez de espaços)
file_path = "./Grupo 10/Documento_grupo_10.pdf"   # caminho local do arquivo para upload
object_name = None                                # opcional: nome do objeto no bucket

connector.create_bucket(bucket_name)              # cria o bucket se não existir
connector.upload_file(bucket_name, file_path, object_name)  # envia o arquivo
connector.list_buckets()                          # lista todos os buckets
connector.list_files(bucket_name)                 # lista arquivos do bucket
connector.download_file(bucket_name, "Documento_grupo_10.pdf", "./meu-arquivo-baixado.pdf") # download
connector.generate_presigned_url(bucket_name, "Documento_grupo_10.pdf", expiration_hours=1) # url temporaria
connector.get_file_metadata(bucket_name, "Documento_grupo_10.pdf") # metadados
connector.delete_file(bucket_name, "Documento_grupo_10.pdf")  # deleta arquivo
connector.delete_bucket(bucket_name)  # deleta bucket vazio
```

### Acesso rápido via browser
- Console: http://localhost:9001 (admin/password123).
- Buckets e objetos podem ser criados/listados/baixados pelo console.