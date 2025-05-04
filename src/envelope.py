from rsa_manager import RSAKeyManager
from aes_manager import AESManager
from utils import Utils
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding

class Envelope:
    @staticmethod
    def create(message, pub_key_file, aes_key_size, aes_mode, fmt,
               out_key_file, out_msg_file, iv_file=None):

        rsa_pub = RSAKeyManager.load_public_key(pub_key_file)
        aes = AESManager(aes_key_size)

        ciphertext, iv = aes.encrypt(message, aes_mode)

        encrypted_key = rsa_pub.encrypt(aes.key, rsa_padding.PKCS1v15())

        with open(out_key_file, "w") as f:
            f.write(Utils.encode(encrypted_key, fmt))

        with open(out_msg_file, "w") as f:
            f.write(Utils.encode(ciphertext, fmt))

        if iv and iv_file:
            with open(iv_file, "w") as f:
                f.write(iv.hex())

        print("[✔] Envelope criado com sucesso.")

    @staticmethod
    def open(msg_file, key_file, priv_key_file, aes_mode, fmt, out_file, iv_file=None):
        ciphertext = Utils.decode(open(msg_file).read(), fmt)
        encrypted_key = Utils.decode(open(key_file).read(), fmt)
        private_key = RSAKeyManager.load_private_key(priv_key_file)

        aes_key = private_key.decrypt(encrypted_key, rsa_padding.PKCS1v15())
        aes = AESManager(len(aes_key) * 8)
        aes.key = aes_key

        iv = bytes.fromhex(open(iv_file).read()) if (aes_mode == "cbc" and iv_file) else None
        message = aes.decrypt(ciphertext, aes_mode, iv)

        with open(out_file, "wb") as f:
            f.write(message)

        print("[✔] Envelope aberto com sucesso. Mensagem salva em", out_file)
