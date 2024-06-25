Templates are written in [Jinja2](http://jinja.pocoo.org/docs/2.10/). Each email template should include the following Jinja2 blocks:

* `subject` renders the template subject.
* `text_body` renders the text version of a template
* `html_body` renders the HTML version.

Upon rendering, the subject, text, and html versions are all stripped of leading and trailing whitespace.

Consider the following example, `welcome.html`:

```jinja2
{% block subject %}Welcome to our system {{ name }}!{% endblock %}

{% block text_body %}
Hello, {{ name }}

Welcome to the system. To get started, click on this confirmation link:

{{ confirm_link }}
{% endblock %}

{% block html_body %}
<html>
<body>
<h1>Hello, {{ name }}</h1>
<p>Welcome to the system.</p>
<p>To get started, please <a href="{{ confirm_link }}">confirm your signup</a>.
{% endblock %}
```

One template renders the HTML, Text, and Subject of an email, putting all user-facing considerations into one template file and out of the source code. Using this template would be as simple as follows:

```python
import templatemail

mailer = templatemail.TemplateMail(
    template_dirs=['email_templates'],
    delivery_engine=engine)

# Using the two, you can send templates.
template_name = 'welcome.html'
mailer.send_email(
    to_addresses=['test@example.com'],
    from_address='from@example.com',
    template_name=template_name,
    confirm_link='https://example.com/confirm/123',
    name='Joe User'
)
```

Notice that the `confirm_link` and `name` variables are passed in and used by each block. 

You can use all Jinja2 features with TemplateMail, including inheritance, macros, and filters. The only requirement for use is, your templates should define the three blocks mentioned above.


