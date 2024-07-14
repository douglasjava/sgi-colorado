from database_manager import DatabaseManager


def main():
    db_manager = DatabaseManager()
    csv_file = 'base.csv'  # Nome do arquivo CSV

    # Insere os registros do arquivo CSV na tabela `nomes`
    db_manager.insert_from_csv(csv_file)
    print("Registros inseridos com sucesso!")


if __name__ == "__main__":
    main()