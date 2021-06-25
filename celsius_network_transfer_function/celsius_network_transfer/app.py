import os
import json

from .configuration import Configuration
from celsius_network import CelsiusNetworkApi


def lambda_handler(event, context):
    """Lambda function reacting to EventBridge events

    Parameters
    ----------
    event: dict, required
        Event Bridge Scheduled Events Format

        Event doc: https://docs.aws.amazon.com/eventbridge/latest/userguide/event-types.html#schedule-event-type

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    """

    dry_run = os.environ.get('RUN_MODE') == 'test'
    print(f'Running in {"dry run" if dry_run else "production"} mode')

    config = Configuration()

    celnet_api = CelsiusNetworkApi(
        celsius_partner_token=config.celsius_network.api_key.partner_token,
        user_api_key=config.celsius_network.api_key.key
    )

    # easier to type
    withdrawal = config.celsius_network.withdrawal

    current_balance = celnet_api.get_balance_coin(withdrawal.crypto)

    wallet_amount = float(current_balance["amount"])
    wallet_usd_equivalent = float(current_balance["amount_in_usd"])
    if wallet_amount == 0 or wallet_usd_equivalent == 0:
        print('Cannot continue processing - wallet balance is 0')
        return False

    crypto_price = wallet_usd_equivalent / wallet_amount
    print(f'Current {withdrawal.crypto} wallet balance: {wallet_amount} => ${wallet_usd_equivalent}')
    print(f'Current estimated crypto price: ${crypto_price} USD per {withdrawal.crypto}')

    remaining_usd_balance = wallet_usd_equivalent - withdrawal.usd_equivalent
    if crypto_price == 0:
        print('Cannot continue processing - calculated crypto price is 0')
        return False

    remaining_crypto_balance = remaining_usd_balance / crypto_price
    crypto_withdrawal_amount = wallet_amount - remaining_crypto_balance

    if remaining_crypto_balance >= withdrawal.crypto_leave_minimum:
        print(f'Sufficient funds are available for withdrawal of {crypto_withdrawal_amount} {withdrawal.crypto}')
        print(f'Remaining balance will be: {remaining_crypto_balance} {withdrawal.crypto}')
        if not dry_run:
            print(f'Withdrawing ${withdrawal.usd_equivalent} worth of {withdrawal.crypto} ({crypto_withdrawal_amount})')
            result = celnet_api.withdraw_coin(withdrawal.crypto, withdrawal.address, crypto_withdrawal_amount)
            print(f'Withdrawal result: {json.dumps(result, indent=2)}')
        else:
            print(f'Would have withdrawn ${withdrawal.usd_equivalent} worth of {withdrawal.crypto} ' +
                  f'({crypto_withdrawal_amount})')
    else:
        print(f'Insufficient funds are available for withdrawal of {crypto_withdrawal_amount} {withdrawal.crypto}')
        print(f'Remaining balance would have been {remaining_crypto_balance} {withdrawal.crypto} ' +
              f'which is less than minimum of {withdrawal.crypto_leave_minimum}')

    # We got here successfully!
    return True
