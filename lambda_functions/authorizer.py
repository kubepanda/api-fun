import boto3
import os

ssm = boto3.client("ssm")

def lambda_handler(event, context):
    username = event["headers"].get("authorization")

    if not username:
        return _deny("anonymous", event["routeArn"])

    try:
        param_name = f"/auth/users/{username}"
        param = ssm.get_parameter(Name=param_name, WithDecryption=False)
        if param["Parameter"]["Value"] == "enabled":
            return _allow(username, event["routeArn"])
        else:
            return _deny(username, event["routeArn"])
    except ssm.exceptions.ParameterNotFound:
        return _deny(username, event["routeArn"])

def _allow(principal_id, resource):
    return {
        "isAuthorized": True,
        "context": {
            "user": principal_id
        }
    }

def _deny(principal_id, resource):
    return {
        "isAuthorized": False,
        "context": {
            "user": principal_id
        }
    }
