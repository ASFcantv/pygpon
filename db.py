import psycopg2
# Recomendado: https://parzibyte.me/blog/2018/12/20/args-kwargs-python/
try:
    credenciales = {
        "dbname": "gpon",
        "user": "gpon",
        "password": "Cantv2021",
        "host": "200.44.45.148",
        "port": 5432
    }
    conexion = psycopg2.connect(**credenciales)
    
except psycopg2.Error as e:
    print("Ocurrio un error al conectar a PostgreSQL: ", e)
    conexion = psycopg2.connect(**credenciales)