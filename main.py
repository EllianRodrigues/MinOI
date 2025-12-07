from src import MinioConnector

def main() -> None:
    connector = MinioConnector()
    try:
        connector.connect()
    except ConnectionError as exc:
        print(f"Falha ao conectar ao MinIO: {exc}")
        return
    
    bucket_name = "grupo-10"  
    file_path = "./Grupo 10/Documento_grupo_10.pdf"  
    object_name = None  

    try:
        connector.create_bucket(bucket_name) # cria bucket
        connector.upload_file(bucket_name, file_path, object_name) # upload
        connector.list_buckets() # lista todos os buckets
        connector.list_files(bucket_name) # lista arquivos no bucket
        # connector.download_file(bucket_name, "Documento_grupo_10.pdf", "./meu-arquivo-baixado.pdf") # download
        # connector.generate_presigned_url(bucket_name, "Documento_grupo_10.pdf", expiration_hours=1) # url temporaria
        # connector.get_file_metadata(bucket_name, "Documento_grupo_10.pdf") # metadados
        # connector.delete_file(bucket_name, "Documento_grupo_10.pdf")  # deleta arquivo
        # connector.delete_bucket(bucket_name)  # deleta bucket vazio

    except (ConnectionError, FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Falha ao operar no MinIO: {exc}")
        return

if __name__ == "__main__":
    main()