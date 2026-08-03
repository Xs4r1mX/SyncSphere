from django.conf import settings
from apps.notification.services.template_service import TemplateService
from apps.notification.services.providers import BrevoProvider


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

        template_context = {
            "platform_logo_url": settings.PLATFORM_LOGO_URL,
            **(context or {}),
        }

        templates = TemplateService.render_email(
            html_template=html_template,
            text_template=text_template,
            context=template_context,
        )

        BrevoProvider.send_email(
            subject=subject,
            recipient=recipient,
            html_content=templates["html"],
            text_content=templates["text"],
        )