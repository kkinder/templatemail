from typing import List

import requests

from . import Engine
from .. import DeliveryNotMade


class MailgunDeliveryEngine(Engine):
    def __init__(self, api_key, domain_name):
        self.api_key = api_key
        self.domain_name = domain_name
        self._requests = requests

    def send_simple_message(self, from_address: str, to_addresses: List[str], subject: str, text_body: str = None,
                            html_body: str = None):
        data = {"from":    from_address,
                "to":      to_addresses,
                "subject": subject}
        if text_body:
            data['text'] = text_body.strip()
        if html_body:
            data['html'] = html_body.strip()
        response = self._requests.post(
            f"https://api.mailgun.net/v3/{self.domain_name}/messages",
            auth=("api", self.api_key),
            data=data
        )
        if response.status_code < 200 or response.status_code > 299:
            raise DeliveryNotMade(details=f"Got unexpected status from mailgun: {response.status_code}",
                                  response=response)
