from database_manager import DatabaseManager, insert_from_csv


def main():
    db_manager = DatabaseManager()

    csv_file = '../data/base.csv'  # Nome do arquivo CSV

    # Insere os registros do arquivo CSV na tabela `nomes`
    insert_from_csv(csv_file)
    print("Registros inseridos com sucesso!")


if __name__ == "__main__":
    main()
