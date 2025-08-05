from unittest import TestCase
from unittest.mock import patch, MagicMock
import json

import lambda_functions.handler_view  # Adjust this import as needed

class TestViewImage(TestCase):
    @patch("lambda_functions.handler_view.TABLE")
    @patch("lambda_functions.handler_view.s3")
    def test_get_image_success(self, mock_s3, mock_table):
        # Mock the image metadata from DynamoDB
        mock_table.get_item.return_value = {
            "Item": {
                "image_id": "img123",
                "tags": ["cat"],
                "uploader": "user1",
                "s3_key": "images/img123.jpg"
            }
        }

        # Mock the pre-signed S3 URL
        mock_s3.generate_presigned_url.return_value = "https://mocked-s3-url.com/img123.jpg"

        # Simulated API Gateway event with authorizer info
        event = {
            "requestContext": {
                "authorizer": {
                    "lambda": {
                        "user": "user1"
                    }
                }
            },
            "pathParameters": {"image_id": "img123"}
        }

        response = lambda_functions.handler_view.lambda_handler(event, {})

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("download_url", body)
        self.assertIn("mocked-s3-url", body["download_url"])

        # Ensure correct methods were called
        mock_table.get_item.assert_called_once_with(Key={"image_id": "img123"})
        mock_s3.generate_presigned_url.assert_called_once()


    @patch("lambda_functions.handler_view.TABLE")
    @patch("lambda_functions.handler_view.s3")
    def test_get_image_not_found(self, mock_s3, mock_table):
        # Mock the image metadata from DynamoDB
        mock_table.get_item.return_value = {}

        # Mock the pre-signed S3 URL
        mock_s3.generate_presigned_url.return_value = "https://mocked-s3-url.com/img123.jpg"

        # Simulated API Gateway event with authorizer info
        event = {
            "requestContext": {
                "authorizer": {
                    "lambda": {
                        "user": "user1"
                    }
                }
            },
            "pathParameters": {"image_id": "img124"}
        }

        response = lambda_functions.handler_view.lambda_handler(event, {})

        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertIn("not", str(body))
        

    @patch("lambda_functions.handler_view.TABLE")
    @patch("lambda_functions.handler_view.s3")
    def test_get_image_success(self, mock_s3, mock_table):
        # Mock the image metadata from DynamoDB
        mock_table.get_item.return_value = {
            "Item": {
                "image_id": "img123",
                "tags": ["cat"],
                "uploader": "user1",
                "s3_key": "images/img123.jpg"
            }
        }

        # Mock the pre-signed S3 URL
        mock_s3.generate_presigned_url.return_value = "https://mocked-s3-url.com/img123.jpg"

        # Simulated API Gateway event with authorizer info
        event = {
            "requestContext": {
                "authorizer": {
                    "lambda": {
                        "user": "user2"
                    }
                }
            },
            "pathParameters": {"image_id": "img123"}
        }

        response = lambda_functions.handler_view.lambda_handler(event, {})

        self.assertEqual(response["statusCode"], 403)
        body = json.loads(response["body"])
        self.assertIn("Unauthorized", str(body))

        # Ensure correct methods were called
        mock_table.get_item.assert_called_once_with(Key={"image_id": "img123"})
