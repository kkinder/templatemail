from abc import ABC
from typing import List


class Engine(ABC):
    """
    Defines the interface for engines, which are used to send email.
    """

    def send_simple_message(self, from_address: str, to_addresses: List[str], subject: str, text_body: str = None,
                            html_body: str = None):
        """
        Handles the delivery of an email. This method should be implemented in subclasses.

        :param from_address: From address
        :param to_addresses: To address(es)
        :param subject: Subject of email
        :param text_body: Text body. Leave None for HTML-only.
        :param html_body: HTML body. Leave None for Text-only.
        :raises DeliveryNotMade: Raised when a delivery cannot be made.
        """
        pass
