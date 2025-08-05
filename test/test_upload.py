import unittest
from unittest.mock import patch, MagicMock
import lambda_functions
import os
import json
import base64

class TestUploadImage(unittest.TestCase):

    
    @patch("lambda_functions.handler_upload.TABLE")
    @patch("lambda_functions.handler_upload.s3")
    def test_upload_image_success(self, mock_s3, mock_boto_client):
        image = b"fake image"
        encoded_image = base64.b64encode(image).decode("utf-8")
        
        event = {
           "requestContext": {
              "authorizer":{
                 "lambda":{
                    "user": "test-user"
                 }
              }
           },
            "body": json.dumps({ 
                    "image_base64": encoded_image,
                    "metadata": {
                            "filename": "cat.jpg",
                            "tags": ["cat", "cute"],
                            "uploader": "test-user"
                            }})
                }

        context = {}

        # Act
        response = lambda_functions.handler_upload.lambda_handler(event, context)

    
        # Parse the returned image_id
        response_body = json.loads(response["body"])
        image_id = response_body["image_id"]
        expected_s3_key = f"images/{image_id}.jpg"

        # Assert S3 upload call
        args, kwargs = mock_s3.put_object.call_args

        assert kwargs["Bucket"] == "image-bucket-segregations"
        assert kwargs["Key"] == expected_s3_key
        assert isinstance(kwargs["Body"], bytes)

        mock_boto_client.put_item.assert_called_once()
        args, kwargs = mock_boto_client.put_item.call_args

        item = kwargs["Item"]
        assert item["uploader"] == "test-user"
        assert item["image_id"] == image_id
        assert item["filename"] == "cat.jpg"
        assert item["s3_key"] == expected_s3_key

