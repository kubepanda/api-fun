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

    s3.delete_object(Bucket=BUCKET, Key=item["s3_key"])
    TABLE.delete_item(Key={"image_id": image_id})

    return {"statusCode": 200, "body": "Deleted successfully"} """

import os
import json
import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

TABLE = dynamodb.Table(os.environ["TABLE_NAME"])
BUCKET = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    image_id = event["pathParameters"]["image_id"]

    # Extract the user from the Lambda authorizer
    user = event.get("requestContext", {}).get("authorizer", {}).get("lambda", {}).get("user", "unknown")
    # Get image metadata
    item = TABLE.get_item(Key={"image_id": image_id}).get("Item")

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Image not found"})
        }

    # Authorization check: only uploader can delete
    if item.get("uploader") != user:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "You are not authorized to delete this image"})
        }

    # Proceed with deletion
    s3.delete_object(Bucket=BUCKET, Key=item["s3_key"])
    TABLE.delete_item(Key={"image_id": image_id})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Deleted successfully"})
    }
