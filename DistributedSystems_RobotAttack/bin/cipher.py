#From http://programeveryday.com/post/implementing-a-basic-caesar-cipher-in-python/

def encrypt(n, plaintext):
    key = 'abcdefghijklmnopqrstuvwxyz'
    """Encrypt the string and return the ciphertext"""
    result = ''
    for l in plaintext.lower():
        try:
            i = (key.index(l) + n) % 26
            result += key[i]
        except ValueError:
            result += l
    return result.lower()


def decrypt(n, ciphertext):
    key = 'abcdefghijklmnopqrstuvwxyz'
    """Decrypt the string and return the plaintext"""
    result = ''
    for l in ciphertext:
        try:
            i = (key.index(l) - n) % 26
            result += key[i]
        except ValueError:
            result += l
    return result