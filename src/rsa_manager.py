from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class RSAKeyManager:
    @staticmethod
    def generate_keys(key_size, pub_file, priv_file):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        with open(priv_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(pub_file, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    @staticmethod
    def load_public_key(filename):
        with open(filename, "rb") as f:
            return serialization.load_pem_public_key(f.read(), backend=default_backend())

    @staticmethod
    def load_private_key(filename):
        with open(filename, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    