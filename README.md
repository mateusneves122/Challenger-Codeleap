# API de Rede Social Django

Este projeto é uma API desenvolvida em Django para uma plataforma de rede social simples. Ele permite que usuários se registrem, criem posts e sigam outros usuários.

## Modelos de Dados e Relações
O sistema é construído em torno de três tabelas principais: `users`, `posts`, e `follows`. As relações entre elas são as seguintes:

*   **Relação entre `users` e `posts` (Um-para-Muitos):**
    *   Um usuário (da tabela `users`) pode criar várias postagens (registros na tabela `posts`).
    *   Cada postagem na tabela `posts` está associada a um único usuário através de uma chave estrangeira que referencia a tabela `users`.

*   **Relação entre `users` e `follows` (Muitos-para-Muitos, através da tabela `follows`):**
    *   A tabela `follows` serve como uma tabela de junção para representar quem segue quem.
    *   Ela contém duas chaves estrangeiras que referenciam a tabela `users`: uma para o "seguidor" (`follower`) e outra para o "seguido" (`following`).
    *   Isso permite que um usuário siga múltiplos outros usuários e também seja seguido por múltiplos usuários.

*Resumindo:*
*   `users` ⟵ (um) `posts` (muitos)
*   `users` (seguidor) ⟵ (um) `follows` (muitos) ⟶ (um) `users` (seguido)

## Autenticação JWT Customizada

O projeto implementa uma lógica de autenticação JWT customizada através da classe `CustomJWTAuthentication`.

Esta classe estende o comportamento padrão do `JWTAuthentication` do `rest_framework_simplejwt` para incluir uma verificação adicional: ela impede a autenticação de usuários que foram "soft-deleted" (ou seja, que possuem o campo `deleted_at` preenchido na tabela `users`). Isso garante que apenas usuários ativos possam obter tokens de acesso.

## Potencial de Escalabilidade

A estrutura atual do projeto, com a separação clara de responsabilidades entre os apps (`user`, `post`, `social`, `auth`) e o modelo de relacionamento bem definido no banco de dados, facilita a expansão da API com novas funcionalidades.

Por exemplo, seria relativamente simples adicionar:
*   **Comentários**: Um novo modelo `Comment` poderia ser criado, relacionando-se com `Post` (um post pode ter muitos comentários) e `User` (um usuário pode fazer muitos comentários).
*   **Likes/Reações**: Um modelo `Like` ou `Reaction` poderia ser implementado, conectando `User` a `Post` (ou até mesmo a `Comment`), permitindo que usuários curtam ou reajam a conteúdos.

## Como Executar o Projeto com Docker

O projeto é configurado para rodar com Docker e Docker Compose.

### Pré-requisitos

* Docker instalado
* Docker Compose instalado

### Passos para Execução

1.  **Clone o repositório** (se ainda não o fez):
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
    docker-compose up --build
    ```
    * O comando `--build` reconstrói a imagem da aplicação se houver mudanças no `Dockerfile` ou no código-fonte.

    * **Nota sobre `init_tables.sql`**: O `docker-compose.yaml` referencia um script `./scripts/init_tables.sql`. Este script já cria as tabelas, sem a necessidade de migrate.


6.  **Acesse a Aplicação**:
    A API estará disponível em `http://localhost:8000`.
    Para acessar a documentação da API (gerada com ReDoc), visite:
    `http://localhost:8000/api/schema/redoc/`

### Parando a Aplicação

* Para parar os contêineres, pressione `Ctrl+C` no terminal onde o `docker-compose up` está rodando.
* Para remover os contêineres e a rede criada:
    ```bash
    docker-compose down
    ```
* Para remover também os volumes de dados persistentes (incluindo os dados do banco de dados):
    ```bash
    docker-compose down -v
    ```