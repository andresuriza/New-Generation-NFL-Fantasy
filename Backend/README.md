## Se debe crear un .env para conectar la base de datos de PostgreSQL en su PC.

Para esto crear un archivo `.env` en este directorio y agregar la linea:

    DATABASE_URL="postgresql://<usuario>:<password>@localhost:5432/XNFL-Fantasy"

Reemplazar usuario por su usuario (usualmente postgres) y contraseña por la que se utiliza.


## Para restaurar base de datos de script usar:

    psql -h localhost -p 5432 -U postgres -f full_db_creation_script.sql