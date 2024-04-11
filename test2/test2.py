from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt_rsa_key(passphrase: bytes, salt: bytes, rsa_key_encrypted: bytes) -> str:
    nonce = "thisisnoncejulia"
    key = derive_key(passphrase, salt)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce.encode()))
    decryptor = cipher.decryptor()
    rsa_key_decrypted = decryptor.update(rsa_key_encrypted) + decryptor.finalize()
    return rsa_key_decrypted.decode()
    
def derive_key(passphrase: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(passphrase)

passphrase = "randomismoresecure"
server_id = "8deqIsDyimRJCIsxRZgmF7Lhv8ldIa9NLyJDIsoscdA"
pass_encrypted = "b'h\x9b\xe6\xf80+\x93\x987\xb7]\xbf'"
print(pass_encrypted)
pass_encrypted = pass_encrypted.strip("b'")
print(pass_encrypted)
pass_encrypted = pass_encrypted.encode("latin")
password = decrypt_rsa_key(passphrase.encode(), server_id.encode(), pass_encrypted)

print(password)