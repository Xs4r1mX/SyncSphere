from django.template.loader import render_to_string


class TemplateService:

    @staticmethod
    def render_template(
        template_name,
        context=None
    ):
        """
        Render a django template.

        Example:
        emails/auth/verify_email.html
        """

        return render_to_string(
            template_name,
            context or {}
        )


    @classmethod
    def render_email(
        cls,
        html_template,
        text_template,
        context=None
    ):
        """
        Render both HTML and plain text versions.
        """

        html_content = cls.render_template(
            html_template,
            context
        )

        text_content = cls.render_template(
            text_template,
            context
        )

        return {
            "html": html_content,
            "text": text_content,
        }