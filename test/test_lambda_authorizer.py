import unittest
from unittest.mock import patch
from moto import mock_aws
import boto3

import lambda_functions.authorizer as authorizer  # Adjust path as needed

class TestLambdaAuthorizer(unittest.TestCase):
    @mock_aws
    def test_authorizer_allow(self):
        ssm = boto3.client("ssm", region_name="us-east-1")
        ssm.put_parameter(
            Name="/auth/users/user1",
            Value="enabled",
            Type="String"
        )

        event = {
            "headers": {
                "authorization": "user1"
            },
            "routeArn": "arn:aws:execute-api::example"
        }

        response = authorizer.lambda_handler(event, {})
        print(response["isAuthorized"])
        self.assertTrue(response["isAuthorized"])
        self.assertEqual(response["context"]["user"], "user1")

    @mock_aws
    def test_authorizer_deny(self):
        # No SSM parameter created for this user
        event = {
            "headers": {
                "authorization": "unknown_user"
            },
            "routeArn": "arn:aws:execute-api::example"
        }

        response = authorizer.lambda_handler(event, {})
        self.assertFalse(response["isAuthorized"])
        self.assertEqual(response["context"]["user"], "unknown_user")

    @mock_aws
    def test_authorizer_no_header(self):
        event = {
            "headers": {},  # No 'authorization'
            "routeArn": "arn:aws:execute-api::example"
        }

        response = authorizer.lambda_handler(event, {})
        self.assertFalse(response["isAuthorized"])
        self.assertEqual(response["context"]["user"], "anonymous")