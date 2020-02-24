import requests
import json
import logging


logger = logging.getLogger("proxy")


class ProxyApiCaller:
    def __init__(self, url):
        self.url = url

    def get_account_nonce(self, address):
        req = f"{self.url}/address/{address}/nonce"
        try:
            response = requests.get(req)
            if response.status_code != 200:
                return "response status code " + str(response.status_code)

            parsed = json.loads(response.text)
            return print(parsed['nonce'])
        except:
            # TODO maybe we can discuss what should we do if we get except here
            return print("cannot get nonce")

    def get_account_balance(self, address):
        req = f"{self.url}/address/{address}/balance"
        try:
            response = requests.get(req)
            if response.status_code != 200:
                return "response status code " + str(response.status_code)

            parsed = json.loads(response.text)
            return print(parsed['balance'])
        except:
            # TODO maybe we can discuss what should we do if we get except here
            return print("cannot get balance")

    def get_account(self, address):
        req = f"{self.url}/address/{address}"
        try:
            response = requests.get(req)
            if response.status_code != 200:
                return "response status code " + str(response.status_code)
            parsed = json.loads(response.text)
            return print(parsed)
        except:
            # TODO maybe we can discuss what should we do if we get except here
            return print("cannot get account")
