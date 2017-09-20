import requests
from requests.auth import HTTPDigestAuth
import json
import utils


class RPCHandler:
    """
    Manages RPC calls for an open rpc server (Monero wallet/daemon).

    RPCHandler supports methods of the Monero daemon and the Monero wallet, but these have different
    API. When using an RPCHandler be sure to use only the methods that are supported by the rpc
    server that is running (daemon/wallet).
    """

    def __init__(self, host='localhost', port=18082, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.url = 'http://' + host + ':' + str(port) + '/json_rpc'

    def _send_recv(self, rpc_input):
        """
        make an rpc call and return its result. If an error occurred RuntimeError is raised
        :param rpc_input: input for the rpc call (json format)
        :raise RuntimeError if the called rpc method failed
        """
        response = requests.post(self.url, data=json.dumps(rpc_input),
                                 auth=HTTPDigestAuth(self.username, self.password))
        response = response.json()
        if 'error' in response:
            raise RuntimeError(response['error']['message'])
        return response['result']

    # ----- Wallet RPC -----

    def get_balance(self):
        """
        return the wallet's XMR balance and unlocked balance.
        values returned as tuple (balance, unlocked_balance)
        """
        rpc_input = {'method': 'getbalance'}
        result = self._send_recv(rpc_input)
        return utils.atomic_to_xmr(result['balance']), \
               utils.atomic_to_xmr(result['unlocked_balance'])

    def get_address(self):
        """
        return the wallet address
        """
        rpc_input = {'method': 'getaddress'}
        result = self._send_recv(rpc_input)
        return result['address']

    def transfer(self, destinations, payment_id=None, mixin=5, priority=0):
        """
        :param destinations: array of dictionaries. each dictionary has keys 'amount' and 'address'.
                             'amount' is an unsigned int (amount of XMR in atomic units) and 'address'
                             is a string - the address to send to.
        :param payment_id string payment id (optional)
        :param mixin integer the ring size
        """
        params = {'destinations': destinations,
                  'fee': 0,  # this is mandatory, but is ignored. fee is calculated automatically
                  'mixin': mixin,
                  'unlock_time': 0,
                  'priority': priority,
                  'get_tx_hex': False}

        if payment_id is not None:
            params.update({'payment_id': payment_id})

        rpc_input = {'method': 'transfer', 'params': params}

        result = self._send_recv(rpc_input)
        # result has keys: 'fee', 'tx_hash', 'tx_key'

    def sweep_all(self, address, priority=0, mixin=5, payment_id=None):
        """
        :param address:
        :param priority:
        :param mixin:
        :param payment_id:
        :return:
        """
        params = {'address': address,
                  'priority': priority,
                  'mixin': mixin,
                  'unlock_time': 0}
        if payment_id is not None:
            params.update({'payment_id': payment_id})

        rpc_input = {'method': 'sweep_all', 'params': params}
        result = self._send_recv(rpc_input)
        # result has keys: 'tx_hash_list', 'tx_key_list', 'tx_blob_list'

    def make_integrated_address(self, payment_id=''):
        """
        create an integrated address (a special address for receiving funds which already contains
        a unique payment id).
        :param payment_id: string. payment id. if empty, random id is generated
        :return: the generated integrated address
        """
        params = {'payment_id': payment_id}
        rpc_input = {'method': 'make_integrated_address', 'params': params}
        result = self._send_recv(rpc_input)
        return result['integrated_address']

    def split_integrated_address(self, integrated_address):
        """
        :param integrated_address: integrated address
        :return: the address and payment id corresponding to the given integrated address.
                 returns a tuple (standard_address, payment_id)
        """
        params = {'integrated_address': integrated_address}
        rpc_input = {'method': 'split_integrated_address', 'params': params}
        result = self._send_recv(rpc_input)
        return result['standard_address'], result['payment_id']

    # ----- Daemon RPC -----

    def get_block(self, height=None, hash=None):
        """
        retrieve block information from a block height or block hash. At least one of the arguments
        should be supplied. If both arguments are supplied, the hash is ignored and the block is
        retrieved by height.

        :param height int. the height of the block to retrieve
        :param hash string. the hash of the block to retrieve

        :return: a dictionary with the block information
        """
        if height is not None:
            params = {'height': height}
        elif hash is not None:
            params = {'hash': hash}
        else:
            return None

        rpc_input = {'method': 'getblock', 'params': params}
        result = self._send_recv(rpc_input)
        return json.loads(result['json'])

    def get_transactions(self, txs_hashes):
        """
        retrieve information about one or more transactions. transactions are retrieved from
        tx hashes.
        :param txs_hashes list of hashes of the transactions to retrieve.

        :return: list of transactions. each transaction is given as a json string
        """

        # this daemon RPC call does not use the JSON_RPC interface, so we make the call here,
        # instead of calling _send_recv
        rpc_input = {'txs_hashes': txs_hashes, 'decode_as_json': True}
        url = 'http://' + self.host + ':' + str(self.port) + '/gettransactions'
        response = requests.post(url, data=json.dumps(rpc_input),
                                 auth=HTTPDigestAuth(self.username, self.password)).json()

        result = response['txs_as_json']  # list of strings. each string is in json format
        return result
