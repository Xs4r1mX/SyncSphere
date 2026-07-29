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


    @classmethod
    def send_verification_email(
        cls,
        *,
        user,
        verification_url,
    ):
        """
        Send account verification email.
        """

        cls.send_email(
            subject="Verify your SyncSphere account",
            recipient=user.email,

            html_template=(
                "emails/auth/verify_email.html"
            ),

            text_template=(
                "emails/auth/verify_email.txt"
            ),

            context={
                "first_name": user.first_name,
                "verification_url": verification_url,
                "expiry_hours": 24,
            },
        )