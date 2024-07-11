from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def pad_key(key, length):
    # 调整密钥长度
    return key.ljust(length)[:length].encode('utf-8')

def encrypt(key, plaintext):
    try:
        key = pad_key(key, 32)  # AES-256需要32字节密钥
        iv = os.urandom(16)  # 生成随机的16字节IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext
    except Exception as e:
        print(f'EncodeAES encrypt error: {e}')
        return None


def decrypt(key, ciphertext):
    try:
        key = pad_key(key, 32)  # 调整密钥长度
        iv = ciphertext[:16]  # 提取IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext[16:]) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()

        return plaintext
    except Exception as e:
        print(f'EncodeAES decrypt error: {e}')
        return None

# 示例使用
key = "jhzchfl008"
plaintext = "Hello, World!"

#ciphertext = encrypt(key, plaintext)
#print("Ciphertext:", ciphertext)
#decrypted_text = decrypt(key, ciphertext)
#("Decrypted text:", decrypted_text)
