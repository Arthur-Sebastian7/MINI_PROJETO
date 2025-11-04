# chat/database.py
from pymongo import MongoClient

class MongoConnection:
    """Gerencia a conexão com o MongoDB"""

    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="Chat"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.client.server_info()  # Testa conexão
            print("Conectado ao MongoDB!")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            return False

    def get_collection(self, name):
        if self.db is None:
            raise Exception("Banco de dados não conectado.")
        return self.db[name]

    def close(self):
        if self.client:
            self.client.close()
            print("Conexão encerrada.")