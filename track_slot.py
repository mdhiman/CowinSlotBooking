#!/usr/bin/env python3
'''
Script to track available vaccine doses for 18+.

Example Output:

    [2021-05-03 14:12:32.641999] [BBMP] #421758 Newbagalur Layout UPHC C 1@560084: 0 doses on 04-05-2021,0 doses on 05-05-2021,0 doses on 06-05-2021,0 doses on 07-05-2021,0 doses on 08-05-2021
[2021-05-03 14:12:32.642144] [BBMP] #563937 APOLLO MEDICAL CENTER P3@560066: 0 doses on 04-05-2021
[2021-05-03 14:12:32.642173] [BBMP] #569247 MANIPAL WHITEFIELD COVAXIN@560066: 0 doses on 04-05-2021,0 doses on 05-05-2021,0 doses on 06-05-2021,0 doses on 07-05-2021,0 doses on 08-05-2021
'''

import json
import time
from urllib import request
from datetime import datetime
from datetime import timedelta
from datetime import date

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CDN_URL='https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict'
sender_address = ''
sender_pass = ''
receiver_address = 'vatsala.charu93@gmail.com'

"""
If you are using gmail to send email, then you need to enable less secure apps, you can enable it from below link.

https://myaccount.google.com/lesssecureapps 
"""

def slot_predicate(slot):
    return slot['min_age_limit'] != 45 and slot['available_capacity']>0

def send_email(mail_content):
    
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Congratulations! Cowin Vaccine slots are available now.'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def render_center(center):
    dates = ','.join([
        '{} doses on {}'.format(slot['available_capacity'], slot['date'])
        for slot in center['sessions']
        if slot_predicate(slot)
    ])
    return '[{}] [{}] #{} {}@{}: {}'.format(
        datetime.now(),
        center['district_name'], center['center_id'], center['name'],
        center['pincode'], dates
    )

def find_centers_day(district_id, date):
    time.sleep(2)
    try:
        centers = json.loads(request.urlopen('{}?district_id={}&date={}'.format(
            CDN_URL,
            district_id,
            date.strftime("%d-%m-%Y")
        )).read())['centers']

        eligible_centers = [
            center
            for center in centers
            if any(
                slot
                for slot in center['sessions']
                if slot_predicate(slot)
            )
        ]
        mail_content=""
        for center in eligible_centers:
            curr_center=render_center(center)
            print(curr_center)
            mail_content+=curr_center+"\n"
        if mail_content:
            send_email(mail_content)


    except Exception as e:
        print("Failed to query for: {} @ {}".format(district_id, date), e)


def find_centers(district_id, days=10):
    today = date.today()
    find_centers_day(district_id, today + timedelta(days=1))

if __name__ == '__main__':
    district_ids = [
	#BBMP
	294
    ]
    while (1):
        for district_id in district_ids:
            find_centers(district_id)
        time.sleep(30)
