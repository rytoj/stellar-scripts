import requests
import time
from stellar_base.address import Address
from stellar_base.builder import Builder
from stellar_base.keypair import Keypair
import os


class GetKeys:
    def generate_new_prv_key(self):
        """
        Generates new private key (or seed)
        :return:
        """
        kp = Keypair.random()
        private_key = kp.seed().decode()
        return private_key

    def get_public_key_from_seed(self, seed):
        """
        Get public key from seed
        :param seed: private key
        :return: public address
        """
        kp = Keypair.from_seed(seed)
        publickey = kp.address().decode()
        return publickey

    def get_private_public_key(self):
        prv_key = self.generate_new_prv_key()
        pub_key = self.get_public_key_from_seed(prv_key)
        print("Public key: {}\nPrivate key:{}".format(prv_key, pub_key))


class Stelar():
    def __init__(self, publickey, testnet=False, local=False):
        self.pulic_key = publickey
        self.testnet = testnet
        self.local = local

    def get_wallet(self):
        """"Get balance from public key
        :param public_key: stellar public key
        :param testnet: boolean parameter
        :return: current balance
        """

        if self.local:
            try:
                r = requests.get('http://localhost:8000/friendbot?addr=' + self.pulic_key, timeout=1)
            except requests.exceptions.ConnectionError:
                r = requests.get('https://horizon-testnet.stellar.org/friendbot?addr=' + self.pulic_key)
        else:
            r = requests.get('https://horizon-testnet.stellar.org/friendbot?addr=' + self.pulic_key)

        if self.testnet:
            self.address = Address(address=self.pulic_key)
        else:
            self.address = Address(address=self.pulic_key, network='public')

        self.address.get()  # get the updated information
        self.wallet = self.address.balances
        return self.address.balances

    def get_native_balance(self):
        """
        :return: XLM balance
        """
        for asset in self.wallet:
            if asset.get("asset_type") == "native":
                return asset.get("balance")

    def get_token_balance(self, token):
        """
        :return: token balance
        """
        for asset in self.wallet:
            if asset.get('asset_code') == token:
                return asset.get("balance") + " XML"
        return "Token not found."

    def get_balance(self, balance):
        return balance.get("balance")

    def loop_balance(self, refresh=3, token=False):
        """
        :param refresh: default refresh time
        :param token: token name
        :return: asset balance
        """
        while True:
            time.sleep(5)
            self.get_wallet()
            os.system('cls' if os.name == 'nt' else 'clear')
            if not token:
                print(self.get_native_balance() + " XLM")
            else:
                print(self.get_token_balance(token))

    def send(self, seed, public_key, amount, comment="", asset="XML"):
        """
        Sends stellar to public address
        :param testnet: boolean parameter
        :param seed: private key
        :param amount: amount you want to send
        :param comment: comment in transaction string length <= 28 bytes
        :param public_key: public key, where you want to send lumen
        :param asset: by default lumen XML
        :return: return transaction info
        """
        if self.testnet:
            builder = Builder(secret=seed)
        else:
            builder = Builder(secret=seed, network='public')
        builder.add_text_memo(comment)
        builder.append_payment_op(public_key, amount, asset)
        builder.sign()
        return builder.submit()


def run_as_standalone():
    account = Stelar(publickey="GABGKZCXBGDOPBFNWOHLOIJU4DFA3VYKWMPJAMKV4QS4YYJ5IK3CNWNQ", testnet=True)
    wallet = account.get_wallet()
    stellar = account.get_native_balance()
    sudocoin = account.get_token_balance("sudokoin")
    account.loop_balance()



if __name__ == "__main__":
    run_as_standalone()
