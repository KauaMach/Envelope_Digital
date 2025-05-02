import os
import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Funcoes

def generate_aes_key(key_size):
    """Gera uma chave aleatoria AES de dado tamanho (em bits)."""
    return secrets.token_bytes(key_size // 8)

def pad(data, block_size):
    """Preenche dados usando PKCS7."""
    padder = padding.PKCS7(block_size).padder()
    return padder.update(data) + padder.finalize()

def unpad(data, block_size):
    """Remove PKCS7 padding dos dados."""
    unpadder = padding.PKCS7(block_size).unpadder()
    return unpadder.update(data) + unpadder.finalize()

def encode_output(data, encoding_format):
    """Codifica os dados para hexadecimal ou Base64."""
    if encoding_format.lower() == "hexadecimal":
        return data.hex()
    elif encoding_format.lower() == "base64":
        return base64.b64encode(data).decode('utf-8')
    else:
        raise ValueError("Formato de codificacao invalido. Deve ser 'hexadecimal' ou 'base64'.")

def decode_input(data, encoding_format):
    """Decodifica os dados de hexadecimal ou Base64."""
    if encoding_format.lower() == "hexadecimal":
        return bytes.fromhex(data)
    elif encoding_format.lower() == "base64":
        return base64.b64decode(data)
    else:
        raise ValueError("Formato de decodificacao invalido. Deve ser 'hexadecimal' ou 'base64'.")

# Key Generation

def generate_rsa_key_pair(key_size, public_key_file, private_key_file):
    """Gera par de chaves RSA - salvando em PEM."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serializa e salva chave privada
    with open(private_key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Serializa e salva chave publica
    with open(public_key_file, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# Envelope Creation

def create_envelope(message, public_key_file, aes_key_size, aes_mode, output_pattern,
                     encrypted_key_file, encrypted_message_file, iv_file=None):
    """Cria um envelope ao encriptar a msg e a chave AES."""

    # converte msg para bytes (se string)
    if isinstance(message, str):
        message = message.encode('utf-8')

    # Gera uma chave AES
    aes_key = generate_aes_key(aes_key_size)

    # Le a chave publica do destinatario
    with open(public_key_file, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

    # Encripta a chave AES usando RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        rsa_padding.PKCS1v15()
    )

    # Encripta a mensagem usando AES
    if aes_mode.lower() == "ecb":
        cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_message = pad(message, algorithms.AES.block_size)
        ciphertext = encryptor.update(padded_message) + encryptor.finalize()
        iv = None # Sem IV no modo ECB
    elif aes_mode.lower() == "cbc":
        iv = os.urandom(algorithms.AES.block_size // 8) # iv aleatorio
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_message = pad(message, algorithms.AES.block_size)
        ciphertext = encryptor.update(padded_message) + encryptor.finalize()

        # Salva IV para arquivo (em hexadecimal)
        if iv_file:
            with open(iv_file, "w") as f:
                f.write(iv.hex())
        else:
            raise ValueError("IV deve ser especificado usando modo CBC.")


    else:
        raise ValueError("Modo AES invalido. deve ser 'ECB' ou 'CBC'.")

    # Codifica a chave encriptada e a msg baseado no padrao de saida
    encoded_encrypted_key = encode_output(encrypted_key, output_pattern)
    encoded_ciphertext = encode_output(ciphertext, output_pattern)

    # Salva a chave/msg encriptada para arquivo
    with open(encrypted_key_file, "w") as f:
        f.write(encoded_encrypted_key)

    with open(encrypted_message_file, "w") as f:
        f.write(encoded_ciphertext)


# Opening the Envelope

def open_envelope(encrypted_message_file, encrypted_key_file, private_key_file, aes_mode,
                  output_file, iv_file=None):
    """Abre um envelope decriptando a chave AES e a mensagem."""

    # Le a msg encriptada e a chave
    with open(encrypted_message_file, "r") as f:
        encoded_ciphertext = f.read()

    with open(encrypted_key_file, "r") as f:
        encoded_encrypted_key = f.read()

    # Le a chave privada do destinatario
    with open(private_key_file, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

    # Decodificar a chave encriptada e a msg
    encrypted_key = decode_input(encoded_encrypted_key, 'hexadecimal')
    ciphertext = decode_input(encoded_ciphertext, 'hexadecimal') 

    # Decriptar a chave AES usando RSA
    aes_key = private_key.decrypt(
        encrypted_key,
        rsa_padding.PKCS1v15()
    )

    # Decriptar a msg usando AES
    if aes_mode.lower() == "ecb":
        cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_message = decryptor.update(ciphertext) + decryptor.finalize()
        block_size = algorithms.AES.block_size
        message = unpad(decrypted_padded_message, block_size)
    elif aes_mode.lower() == "cbc":
        if iv_file:
             with open(iv_file, "r") as f:
                iv_hex = f.read()
                iv = bytes.fromhex(iv_hex)
        else:
            raise ValueError("Arquivo IV deve ser especificado usando modo CBC.")

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_message = decryptor.update(ciphertext) + decryptor.finalize()
        block_size = algorithms.AES.block_size
        message = unpad(decrypted_padded_message, block_size)
    else:
        raise ValueError("Modo AES invalido. Deve ser 'ECB' ou 'CBC'.")

    # Salvar a mensagem decriptada
    with open(output_file, "wb") as f:
        f.write(message)


if __name__ == "__main__":
    # 1. Geracao de chaves
    key_size = int(input("Digite o tamanho da chave RSA (1024/2048): "))
    public_key_file = "public_key.pem"
    private_key_file = "private_key.pem"
    generate_rsa_key_pair(key_size, public_key_file, private_key_file)
    print(f"Par de chaves RSA gerados e salvos em {public_key_file} e {private_key_file}")

    # 2. Criacao do Envelope
    message = input("Digite a mensagem a ser codificada: ")

    aes_key_size = int(input("Digite o tamanho da chave AES - 128, 192 ou 256: "))
    aes_mode = input("Digite o modo AES (ECB/CBC): ").lower()
    output_pattern = input("Escolha o padrao de saida (hexadecimal/base64): ").lower()
    encrypted_key_file = "encrypted_key.txt"
    encrypted_message_file = "encrypted_message.txt"
    iv_file = "iv.txt" if aes_mode == "cbc" else None # iv file somente se o "cbc" for selecionado

    create_envelope(message, public_key_file, aes_key_size, aes_mode, output_pattern,
                     encrypted_key_file, encrypted_message_file, iv_file)
    print(f"Envelope criado. Chave criptografada salva em {encrypted_key_file}, "
          f"mensagem criptografada salva em {encrypted_message_file}, e IV salvo em {iv_file}.")

    # 3. Abrindo o Envelope
    output_file = "output.txt"
    open_envelope(encrypted_message_file, encrypted_key_file, private_key_file, aes_mode, output_file, iv_file)
    print(f"Envelope aberto. Mensagem descriptografada salva em {output_file}")