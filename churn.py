#!/usr/bin/env python3

import random
import time
import argparse
import logging
import sys
from RPCHandler import RPCHandler

MIN_WAIT_TIME = 25  # it takes ~20 minutes for balance to be unlocked after a sweep

prog_usage = 'python3 churn.py [ARGUMENTS]'
prog_description = 'Automatically churn your Monero coins.'
prog_epilog = 'Note: You must start a wallet RPC server (the official monero-wallet-rpc) before you run this program'


def get_parsed_args():
    parser = argparse.ArgumentParser(usage=prog_usage,
                                     description=prog_description,
                                     epilog=prog_epilog)
    parser.add_argument('--churn-window-start',
                        help='number of minutes until the churning time window starts (default 0)',
                        required=False, type=int, default=0)
    parser.add_argument('--churn-window-end',
                        help='number of minutes until the churning time window ends (default 360)',
                        required=False, type=int, default=360)
    parser.add_argument('--num-churns', help='total number of churns to perform (default 6)',
                        required=False, type=int, default=6)
    parser.add_argument('--priority', help='priority for the churns transactions (default 0)',
                        required=False, type=int, default=0)
    parser.add_argument('--mixin', help='ring size for the churns transactions (default 5)',
                        required=False, type=int, default=5)
    parser.add_argument('--rpc-host',
                        help='hostname of the machine running the rpc server (default localhost)',
                        required=False, type=str, default='localhost')
    parser.add_argument('--rpc-port', help='listening port on the rpc server (default 18082)',
                        required=False, type=int, default=18082)
    parser.add_argument('--username', help='username for rpc authentication (default none)',
                        required=False, type=str, default='')
    parser.add_argument('--password', help='password for rpc authentication (default none)',
                        required=False, type=str, default='')

    return parser.parse_args()


def init_logger():
    # initialize logger
    logging.basicConfig(filename='churn.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    # print log messages to stdout too
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # disable logs of the 'requests' module, unless they are warnings
    logging.getLogger('requests').setLevel(logging.WARNING)


def sleep(minutes):
    """
    sleep for 'minutes' minutes
    """
    time.sleep(minutes * 60)


def is_wallet_ready(rpc_handler):
    """
    Checks if the wallet is ready for churning, that is, all balance is unlocked
    :return: True if wallet is ready for churning
    """
    balance, unlocked_balance = rpc_handler.get_balance()
    return balance == unlocked_balance


def main():
    args = get_parsed_args()
    init_logger()
    logging.info('Starting churn script')
    try:
        rpc_handler = RPCHandler(args.rpc_host, args.rpc_port, args.username, args.password)

        address = rpc_handler.get_address()
        balance, unlocked_balance = rpc_handler.get_balance()
        if balance != unlocked_balance:
            logging.error('Wallet is not ready for churn. Wait until all balance is unlocked')
            return False

        logging.info('Wallet address: {0}\nCurrent balance: {1}'.format(address, balance))

        # we look at a time-line where each unit is a minute.
        # assume the current time is 0, the start time is m and the end time is n.
        # we randomly choose num_churns points in the interval [m, n]. these points are the times
        # in which we are going to churn
        times = random.sample(range(args.churn_window_start, args.churn_window_end + 1),
                              args.num_churns)
        times.extend([args.churn_window_start])
        times.sort()
        logging.info('sleeping times: {0}'.format(times))

        # sleep until the time is m
        logging.info('going to sleep for {0} minutes'.format(args.churn_window_start))
        sleep(args.churn_window_start)
        for i in range(0, len(times) - 1):
            if i == 0:
                # no need to wait MIN_WAIT_TIME in the first time we churn
                d = times[i + 1] - times[i]
            else:
                d = max(times[i + 1] - times[i], MIN_WAIT_TIME)
            logging.info('going to sleep for {0} minutes'.format(d))
            sleep(d)

            while not is_wallet_ready(rpc_handler):
                # not all balance is unlocked. wait more
                logging.info(
                    'Not all balance is unlocked. Sleep for {0} more minutes'.format(MIN_WAIT_TIME))
                sleep(MIN_WAIT_TIME)
            logging.info('churning...')
            rpc_handler.sweep_all(address, priority=args.priority)
            logging.info('churned successfully')

        logging.info('Churn process ended.')

    except Exception as e:
        logging.error('Exception occurred: {0}. Aborting'.format(e))
        exit(1)


main()
