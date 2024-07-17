# Nome do Projeto

Descrição breve sobre o que o seu projeto faz.

## Tabela de Conteúdos

- [Instalação](#instalação)
- [Uso](#uso)

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/douglasjava/sgi-colorado
    ```
2. Navegue até o diretório do projeto:
    ```bash
    cd sgi-colorado
    ```
3. (Opcional) Crie e ative um ambiente virtual:
    ```bash
    python -m venv env
    source env/bin/activate  # No Windows use `env\Scripts\activate`
    ```
4. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Estrutura

sgi-colorado
├── static/
│   ├── style.css
├── template/
│   ├── chamada.html
│   ├── dashboard.html
│   ├── index.html
│   ├── pesquisa.html
├── .gitignore
├── .slugignore
├── app.py
├── base.csv
├── create_insert_tables.py
├── database.db
├── database_manager.py
├── environment.yml
├── Procfile
├── requirements.txt
├── runtime.txt
├── settings.py
└── README.md
