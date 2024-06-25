For convenience and as an example, TemplateMail ships with [Mailgun's Transactional Eamil Templates](https://www.mailgun.com/email-templates/transactional-email-templates). These provide an excellent way of sending some boilerplate emails in a new project without a lot of hassle. The Mailgun examples are modified a bit for inclusion in TemplateMail and are meant primarily as examples.

Note that you can use these templates with any backend, not just the Mailgun engine.

For example, the `mailgun-transactional/action.html` template is for an action, such as confirming a forgotten password.

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
    delivery_engine=engine)

mailer.send_email(
    to_addresses=['test@example.com'],
    from_address='from@example.com',
    template_name='mailgun-transactional/action.html',
    
    user_name='Ken',
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

See [the git repository](https://github.com/kkinder/templatemail/tree/master/templatemail/templates/mailgun-transactional) for other examples.