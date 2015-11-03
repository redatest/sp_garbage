# -*- coding: utf-8 -*-

from os import path
from email.MIMEImage import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from django.conf import settings

def send_nice_email(template_name,
                    email_context,
                    subject,
                    recipients,
                    sender=None,
                    images=None,
                    fail_silently=False):
    """ Sends a multi-part e-mail with inline images with both HTML and Text.

    template_name must NOT contain an extension. Both HTML (.html) and
    TEXT (.txt) versions must exist, eg 'emails/my_nice_email' will use both
    my_nice_email.html and my_nice_email.txt.

    email_context should be a plain python dictionary. It is applied against
    both the email messages (templates) and the subject.

    subject can be plain text or a Django template string, eg:
        New Job: {{ job.id }} {{ job.title }}

    recipients can be either a string, eg 'a@b.com' or a list, eg:
        ['a@b.com', 'c@d.com']. Type conversion is done if needed.

    sender can be an e-mail, 'Name <email>' or None. If unspecified, the
    DEFAULT_FROM_EMAIL will be used.

    images must be provided as a tuple, with the absolute path, followed by the
    image name:
        (('/path/to/image1', 'img1'), ('/path/to/image2', 'img2'))
    They are then used in the templates like the following:
        <img src="cid:img1" />

    if fail_silently is False, exceptions will be raised if an error occurs.

    Please refer to the SMTP.sendmail documentation:
        http://docs.python.org/library/smtplib.html#smtplib.SMTP.sendmail

    """

    if not sender:
        sender = settings.DEFAULT_FROM_EMAIL

    context = Context(email_context)

    text_part = loader.get_template('%s.txt' % template_name).render(context)
    html_part = loader.get_template('%s.html' % template_name).render(context)
    subject_part = loader.get_template_from_string(subject).render(context)

    if type(recipients) != list:
        recipients = [recipients,]

    msg = EmailMultiAlternatives(subject_part, text_part, sender, recipients)
    msg.attach_alternative(html_part, 'text/html')

    if images:
        for file, name in images:
            # f = open(path.join(settings.MEDIA_ROOT, file), 'rb')
            f = open(file, 'rb')
            msgImage = MIMEImage(f.read())
            f.close()
            msgImage.add_header('Content-ID', '<%s>' % name)
            msg.attach(msgImage)

    return msg.send(fail_silently)
