import logging

import bleach
from jinja2 import BaseLoader
from jinja2.sandbox import SandboxedEnvironment
from markupsafe import Markup

logger = logging.getLogger(__name__)


class TextFormatter:
    def __init__(self):
        self.env = SandboxedEnvironment(loader=BaseLoader(), autoescape=True)
        self.env.filters.clear()
        self.env.tests.clear()
        self.env.globals.clear()

        self.allowed_tags = ["p", "b", "i", "u", "ul", "li", "br", "strong", "em"]
        self.allowed_attributes = {"*": ["style", "class"]}

    def format_string(self, template_str: str, values=None, **kwargs) -> str:
        """Regular template rendering with escaping"""
        template = self.env.from_string(template_str)
        return template.render(values or {}, **kwargs)

    def format_email(
        self,
        subject_template: str,
        base_template: str,
        content_template: str,
        data=None,
        **kwargs,
    ) -> tuple[str, str]:
        """
        Special handling for email templates where content needs to be rendered as HTML
        """
        # First render the content template
        content = self.format_string(content_template, data, **kwargs)

        # Clean the HTML but don't escape it
        clean_content = bleach.clean(
            content,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True,
        )

        # Mark the cleaned HTML as safe using Markup
        safe_content = Markup(clean_content)

        rendered_subject_template = self.format_string(subject_template, data, **kwargs)

        # Create new env just for HTML template
        html_env = SandboxedEnvironment(loader=BaseLoader(), autoescape=True)
        html_env.filters["safe"] = lambda x: (
            x if isinstance(x, Markup) else Markup(str(x))
        )

        # Render base template with the safe content
        template = html_env.from_string(base_template)
        rendered_base_template = template.render(
            data={
                "message": safe_content,
                "title": rendered_subject_template,
                "unsubscribe_link": kwargs.get("unsubscribe_link", ""),
            }
        )

        return rendered_subject_template, rendered_base_template
