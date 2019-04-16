# Welcome to TemplateMail

TemplateMail is a simple Python library for sending emails using a templating language you already know: Jinaj2. It includes by default a Mailgun backend for easy delivery, along with example responsive templates based on [Mailgun Responsive Templates](https://github.com/mailgun/transactional-email-templates).

You can get started sending email within your project this easily:

```python
import templatemail


mailer = templatemail.TemplateMail(
    template_dirs=['email_templates'],
    delivery_engine=templatemail.MailgunDeliveryEngine(api_key=MAILGUN_API_KEY, domain_name=MAILGUN_DOMAIN))
result = mailer.send_email(
    to_addresses=['test@example.com'],
    from_address='from@example.com',
    template_name='welcome.html',
    user_name='Ken'
)
```

In `email_templates/welcome.html`:

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

You have full use of jinja2 functionality, including inheritance, and HTML/Text content is rendered in separate blocks. (Note that you can leave either blank and it will be sent as either an HTML-only email or a text-only email.)

It's that simple.

----

## Installation

```pip install templatemail```

## Usage

### Rendering
The `templatemail` package contains the `TemplateMail` class, which renders email. To *only* render an email, but not send it, call the `render()` method:

```python
mailer = templatemail.TemplateMail(...)
content = mailer.render(template_name, *args, **kwargs)
print(content.subject)
print(content.text_body)
print(content.html_body)
```

### Delivery
Delivery depends on the TemplateMail class having a `delivery_engine` attribute set or passed to its constructor. Currently, the package ships with a delivery engine for Mailgun.

```python
engine = templatemail.MailgunDeliveryEngine('YOUR MAILGUN API KEY', 'YOUR MAILGUN DOMAIN')
mailer = templatemail.TemplateMail(..., delivery_engine=engine)
```

A delivery engine can be any class that has a `send_simple_message` method with the following signature:

```python
def send_simple_message(self, from_address: str, to_addresses: List[str], subject: str, text_body: str,
                        html_body: str):
```

`DeliveryNotMade` is raised if a delivery is not possible.

## Using Mailgun's responsive email templates

Largely as an example, I've included some of Mailgun's [responsive templates](https://github.com/mailgun/transactional-email-templates), inlined, with the package.

For example:

```python
mailer = templatemail.TemplateMail(template_dirs=['templates'])
content = mailer.render(
    'mailgun-transactional/action.html',
    subject="Did You Forget Your Password?",
    meta_name='Confirm Email',
    leadin='Please confirm your email address by clicking the link below.',
    explanation='We may need to send you critical information about our service and it is important that we have an accurate email address.',
    action_link='https://localhost:8080/forgot-password/click-me',
    action_text="Reset your password",
    signature='--The Team',
    footer='You are getting this message because someone (presumably you) clicked on Forgot Password on our site.'
)
```

## Get in touch
Have a pull request or an issue? [Use Github](https://github.com/kkinder/templatemail).

## Legal stuff
© Copyright 2019 Ken Kinder. Includes work from Mailgun, which is © Copyright 2014 Mailgun.

TemplateMail is licensed under the Apache 2.0 license. See LICENSE for details.

Includes templates from the Mailgun Responsive Templates repository. See LICENSE-mailgun-templates for details on its license.
