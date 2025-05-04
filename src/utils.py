import base64
from cryptography.hazmat.primitives import padding

class Utils:
    @staticmethod
    def pad(data, block_size):
        padder = padding.PKCS7(block_size).padder()
        return padder.update(data) + padder.finalize()

    @staticmethod
    def unpad(data, block_size):
        unpadder = padding.PKCS7(block_size).unpadder()
        return unpadder.update(data) + unpadder.finalize()

    @staticmethod
    def encode(data, fmt):
        if fmt == "hexadecimal":
            return data.hex()
        elif fmt == "base64":
            return base64.b64encode(data).decode('utf-8')
        else:
            raise ValueError("Formato inválido.")

    @staticmethod
    def decode(data, fmt):
        if fmt == "hexadecimal":
            return bytes.fromhex(data)
        elif fmt == "base64":
            return base64.b64decode(data)
        else:
            raise ValueError("Formato inválido.")
