from src import MinioConnector

def main() -> None:
    connector = MinioConnector()
    try:
        client = connector.connect()
    except ConnectionError as exc:
        print(f"Falha ao conectar ao MinIO: {exc}")
        return

    print("Cliente MinIO pronto para uso.")


if __name__ == "__main__":
    main()