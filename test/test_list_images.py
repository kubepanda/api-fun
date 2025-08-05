import unittest
from unittest.mock import patch, MagicMock
import lambda_functions
import os

class TestListImages(unittest.TestCase):

    @patch("lambda_functions.handler_list.TABLE")
    def test_list_images_success(self, mock_table):
        mock_table.scan.return_value = {
            "Items": [{"image_id": "img123", "tags": ["cat"], "uploader": "user1"}]
        }

        event = {
            "queryStringParameters": {"tag": "cat", "uploader": "user1"}
        }

        response = lambda_functions.handler_list.lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("img123", response["body"])
        mock_table.scan.assert_called_once()
