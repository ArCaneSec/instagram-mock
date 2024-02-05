from random import randint


def generate_hash(self) -> str:
    return chr(randint(1, 129))
