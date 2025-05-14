# Django Social Network API

This project is an API developed in Django for a simple social network platform. It allows users to register, create posts, and follow other users.

## Data Models and Relationships
The system is built around three main tables: `users`, `posts`, and `follows`. The relationships between them are as follows:

*   **Relationship between `users` and `posts` (One-to-Many):**
    *   A user (from the `users` table) can create multiple posts (records in the `posts` table).
    *   Each post in the `posts` table is associated with a single user through a foreign key that references the `users` table.

*   **Relationship between `users` and `follows` (Many-to-Many, through the `follows` table):**
    *   The `follows` table serves as a junction table to represent who follows whom.
    *   It contains two foreign keys that reference the `users` table: one for the "follower" and another for the "followed" (`following`).
    *   This allows a user to follow multiple other users and also be followed by multiple users.

*In summary:*
*   `users` ⟵ (one) `posts` (many)
*   `users` (follower) ⟵ (one) `follows` (many) ⟶ (one) `users` (followed)

## Custom JWT Authentication

The project implements custom JWT authentication logic through the `CustomJWTAuthentication` class.

This class extends the default behavior of `JWTAuthentication` from `rest_framework_simplejwt` to include an additional check: it prevents the authentication of users who have been "soft-deleted" (i.e., those who have the `deleted_at` field populated in the `users` table). This ensures that only active users can obtain access tokens.

## Scalability Potential

The current project structure, with a clear separation of responsibilities between apps (`user`, `post`, `social`, `auth`) and a well-defined database relationship model, facilitates the expansion of the API with new functionalities.

For example, it would be relatively simple to add:
*   **Comments**: A new `Comment` model could be created, relating to `Post` (a post can have many comments) and `User` (a user can make many comments).
*   **Likes/Reactions**: A `Like` or `Reaction` model could be implemented, connecting `User` to `Post` (or even `Comment`), allowing users to like or react to content.

## How to Run the Project with Docker

The project is configured to run with Docker and Docker Compose.

### Prerequisites

* Docker instalado
* Docker Compose instalado
* Docker installed
* Docker Compose installed

### Steps to Run

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-da-pasta-do-projeto>
    ```

2.  **Crie o arquivo `.env`**:
    Na raiz do projeto (mesmo diretório do `docker-compose.yaml`), crie um arquivo chamado `.env` com as seguintes variáveis de ambiente. Substitua os valores conforme necessário:
    Se você clonou o repositório, pode haver um arquivo `EXAMPLE.env`. Copie este arquivo para `.env` e depois altere os valores com os dados que escolheu.
    ```env
    # Configuração do Banco de Dados
    DB_USER=admin
    DB_PASSWORD=admin
    DB_NAME=codeleap
    DB_HOST=db
    DB_PORT=5432
    ```
    * `DB_HOST` deve ser `db`, que é o nome do serviço do banco de dados no `docker-compose.yaml`.

3.  **Construa e Inicie os Contêineres**:
    No terminal, na raiz do projeto, execute:
    ```bash
    docker-compose up -d --build
    ```
    * O comando `--build` reconstrói a imagem da aplicação se houver mudanças no `Dockerfile` ou no código-fonte.

    * **Nota sobre `init_tables.sql`**: O `docker-compose.yaml` referencia um script `./scripts/init_tables.sql`. Este script já cria as tabelas, sem a necessidade de migrate.


6.  **Acesse a Aplicação**:
    A API estará disponível em `http://localhost:8000`.
    Para acessar a documentação da API (gerada com ReDoc), visite:
    `http://localhost:8000/api/schema/redoc/`

### Parando a Aplicação

* Para remover os contêineres e a rede criada:
    ```bash
    docker-compose down
    ```
* Para remover também os volumes de dados persistentes (incluindo os dados do banco de dados):
    ```bash
    docker-compose down -v
    ```