from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_otp_email(email, otp_code, user=None):
    """
    Renders email/otp_template.html and sends an OTP verification email to the user.
    """
    subject = "Verify Your Account"
    context = {
        "user": user,
        "otp": otp_code,
        "year": datetime.now().year,
    }
    html_message = render_to_string("email/otp_template.html", context)
    plain_message = strip_tags(html_message)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", "noreply@attendance.com"))

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )
