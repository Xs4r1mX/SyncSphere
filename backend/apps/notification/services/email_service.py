from apps.notification.services.template_service import TemplateService
from apps.notification.services.providers import BrevoProvider
from django.utils import timezone


class EmailService:

    @staticmethod
    def send_email(
        *,
        subject,
        recipient,
        html_template,
        text_template,
        context=None,
    ):
        """
        Generic email sender.
        """

        templates = TemplateService.render_email(
            html_template=html_template,
            text_template=text_template,
            context=context,
        )

        BrevoProvider.send_email(
            subject=subject,
            recipient=recipient,
            html_content=templates["html"],
            text_content=templates["text"],
        )