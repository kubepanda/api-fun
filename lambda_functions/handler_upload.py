# lambda/handler.py

""" import json, uuid, base64
import boto3
import os
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET = os.environ["BUCKET_NAME"]
TABLE = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    body = json.loads(event["body"])
    image_data = base64.b64decode(body["image_base64"])
    metadata = body["metadata"]

    image_id = str(uuid.uuid4())
    s3_key = f"images/{image_id}.jpg"

    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=image_data)

    item = {
        "image_id": image_id,
        "filename": metadata.get("filename"),
        "upload_time": datetime.now(),
        "tags": metadata.get("tags", []),
        "uploader": metadata.get("uploader", "unknown"),
        "s3_key": s3_key,
    }

    TABLE.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": json.dumps({"image_id": image_id}),
    }
 """


# lambda/handler_upload.py

import json
import uuid
import base64
import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET = os.environ["BUCKET_NAME"]
TABLE = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    try:
        # Get the uploader from the authorizer context (set by Lambda authorizer)
        uploader = event.get("requestContext", {}).get("authorizer", {}).get("lambda", {}).get("user", "unknown")

        # Parse input
        body = json.loads(event["body"])
        image_data = base64.b64decode(body["image_base64"])
        metadata = body.get("metadata", {})

        # Generate ID and upload to S3
        image_id = str(uuid.uuid4())
        s3_key = f"images/{image_id}.jpg"

        s3.put_object(Bucket=BUCKET, Key=s3_key, Body=image_data)

        # Prepare metadata for DynamoDB
        item = {
            "image_id": image_id,
            "filename": metadata.get("filename", f"{image_id}.jpg"),
            "upload_time": datetime.now(),
            "tags": metadata.get("tags", []),
            "uploader": uploader,
            "s3_key": s3_key,
        }

        TABLE.put_item(Item=item)

        return {
            "statusCode": 201,
            "body": json.dumps({"image_id": image_id}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }