from datetime import datetime, timedelta, timezone
import boto3
import os
import render

ses = boto3.client("ses")
ec2 = boto3.client('ec2')

subject = os.getenv("subject")
source = os.getenv("source")
addresses = os.environ.get("addresses", "").split()
max_days = int(os.environ.get("max_days", "30"))

limit_date = datetime.now(tz=timezone.utc) - timedelta(days=max_days)


def handler(event, context):
    imgs = ec2.describe_images(Owners=['self'])['Images']

    old_imgs = [
        x for x in imgs
        if datetime.strptime(x["CreationDate"], "%Y-%m-%dT%H:%M:%S.%f%z") < limit_date
    ]

    res = ses.send_email(
        Source=source,
        Destination={
            'ToAddresses': addresses
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Html': {
                    'Data': render.html(old_imgs),
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    return res