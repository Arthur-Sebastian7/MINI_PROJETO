# chat/app.py
from datetime import datetime
from pymongo import DESCENDING
from cryptography.fernet import InvalidToken
from .database import MongoConnection
from .security import encrypt_message, decrypt_message

class ChatApp:
    """Classe principal do chat criptografado"""

    def __init__(self):
        self.mongo = MongoConnection()
        self.current_user = None
        self.users_collection = None
        self.messages_collection = None

    def start(self):
        print("=" * 60)
        print("CHAT DE MENSAGENS CRIPTOGRAFADAS")
        print("=" * 60)

        if not self.mongo.connect():
            print("Não foi possível iniciar a aplicação. Verifique o MongoDB.")
            return

        self.users_collection = self.mongo.get_collection("Users")
        self.messages_collection = self.mongo.get_collection("Messages")

        self.login()

    def login(self):
        while True:
            username = input("\nDigite seu @username (ou 'sair'): ").strip()
            if username.lower() == "sair":
                self.mongo.close()
                return

            if username.startswith("@"):
                username = username[1:]

            if len(username) < 3:
                print("Username muito curto!")
                continue

            self.current_user = username
            user_exists = self.users_collection.find_one({"username": username})
            if not user_exists:
                self.users_collection.insert_one({"username": username, "created_at": datetime.now()})
                print(f"Usuário @{username} registrado!")
            else:
                print(f"Bem-vindo de volta, @{username}!")

            self.menu()
            break

    def menu(self):
        while True:
            print("\n" + "=" * 60)
            print(f"MENU PRINCIPAL - @{self.current_user}")
            print("=" * 60)
            print("1 - Enviar mensagem")
            print("2 - Ler mensagens novas")
            print("3 - Trocar de usuário")
            print("4 - Sair")
            print("=" * 60)

            option = input("Escolha uma opção: ").strip()
            if option == "1":
                self.send_message()
            elif option == "2":
                self.read_messages()
            elif option == "3":
                self.login()
                break
            elif option == "4":
                self.mongo.close()
                print("\nAté logo!")
                break
            else:
                print("Opção inválida.")

    def send_message(self):
        recipient = input("\nDigite o @destinatário: ").strip()
        if recipient.startswith("@"):
            recipient = recipient[1:]

        message = input("Digite sua mensagem (10 a 2000 caracteres): ").strip()
        if len(message) < 10:
            print("Mensagem muito curta!")
            return

        key = input("Digite a chave combinada: ").strip()

        try:
            encrypted = encrypt_message(message, key)
            self.messages_collection.insert_one({
                "from": self.current_user,
                "to": recipient,
                "message": encrypted,
                "status": "não lida",
                "timestamp": datetime.now()
            })
            print(f"Mensagem enviada para @{recipient}")
        except Exception as e:
            print(f"Erro ao enviar: {e}")

    def read_messages(self):
        msgs = list(self.messages_collection.find({
            "to": self.current_user, "status": "não lida"
        }).sort("timestamp", DESCENDING))

        if not msgs:
            print("\nNenhuma mensagem nova.")
            return

        print("\nMensagens não lidas:")
        for i, msg in enumerate(msgs, 1):
            print(f"{i}. @{msg['from']} - {msg['timestamp'].strftime('%d/%m %H:%M')}")

        choice = input("\nEscolha uma mensagem (número): ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(msgs):
            print("Escolha inválida.")
            return

        msg = msgs[int(choice) - 1]
        key = input("Digite a chave para descriptografar: ").strip()

        try:
            decrypted = decrypt_message(msg["message"], key)
            print("\nMENSAGEM:")
            print(decrypted)
            self.messages_collection.update_one({"_id": msg["_id"]}, {"$set": {"status": "lida"}})
        except InvalidToken:
            print("Chave incorreta!")