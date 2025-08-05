import os
import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
TABLE = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    params = event.get("queryStringParameters", {}) or {}
    filter_tag = params.get("tag")
    filter_uploader = params.get("uploader")

    scan_kwargs = {}
    filter_expr = []

    if filter_tag:
        filter_expr.append(Attr("tags").contains(filter_tag))
    if filter_uploader:
        filter_expr.append(Attr("uploader").eq(filter_uploader))

    if filter_expr:
        scan_kwargs["FilterExpression"] = filter_expr[0]
        for expr in filter_expr[1:]:
            scan_kwargs["FilterExpression"] &= expr

    response = TABLE.scan(**scan_kwargs)
    return {
        "statusCode": 200,
        "body": json.dumps(response["Items"])
    }
