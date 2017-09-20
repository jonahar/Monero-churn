import os
import codecs
import sys


def xmr_to_atomic(amount):
    """
    :param amount: amount of XMR
    :return: the given amount of XMR in atomic units
    """
    return int(amount * 1e12)


def atomic_to_xmr(atomic_units):
    """
    :return: the value of atomic_units atomic units in XMR
    """
    return float(atomic_units) / 1e12


def generate_payment_id(num_bytes=32):
    """
    :param num_bytes integer. number of bytes in the payment id. should be 32 or 8 (to use for
     integrated addresses)
    :return: a random payment id
    """

    if num_bytes not in [8, 32]:
        print('payment id must be 8 or 32 bytes', file=sys.stderr)
        return None

    return codecs.encode(os.urandom(num_bytes), 'hex').decode()
