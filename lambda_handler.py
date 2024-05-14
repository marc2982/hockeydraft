#!/usr/bin/env python3
from datetime import datetime

import boto3

from app.csv_to_html import main

BUCKET_NAME = "playoff-pools"


def lambda_handler(event, context):
    current_year = datetime.today().year
    html, file_name = main(str(current_year))
    stream_to_s3(html, file_name)


def stream_to_s3(html: str, file_name: str):
    encoded_string = html.encode("utf-8")
    s3 = boto3.resource("s3")
    s3.Bucket(BUCKET_NAME).put_object(Key=file_name, Body=encoded_string)
