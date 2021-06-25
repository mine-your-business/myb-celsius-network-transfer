import os


class Configuration:

    def __init__(self):
        self.celsius_network = CelsiusNetwork()


class CelsiusNetworkApiKey:

    def __init__(self):
        self.key = os.environ.get('CELNET_API_KEY')
        self.partner_token = os.environ.get('CELNET_PARTNER_TOKEN')


class CelsiusNetworkWithdrawal:

    def __init__(self):
        self.crypto = os.environ.get('WITHDRAWAL_CRYPTO')
        self.crypto_leave_minimum = float(os.environ.get('WITHDRAWAL_CRYPTO_LEAVE_MIN'))
        self.address = os.environ.get('WITHDRAWAL_ADDRESS')
        self.usd_equivalent = float(os.environ.get('WITHDRAWAL_USD_EQUIVALENT'))


class CelsiusNetwork:

    def __init__(self):
        self.withdrawal = CelsiusNetworkWithdrawal()
        self.api_key = CelsiusNetworkApiKey()
