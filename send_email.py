import os
import datetime
from cs50 import SQL
from email.message import EmailMessage
import smtplib

EMAIL_ADDRESS = os.getenv("MAIL_DEFAULT_SENDER")
EMAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# contacts = ['aumur.kop@gmail.com', 'test@example.com']

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///plant.db")

today = datetime.datetime.today().strftime('%Y-%m-%d')

user_id_list = db.execute("SELECT DISTINCT user_id FROM plants WHERE next = ?", today)

print(len(user_id_list))

if len(user_id_list) > 0:
    msg = EmailMessage()
    msg['Subject'] = 'Check out your plants!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'aumur.kop@gmail.com'

    msg.set_content('This is a plain text email')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

print(f'\n\n{today}\n\n')
print(f'\n\n{user_id_list}\n\n')
# print(f'\n\n{user_ids}\n\n')

# contacts = [d['email'] for d in email_list]
# print(f'\n\n{email_list}\n\n')