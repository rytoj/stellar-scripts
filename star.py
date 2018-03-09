import os
import time

import requests
from stellar_base.address import Address
from stellar_base.builder import Builder
from stellar_base.keypair import Keypair


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
    def __init__(self, publickey, testnet=True, local=False):
        self.public_key = publickey
        self.testnet = testnet
        self.local = local
        self.docker_horizon = "http://localhost:8000/friendbot?addr="
        self.main_horizon = "https://horizon-testnet.stellar.org/friendbot?addr="

    def get_wallet(self):
        """"Get balance from public key
        :param public_key: stellar public key
        :param testnet: boolean parameter
        :return: current balance
        """

        if self.local:
            try:
                requests.get(self.docker_horizon + self.public_key, timeout=2)
            except requests.exceptions.ConnectionError:
                requests.get(self.main_horizon + self.public_key)
        else:
            requests.get(self.main_horizon + self.public_key)

        if self.testnet:
            self.address = Address(address=self.public_key)
        else:
            self.address = Address(address=self.public_key, network='public')

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
                return asset.get("balance") + " token"
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

    def demo_balance(self):
        """
        Display balance info for demo
        """
        wallet = self.get_wallet()
        xlm = self.get_native_balance()
        token = self.get_token_balance("PYTH")
        print("Wallet: {}\nXLM:  {}\nPYTH: {}".format(wallet, xlm, token))


def run_as_standalone():
    """
    Run script as stand_alone
    """

    def demo(local_docker=True):
        """
        Display demo account information
        :param local_docker: local docker instance
        """
        account = Stelar(publickey="GABGKZCXBGDOPBFNWOHLOIJU4DFA3VYKWMPJAMKV4QS4YYJ5IK3CNWNQ",
                         testnet=True, local=local_docker)
        account.demo_balance()

    def send_stellar(seed, public_key, amount, currency="XLM", asset_issuer=False, comment="",
                     testnet=True):
        """
        Sends stellar to public address
        :param testnet: boolean parameter
        :param seed: private key
        :param amount: amount you want to send
        :param comment: comment in transaction string length <= 28 bytes
        :param public_key: public key, where you want to send lumen
        :return: return transaction info
        """
        if testnet:
            builder = Builder(secret=seed)
        else:
            builder = Builder(secret=seed, network='public')
        builder.add_text_memo(comment)
        builder.append_payment_op(public_key, amount, currency, asset_issuer)
        builder.sign()
        return builder.submit()

    demo()


if __name__ == "__main__":
    run_as_standalone()
