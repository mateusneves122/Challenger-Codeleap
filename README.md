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

* Docker installed
* Docker Compose installed

### Steps to Run

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <your-repository-url>
    cd <project-folder-name>
    ```

2.  **Create the `.env` file**:
    In the project root (same directory as `docker-compose.yaml`), create a file named `.env` with the following environment variables. Replace the values as needed:
    If you cloned the repository, there might be an `EXAMPLE.env` file. Copy this file to `.env` and then change the values with your chosen data.
    ```env
    # Database Configuration
    DB_USER=admin
    DB_PASSWORD=admin
    DB_NAME=codeleap
    DB_HOST=db
    DB_PORT=5432
    ```
    * `DB_HOST` should be `db`, which is the name of the database service in `docker-compose.yaml`.

3.  **Build and Start the Containers**:
    In the terminal, at the project root, run:
    ```bash
    docker-compose up -d --build
    ```
    * The `--build` command rebuilds the application image if there are changes to the `Dockerfile` or source code.

    * **Note about `init_tables.sql`**: The `docker-compose.yaml` references a script `./scripts/init_tables.sql`. This script already creates the tables, without the need for migrations.


4.  **Access the Application**:
    The API will be available at `http://localhost:8000`.
    To access the API documentation (generated with ReDoc), visit:
    `http://localhost:8000/api/schema/redoc/`

### Stopping the Application

* To remove the containers and the created network:
    ```bash
    docker-compose down
    ```
* To also remove persistent data volumes (including database data):
    ```bash
    docker-compose down -v
    ```