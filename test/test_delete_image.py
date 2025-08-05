import unittest
from unittest.mock import patch, MagicMock
import sys
import lambda_functions
import os 

class TestDeleteImage(unittest.TestCase):

    @patch("lambda_functions.handler_delete.TABLE")
    @patch("lambda_functions.handler_delete.s3")
    def test_delete_image_success(self, mock_s3, mock_table):
        mock_table.get_item.return_value = {
            "Item": {"image_id": "img123", "s3_key": "img123.jpg", "uploader": "user1"}
        }

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

        response = lambda_functions.handler_delete.lambda_handler(event, {})

        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Deleted successfully", response["body"])

        mock_s3.delete_object.assert_called_once_with(
            Bucket=lambda_functions.handler_delete.BUCKET, Key="img123.jpg"
        )
        mock_table.delete_item.assert_called_once_with(Key={"image_id": "img123"})

    @patch("lambda_functions.handler_delete.TABLE")
    def test_delete_image_not_found(self, mock_table):
        mock_table.get_item.return_value = {}

        event = {
            "pathParameters": {"image_id": "missing123"}
        }

        response = lambda_functions.handler_delete.lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Image not found", response["body"])


    
    @patch("lambda_functions.handler_delete.TABLE")
    @patch("lambda_functions.handler_delete.s3")
    def test_delete_image_not_authorized(self, mock_s3, mock_table):
        mock_table.get_item.return_value = {
            "Item": {"image_id": "img123", "s3_key": "img123.jpg", "uploader": "user1"}
        }

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

        response = lambda_functions.handler_delete.lambda_handler(event, {})

        self.assertEqual(response["statusCode"], 403)
        self.assertIn("not authorized", str(response["body"]))
