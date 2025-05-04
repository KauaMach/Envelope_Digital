import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from utils import Utils

class AESManager:
    def __init__(self, key_size):
        self.key = secrets.token_bytes(key_size // 8)

    def encrypt(self, message, mode):
        if isinstance(message, str):
            message = message.encode()

        if mode == "ecb":
            cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()
            padded = Utils.pad(message, algorithms.AES.block_size)
            return encryptor.update(padded) + encryptor.finalize(), None

        elif mode == "cbc":
            iv = os.urandom(algorithms.AES.block_size // 8)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            padded = Utils.pad(message, algorithms.AES.block_size)
            return encryptor.update(padded) + encryptor.finalize(), iv

        else:
            raise ValueError("Modo AES inválido.")

    def decrypt(self, ciphertext, mode, iv=None):
        if mode == "ecb":
            cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        elif mode == "cbc":
            if not iv:
                raise ValueError("IV necessário para modo CBC.")
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        else:
            raise ValueError("Modo AES inválido.")

        decryptor = cipher.decryptor()
        padded_message = decryptor.update(ciphertext) + decryptor.finalize()
        return Utils.unpad(padded_message, algorithms.AES.block_size)

