
from sqlalchemy import create_engine,text



db_config = {
    "dbname": "gpon",
    "user": "gpon",
    "password": "Cantv2021",
    "host": "200.44.45.152",
    "port": 5432
}

engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

