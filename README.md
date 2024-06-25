![Build Status](https://travis-ci.org/kkinder/templatemail.svg?branch=master)

# Welcome to TemplateMail

TemplateMail is a simple Python library that solves most projects' email templating and delivery needs with minimal hassle. Suppose you want to send a welcome email to a new user using Mailgun:

```python
import templatemail
import templatemail.engines.mailgun

# Credentials for Mailgun
MAILGUN_API_KEY = 'YOUR API KEY'
MAILGUN_DOMAIN = 'MAILGUN_DOMAIN'

# The engine is in charge of sending email using a backend system.
engine = templatemail.engines.mailgun.MailgunDeliveryEngine(
    api_key=MAILGUN_API_KEY,
    domain_name=MAILGUN_DOMAIN)
    
# The mailer is in charge of rendering templates and sending them using an engine.
mailer = templatemail.TemplateMail(
    template_dirs=['email_templates'],
    delivery_engine=engine)

# Using the two, you can send templates.
template_name = 'welcome.html'
result = mailer.send_email(
    to_addresses=['test@example.com'],
    from_address='from@example.com',
    template_name=template_name,
    user_name='Ken'
)
```

`welcome.html` is an *email template* used to render the subject, html, and text versions of an email. Let's have a look at `email_templates/welcome.html`:

```jinja2
{% block subject %}Welcome to our system{% endblock %}
{% block html_body %}
<h1>Welcome to our system, {{ user_name }}</h1>
<p>We think you'll really enjoy it here.</p>
{% endblock %}
{% block text_body %}
Welcome to our system, {{ user_name }}
--------------------------------------------

We think you'll really enjoy it here.
{% endblock %}
```

The `subject` block renders the subject, while `html_body` and `text_body` render the HTML and text versions of the email respectively. The work of composing the correct mime envelope, as well as delivery, is handled by an engine. At this time, TemplateMail has native Mailgun and SMTP backends, however you are also free to write your own. (See [Writing your own engine](/engines/#writing-your-own-engine))

It's that simple.

## Installation

You can install templatemail like any other Python module.

```pip install templatemail```

**NOTE**: Only Python 3 is supported.

## Read More

[Read the documentation online](https://templatemail.readthedocs.io/en/latest/) at Read The Docs.

## Get in touch
Have a pull request or an issue? [Use Github](https://github.com/kkinder/templatemail).

## Legal stuff
© Copyright 2019 Ken Kinder. Includes work from Mailgun, which is © Copyright 2014 Mailgun.

TemplateMail is licensed under the Apache 2.0 license. See LICENSE for details.

Includes templates from the Mailgun Responsive Templates repository. See LICENSE-mailgun-templates for details on its license.
