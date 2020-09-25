Before using TemplateMail, you need to decide what kind of *engine* you need for your project. An engine does the work of sending an email. At this time, two engines are included with templatemail, however you are free to write your own.

* `templatemail.engines.mailgun.MailgunDeliveryEngine` works specifically with [Mailgun](https://www.mailgun.com/), a commercial email delivery service.
* `templatemail.engines.smtp.SMTPDeliveryEngine` works with other SMTP servers. Because this module is not yet extensively tested to work with a variety of SMTP servers, and SMTP is a fickle protocol, usage of this module is considered experimental.

# Using Mailgun

To create a Mailgun engine, simply pass your API KEY and Mailgun domain to MailgunDeliveryEngine.

```python
import templatemail.engines.mailgun

MAILGUN_API_KEY = 'YOUR API KEY'
MAILGUN_DOMAIN = 'MAILGUN_DOMAIN'

engine = templatemail.engines.mailgun.MailgunDeliveryEngine(
    api_key=MAILGUN_API_KEY,
    domain_name=MAILGUN_DOMAIN)
```

# Using SMTP

SMTP is a bit more complicated, but not that bad. You have your choice of three security models: No Security, SSL, or START TLS.

```python
import templatemail.engines.smtp

SMTP_HOST = 'smtp.example'
SMTP_PORT = 25
SMTP_USERNAME = 'example'
SMTP_PASSWORD = 'secret'

# Choose one a security mechanism here
SMTP_SECURITY = templatemail.engines.smtp.SMTPSecurity.NONE       # No encryption
SMTP_SECURITY = templatemail.engines.smtp.SMTPSecurity.START_TLS  # TLS
SMTP_SECURITY = templatemail.engines.smtp.SMTPSecurity.SSL        # SSL

engine = templatemail.engines.smtp.SMTPDeliveryEngine(
    host=SMTP_HOST,
    port=SMTP_PORT,
    security=SMTP_SECURITY,
    username=SMTP_USERNAME,
    password=SMTP_PASSWORD
)
```

## Open Relays (no security, no login)

If `username` and `password` are not sent as arguments, no login as attempted. This would be useful for an open relay on a secure network:

```python
import templatemail.engines.smtp

SMTP_HOST = 'smtp.example'
SMTP_PORT = 25

open_relay_engine = templatemail.engines.smtp.SMTPDeliveryEngine(
    host=SMTP_HOST,
    port=SMTP_PORT,
    security=templatemail.engines.smtp.SMTPSecurity.NONE,
)
```

# Writing your own engine

If you want to use another email delivery mechanism that isn't Mailgun or SMTP, you can write your own delivery engine. To implement an engine, inherit from the `templatemail.engines.Engine` [abstract base class](https://docs.python.org/3/library/abc.html). Then define a `send_simple_message` instance method with the following parameters:

* param from_address: From address
* param to_addresses: To address(es)
* param subject: Subject of email
* param text_body: Text body. None for HTML-only
* param html_body: HTML body. None for Text-only
* param headers: Other headers for email

Here's an example of a logging-only backend.

```python
from typing import List, Dict

import logging

import templatemail
from templatemail.engines import Engine


class LoggingDeliveryEngine(Engine):
    def send_simple_message(self,
                            from_address: str,
                            to_addresses: List[str],
                            subject: str,
                            text_body: str = None,
                            html_body: str = None,
                            headers: Dict = None):
        logging.info(f'Sending an email to {to_addresses} with subject of {subject}')


# Install delivery engine
mailer = templatemail.TemplateMail(delivery_engine=LoggingDeliveryEngine)
```

