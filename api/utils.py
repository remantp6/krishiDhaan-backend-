import platform

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.utils import timezone

def send_otp(email, otp):
    subject = 'OTP Verification'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email

    platform_info = platform.platform()
    time = timezone.now()
    # get time only
    clock = time.strftime("%H:%M:%S")
    date = time.strftime("%B %d, %Y")

    

    # Render the HTML template
    html_content = render_to_string('email/otp.html', {'otp': otp, 'platform': platform_info, 'clock': clock, 'date': date})

    # Create the text content by stripping the HTML tags
    text_content = strip_tags(html_content)

    # Create the email message object
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, 'text/html')

    # Send the email
    email.send()

    # Return a response indicating the email was sent
    return HttpResponse('Email sent successfully.')


    