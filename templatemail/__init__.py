"""
Template-based email system for Python.
"""
import logging
import os
from collections import namedtuple
from typing import List

import jinja2

RenderedResult = namedtuple('RenderedResult', ('subject', 'text_body', 'html_body'))
_dir_path = os.path.dirname(os.path.realpath(__file__))
_included_template_dir = os.path.join(_dir_path, 'templates')


class DeliveryEngineNotInstalled(Exception):
    """
    This exception is raised when you attempt to use TemplateMail without a delivery engine installed.
    """


class DeliveryNotMade(Exception):
    """
    Called when a delivery cannot be made
    """
    def __init__(self, details, response=None):
        self.details = details
        self.response = response


class TemplateMail:
    def __init__(self, template_dirs: List[str] = None, delivery_engine=None, logger=None):
        """
        :param template_dirs: Directories containing templates.
        """
        _template_dirs = [_included_template_dir] + template_dirs if template_dirs else [_included_template_dir]
        for path in _template_dirs:
            assert os.path.exists(path)
            assert os.path.isdir(path)

        self.template_environment = jinja2.Environment(
            undefined=jinja2.StrictUndefined,
            loader=jinja2.FileSystemLoader(_template_dirs)
        )

        self.delivery_engine = delivery_engine

        self.logger = logger or logging.getLogger('templatemail')

    def render(self, template_name: str, *args, **kwargs) -> RenderedResult:
        content = self._render_partial(template_name, 'subject', *args, **kwargs)
        text_body = self._render_partial(template_name, 'text_body', *args, **kwargs)
        html_body = self._render_partial(template_name, 'html_body', *args, **kwargs)

        return RenderedResult(content, text_body, html_body)

    def _render_partial(self, template_name: str, block: str, *args, **kwargs, ) -> str:
        render_template = self.template_environment.get_template(f'_render_{block}.html')
        kwargs['templatemail__base_template'] = template_name
        content = render_template.render(*args, **kwargs)
        return content.strip()

    def send_email(self, from_address: str, to_addresses: List[str], template_name: str, dry_run=False, *args,
                   **kwargs):
        if not (self.delivery_engine or dry_run):
            raise DeliveryEngineNotInstalled

        rendered_email = self.render(template_name=template_name, *args, **kwargs)

        if not dry_run:
            self.delivery_engine.send_simple_message(
                from_address=from_address,
                to_addresses=to_addresses,
                subject=rendered_email.subject,
                text_body=rendered_email.text_body,
                html_body=rendered_email.html_body)
        self.log_email(
            from_address=from_address,
            to_addresses=to_addresses,
            template_name=template_name,
            dry_run=dry_run
        )

    def log_email(self, from_address: str, to_addresses: List[str], template_name: str, dry_run: bool):
        prefix = "[Dry run] " if dry_run else ''
        self.logger.info(f'{prefix}Sending {template_name} to {to_addresses} from {from_address}')


__all__ = ['TemplateMail', 'DeliveryEngineNotInstalled', 'DeliveryNotMade']
