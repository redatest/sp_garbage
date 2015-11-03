#!/usr/bin/python
import os
import sys

destination = sys.argv[1]
content = sys.argv[2]


mail_from = "admin@speedjob.fr"
mail_to = destination
subject = "Speedjob: Envoie de candidature"
# subject = content

header = """From: {0}
To: {1}
Subject: {2}
MIME-Version: 1.0
Content-Type: text/html
charset= utf8
""".format(mail_from, mail_to, subject)

# msg = header + content + "MIME-Version: 1.0" + "Content-Type: text/html" + "charset=ISO-8859-1" 
msg = header + content

sendmail = os.popen("/usr/lib/sendmail -t", "w")
sendmail.write(msg)
sendmail.close()
