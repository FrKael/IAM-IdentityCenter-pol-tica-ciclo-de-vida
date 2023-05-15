import boto3
from datetime import datetime, timezone, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ses = boto3.client('ses')
iam = boto3.client('iam')

users = iam.list_users()

access_keys = []

def lambda_handler(event, context):
    for user in users['Users']:
        user_name = user['UserName']
        access_key_metadata = iam.list_access_keys(UserName=user_name)
        for metadata in access_key_metadata['AccessKeyMetadata']:
            access_key = metadata['AccessKeyId']
            create_date = metadata['CreateDate']
            status = metadata['Status']
            last_used = iam.get_access_key_last_used(AccessKeyId=access_key)
            if 'LastUsedDate' in last_used['AccessKeyLastUsed']:
                last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None)
                last_used_date_utc = last_used_date.astimezone(timezone.utc)
                current_date_utc = datetime.now(timezone.utc)
                inactivity_period = (current_date_utc - last_used_date_utc).days
            else:
                inactivity_period = 'N/A'
            access_keys.append({'User': user_name,  'LastUsedDate': last_used_date, 'InactivityPeriod': inactivity_period})

    df_access_keys = pd.DataFrame(access_keys)

    df_access_keys['LastUsedDate'] = df_access_keys['LastUsedDate'].apply(lambda x: x.strftime('%Y-%m-%d') if x is not None else None)

    df_access_keys['InactivityPeriod'] = df_access_keys['InactivityPeriod'].apply(lambda x: x.days if isinstance(x, timedelta) else x)

    inactive_keys = df_access_keys[pd.to_numeric(df_access_keys['InactivityPeriod'], errors='coerce') > 90]

    if len(inactive_keys) > 0:

        table_html = inactive_keys.to_html(index=False)

        subject = 'Inactive IAM Access Keys'
        body = '<html><body><p>The following IAM access keys have not been used for more than 90 days:</p>' + table_html + '</body></html>'
        sender = 'azeballos@argocloudsolutions.com.pe'
        recipients = ["azeballos@argocloudsolutions.com.pe"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            response = ses.send_raw_email(
                Source=sender,
                Destinations=recipients,
                RawMessage={'Data': msg.as_string()}
            )
            print('Email sent')
        except Exception as e:
            print('Error sending email:', e)
    else:
        print('No inactive access keys found')
