from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class BrevoProvider:

    @staticmethod
    def send_email(
        *,
        subject,
        recipient,
        html_content,
        text_content,
    ):
        """
        Send email using Brevo SMTP.
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send()