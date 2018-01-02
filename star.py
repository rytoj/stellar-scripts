import requests
from stellar_base.address import Address
from stellar_base.builder import Builder
from stellar_base.keypair import Keypair


def generate_new_prv_key():
    """
    Generates new private key (or seed)
    :return:
    """
    kp = Keypair.random()
    private_key = kp.seed().decode()
    return private_key


def get_public_key_from_seed(seed):
    """Get public key from seed
    :param seed: private key
    :return: public address
    """
    kp = Keypair.from_seed(seed)
    publickey = kp.address().decode()
    return publickey


def get_balance(public_key, testnet=False):
    """"Get balance from public key
    :param public_key: stellar public key
    :param testnet: boolean parameter
    :return: current balance
    """
    try:
        r = requests.get('http://localhost:8000/friendbot?addr=' + public_key)  # Local docker container
    except requests.exceptions.ConnectionError:
        r = requests.get('https://horizon-testnet.stellar.org/friendbot?addr=' + public_key)
    if testnet:
        address = Address(address=public_key)
    else:
        address = Address(address=public_key, network='public')

    address.get()  # get the updated information
    return public_key, address.balances[0]['balance']


def send_stellar(seed, public_key, amount, comment="", testnet=False):
    """
    Sends stellar to public address
    :param testnet: boolean parameter
    :param seed: private key
    :param amount: amount you want to send
    :param comment: comment in transaction
    :param public_key: public key, where you want to send lumen
    :return: return transaction info
    """
    if testnet:
        builder = Builder(secret=seed)
    else:
        builder = Builder(secret=seed, network='public')
    builder.add_text_memo(comment)  # string length <= 28 bytes
    builder.append_payment_op(public_key, amount, 'XLM')
    builder.sign()
    return builder.submit()


def run_as_standalone():
    # public keys
    # ('GCPFZJIO47RPSPVRCPNLJE7CEMJJXN5YRQLI2BWMSGRVBTCG4ZOX3XRJ', '9598.9999400')
    # ('GDYEGCJSQKSJIZ2LJJHKWV244X7W2F7OWVYZYF7FQZC4OSQRS53G7CXF', '10401.0000000')

    seed1 = 'SBUWFJKAREJ3HT6VIAS6L6IF6OCXBLSAM7PWWEM5R64KH5KLJG6PLRCU'
    seed2 = 'SB3UCTCYLDNMQTA2ZGBISGTMI7TFJQ3ZZXU3EUNO27HGYZW5GCMR7CC4'
    publickey1 = get_public_key_from_seed(seed=seed1)
    publickey2 = get_public_key_from_seed(seed=seed2)

    transaction = send_stellar(seed=seed1, public_key=publickey2, amount=1, comment="Test message", testnet=True)
    print(transaction)
    # Print balances
    for pub in publickey1, publickey2:
        balance = get_balance(pub, testnet=True)
        print(balance)


if __name__ == "__main__":
    run_as_standalone()
