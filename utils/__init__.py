import os
import binascii


def get_random_hex_string(length=14):
    return binascii.b2a_hex(os.urandom(length))


def do_populate_data():
    try:
        pretest_generation = os.environ['GEN']
        if pretest_generation.lower().strip() in ('1', 'on', 'true'):
            return True
    except KeyError:
        return False
    return False
