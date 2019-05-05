import html
import os
import tempfile
import webbrowser
from unittest import TestCase
from unittest.mock import Mock, patch

import templatemail
import templatemail.engines.mailgun
import templatemail.engines.smtp

_dir_path = os.path.dirname(os.path.realpath(__file__))
_test_template_dir = os.path.join(_dir_path, 'test_templates')

#
# Set TEST_TEMPLATEMAIL_IN_BROWSER to render html in your web browser upon test execution.
open_results_in_browser = os.environ.get('TEST_TEMPLATEMAIL_IN_BROWSER', 'False').lower() in (
    'true', '1', 'yes', 't', 'y')


class TestTemplateMail(TestCase):
    def _open_content_rendering_in_browser(self, content):
        if open_results_in_browser:
            escaped_text = html.escape(content.text_body)

            temp = tempfile.NamedTemporaryFile(prefix="templatemail_", suffix='.html', delete=False)
            temp.write(
                content.html_body.encode('utf8') + f'<hr><h1>TEXT VERSION</h1><pre>{escaped_text}</pre>'.encode('utf8'))
            webbrowser.open_new_tab(f'file:///{temp.name}')

    def test_basic_template(self):
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir])
        content = mailer.render(
            'simple_template.html',
        )
        self.assertEqual(content.subject, "My Subject")
        self.assertEqual(content.html_body, "HTML stuff")
        self.assertEqual(content.text_body, "Text stuff")

    def test_render_action_email(self):
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir])
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
        self.assertEqual(content.subject, "Did You Forget Your Password?")
        self.assertIn("--The Team", content.text_body)
        self.assertIn("--The Team", content.html_body)

        self._open_content_rendering_in_browser(content)

    def test_render_billing_email(self):
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir])
        content = mailer.render(
            'mailgun-transactional/billing.html',
            invoice_to="Lee Munroe\nInvoice #12345\nJune 01 2014",
            services=[('Consulting', '$55'), ('Cheese Making', '$500')],
            total_text='Total',
            total_price='$555',
            view_link='http://localhost:8080/invoice',
            view_text='View your invoice online',
            subject="Your invoice is paid",
            title="$33.98 Paid",
            subtitle='Thank you for using Acme.',
            signature='--The Team',
            footer='Sent by the Acme Corporation'
        )
        self.assertEqual(content.subject, "Your invoice is paid")
        self.assertIn("--The Team", content.text_body)
        self.assertIn("--The Team", content.html_body)

        self._open_content_rendering_in_browser(content)

    def test_render_alert_email(self):
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir])
        content = mailer.render(
            'mailgun-transactional/alert.html',
            subject='You are over the number of widgets',
            signature='--The Team',
            action_link="http://localhost:8080/upgrade",
            action_text="Upgrade Now",
            warning_text="You are over the number of widgets on your current plan",
            details="Upgrade now and you can get way, way more widgets.\nNo I'm serious, like, a ton more.",
            footer='Sent by the Acme Corporation'
        )
        self.assertEqual(content.subject, "You are over the number of widgets")
        self.assertIn("--The Team", content.text_body)
        self.assertIn("--The Team", content.html_body)

        self._open_content_rendering_in_browser(content)

    def test_mailgun_sending(self):
        engine = templatemail.engines.mailgun.MailgunDeliveryEngine(api_key='foobar', domain_name='spam.eggs')
        engine._requests.post = Mock(return_value=Mock(status_code=201))

        self._test_sending_mailgun(engine)

    def test_mailgun_sending_failure(self):
        engine = templatemail.engines.mailgun.MailgunDeliveryEngine(api_key='foobar', domain_name='spam.eggs')
        engine._requests.post = Mock(return_value=Mock(status_code=401))

        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir], delivery_engine=engine)
        self.assertRaises(
            templatemail.DeliveryNotMade,
            mailer.send_email,
            to_addresses=['test@example.com'],
            from_address='from@example.com',
            template_name='simple_template.html'
        )

    def test_smtp_sending(self):
        for security in (templatemail.engines.smtp.SMTPSecurity.NONE, templatemail.engines.smtp.SMTPSecurity.START_TLS,
                         templatemail.engines.smtp.SMTPSecurity.SSL):
            engine = self._get_smtp_engine(security=security)

            # TODO: Make this really test something meaningful
            with patch('templatemail.engines.smtp.smtplib.SMTP_SSL') as smtp_ssl:
                with patch('templatemail.engines.smtp.smtplib.SMTP') as smtp:
                    engine.send_simple_message(from_address='from@example.com',
                                               to_addresses=['to@example.com'],
                                               subject='Test',
                                               html_body='HTML Body')
                    engine.send_simple_message(from_address='from@example.com',
                                               to_addresses=['to@example.com'],
                                               subject='Test',
                                               text_body='TEXT Body')
                    engine.send_simple_message(from_address='from@example.com',
                                               to_addresses=['to@example.com'],
                                               subject='Test',
                                               text_body='TEXT Body',
                                               html_body='HTML Body')


    def test_delivery_engine_not_installed(self):
        """
        Tests to make sure DeliveryEngineNotInstalled is raised
        :return:
        """
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir])
        self.assertRaises(
            templatemail.DeliveryEngineNotInstalled,
            mailer.send_email,
            to_addresses=['test@example.com'],
            from_address='from@example.com',
            template_name='simple_template.html'
        )

    def _test_sending_mailgun(self, engine):
        self._test_sending(engine)
        engine._requests.post.assert_called_with(
            'https://api.mailgun.net/v3/spam.eggs/messages',
            auth=('api', 'foobar'),
            data={'from':    'from@example.com', 'to': ['test@example.com'],
                  'subject': 'You are over the number of widgets',
                  'text':    "You are over the number of widgets on your current plan\n\n\nUpgrade now and you can get way, way more widgets.\n\nNo I'm serious, like, a ton more.\n\n\nUpgrade Now: http://localhost:8080/upgrade\n\n--The Team\n\n===========================\nSent by the Acme Corporation",
                  'html':    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" style="font-family: \'Helvetica Neue\', Helvetica, Arial, sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">\n<head>\n    <meta name="viewport" content="width=device-width" />\n    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n    <title>You are over the number of widgets</title>\n\n    <style type="text/css">\n    img {\n        max-width: 100%;\n    }\n    body {\n        -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: none; width: 100% !important; height: 100%; line-height: 1.6em;\n    }\n    body {\n        background-color: #f6f6f6;\n    }\n    @media only screen and (max-width: 640px) {\n        body {\n            padding: 0 !important;\n        }\n        h1 {\n            font-weight: 800 !important; margin: 20px 0 5px !important;\n        }\n        h2 {\n            font-weight: 800 !important; margin: 20px 0 5px !important;\n        }\n        h3 {\n            font-weight: 800 !important; margin: 20px 0 5px !important;\n        }\n        h4 {\n            font-weight: 800 !important; margin: 20px 0 5px !important;\n        }\n        h1 {\n            font-size: 22px !important;\n        }\n        h2 {\n            font-size: 18px !important;\n        }\n        h3 {\n            font-size: 16px !important;\n        }\n        .container {\n            padding: 0 !important; width: 100% !important;\n        }\n        .content {\n            padding: 0 !important;\n        }\n        .content-wrap {\n            padding: 10px !important;\n        }\n        .invoice {\n            width: 100% !important;\n        }\n    }\n</style>\n</head>\n\n<body itemscope itemtype="http://schema.org/EmailMessage" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: none; width: 100% !important; height: 100%; line-height: 1.6em; background-color: #f6f6f6; margin: 0;" bgcolor="#f6f6f6">\n\n<table class="body-wrap" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; width: 100%; background-color: #f6f6f6; margin: 0;" bgcolor="#f6f6f6"><tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0;" valign="top"></td>\n    <td class="container" width="600" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; display: block !important; max-width: 600px !important; clear: both !important; margin: 0 auto;" valign="top">\n        <div class="content" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; max-width: 600px; display: block; margin: 0 auto; padding: 20px;">\n            <table class="main" width="100%" cellpadding="0" cellspacing="0" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; border-radius: 3px; background-color: #fff; margin: 0; border: 1px solid #e9e9e9;" bgcolor="#fff"><tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="alert alert-warning" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 16px; vertical-align: top; color: #fff; font-weight: 500; text-align: center; border-radius: 3px 3px 0 0; background-color: #FF9F00; margin: 0; padding: 20px;" align="center" bgcolor="#FF9F00" valign="top">\n                You are over the number of widgets on your current plan\n            </td>\n            </tr><tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="content-wrap" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 20px;" valign="top">\n                <table width="100%" cellpadding="0" cellspacing="0" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">\n                    \n                    \n                        <tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="content-block" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">\n                        Upgrade now and you can get way, way more widgets.\n                        </td></tr>\n                    \n                        <tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="content-block" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">\n                        No I\'m serious, like, a ton more.\n                        </td></tr>\n                    \n                    \n                    <tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="content-block" itemprop="handler" itemscope itemtype="http://schema.org/HttpActionHandler" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">\n                        <a href="http://localhost:8080/upgrade" class="btn-primary" itemprop="url" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; color: #FFF; text-decoration: none; line-height: 2em; font-weight: bold; text-align: center; cursor: pointer; display: inline-block; border-radius: 5px; text-transform: capitalize; background-color: #348eda; margin: 0; border-color: #348eda; border-style: solid; border-width: 10px 20px;">action_text</a>\n                    </td>\n                    </tr>\n                </tr><tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"><td class="content-block" style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;" valign="top">\n                    --The Team\n                </td>\n                </tr></table></td>\n            </tr></table>\n            <div class="footer"\n                 style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; width: 100%; clear: both; color: #999; margin: 0; padding: 20px;">\n                <table width="100%"\n                       style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">\n                    <tr style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">\n                        <td class="aligncenter content-block"\n                            style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 12px; vertical-align: top; color: #999; text-align: center; margin: 0; padding: 0 0 20px;"\n                            align="center" valign="top">Sent by the Acme Corporation</td>\n                    </tr>\n                </table>\n            </div>\n        </div>\n    </td>\n    <td style="font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0;" valign="top"></td>\n</tr></table></body>\n</html>'})

    def _test_sending(self, engine):
        mailer = templatemail.TemplateMail(template_dirs=[_test_template_dir], delivery_engine=engine)
        result = mailer.send_email(
            to_addresses=['test@example.com'],
            from_address='from@example.com',
            template_name='mailgun-transactional/alert.html',
            subject='You are over the number of widgets',
            signature='--The Team',
            action_link="http://localhost:8080/upgrade",
            action_text="Upgrade Now",
            warning_text="You are over the number of widgets on your current plan",
            details="Upgrade now and you can get way, way more widgets.\nNo I'm serious, like, a ton more.",
            footer='Sent by the Acme Corporation'
        )

    def _get_smtp_engine(self, security=templatemail.engines.smtp.SMTPSecurity.NONE):
        engine = templatemail.engines.smtp.SMTPDeliveryEngine(
            host='localhost',
            port=25,
            security=security,
            username='test',
            password='test'
        )
        return engine
