""" import os
import json
import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
TABLE = dynamodb.Table(os.environ["TABLE_NAME"])
BUCKET = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    image_id = event["pathParameters"]["image_id"]
    item = TABLE.get_item(Key={"image_id": image_id}).get("Item")

    if not item:
        return {"statusCode": 404, "body": "Image not found"}

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": item["s3_key"]},
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"download_url": url})
    }
 """

import os
import json
import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

TABLE = dynamodb.Table(os.environ["TABLE_NAME"])
BUCKET = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    image_id = event["pathParameters"]["image_id"]

    # Extract username from authorizer
    user = event.get("requestContext", {}).get("authorizer", {}).get("lambda", {}).get("user", "unknown")

    # Get image metadata from DynamoDB
    item = TABLE.get_item(Key={"image_id": image_id}).get("Item")
    print("---------------------",item,user,image_id)

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Image not found"})
        }
    
    print(item.get("uploader"))

    # Check authorization: Only uploader can access
    if item.get("uploader") != user:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Unauthorized to access this image"})
        }

    # Generate pre-signed S3 URL
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": item["s3_key"]},
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"download_url": url})
    }
