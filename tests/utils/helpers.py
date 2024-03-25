import random
import string

def create_random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=16))


def create_random_email() -> str:
    return f"{create_random_lower_string()}@{create_random_lower_string()}.com"