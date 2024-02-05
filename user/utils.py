from random import randint


def generate_hash() -> str:
    salt = ""
    for i in range(1, 6):
        salt += chr(randint(33, 129))
    return salt
