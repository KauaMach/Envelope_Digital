from rsa_manager import RSAKeyManager
from aes_manager import AESManager
from envelope import Envelope
from utils import Utils
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
import base64


class EnvelopeApp:
    @staticmethod
    def run():
        while True:
            print("\nMENU:")
            print("1. Gerar par de chaves RSA")
            print("2. Criar envelope digital")
            print("3. Abrir envelope digital")
            print("4. Descriptografar chave AES criptografada com RSA")
            print("0. Sair")

            op = input("Escolha uma opção: ")

            if op == "1":
                size = int(input("Tamanho da chave (1024 ou 2048): "))
                pub = input("Arquivo da chave pública: ")
                priv = input("Arquivo da chave privada: ")
                RSAKeyManager.generate_keys(size, pub, priv)
                print("[✔] Chaves RSA geradas.")

            elif op == "2":
                msg = input("Mensagem: ")
                pub_key = input("Arquivo da chave pública: ")
                aes_size = int(input("Tamanho da chave AES (128/192/256): "))
                mode = input("Modo AES (ecb/cbc): ").lower()
                fmt = input("Formato de saída (hexadecimal/base64): ").lower()
                key_file = input("Arquivo chave criptografada: ")
                msg_file = input("Arquivo mensagem criptografada: ")
                iv_file = input("Arquivo IV (CBC): ") if mode == "cbc" else None

                Envelope.create(msg, pub_key, aes_size, mode, fmt, key_file, msg_file, iv_file)

            elif op == "3":
                msg_file = input("Arquivo da mensagem criptografada: ")
                key_file = input("Arquivo da chave criptografada: ")
                priv_file = input("Arquivo da chave privada: ")
                mode = input("Modo AES (ecb/cbc): ").lower()
                fmt = input("Formato de codificação (hexadecimal/base64): ").lower()
                iv_file = input("Arquivo IV (CBC): ") if mode == "cbc" else None
                out_file = input("Arquivo de saída (mensagem decifrada): ")

                Envelope.open(msg_file, key_file, priv_file, mode, fmt, out_file, iv_file)

            elif op == "4":
                # Nova opção para descriptografar a chave AES
                encrypted_key_file = input("Arquivo da chave AES criptografada: ")
                priv_key_file = input("Arquivo da chave privada RSA: ")
                fmt = input("Formato de codificação da chave (hexadecimal/base64): ").lower()

                # Descriptografar a chave AES
                encrypted_key = Utils.decode(open(encrypted_key_file).read(), fmt)
                private_key = RSAKeyManager.load_private_key(priv_key_file)

                # Descriptografar a chave AES com a chave privada RSA
                aes_key = private_key.decrypt(encrypted_key, rsa_padding.PKCS1v15())
                
                print(f"[✔] Chave AES descriptografada: {Utils.encode(aes_key, fmt)}")

            elif op == "0":
                print("Encerrando.")
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    EnvelopeApp.run()
