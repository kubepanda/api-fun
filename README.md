
# 🖼️ Image Upload & Management API

This project is a serverless REST API for uploading, listing, viewing, and deleting images with metadata, built on AWS Lambda, API Gateway, DynamoDB, and S3.

## 🚀 Features

- Upload images with metadata (tags, filename, uploader)
- List images with filters (`tag`, `uploader`)
- View/download image via signed S3 URL (secure access)
- Delete image (only by uploader)
- Lambda Authorizer using SSM for user access control
- Fully unit tested using `unittest`, `mock`, and `moto`

---

## 📦 Project Structure

```
.
├── lambda_functions/
│   ├── handler_upload.py
│   ├── handler_view.py
│   ├── handler_list.py
│   ├── handler_delete.py
│   └── authorizer.py
├── test/
│   ├── test_upload.py
│   ├── test_view.py
│   ├── test_list.py
│   ├── test_delete.py
│   └── test_lambda_authorizer.py
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│ 
├── README.md
└── requirements.txt
```

---

## 📘 API Reference

### 🔐 Authentication

All endpoints require an `Authorization` header with a valid username. Authorization is handled via a Lambda Authorizer that checks AWS SSM Parameter Store for enabled users.

```http
Authorization: user1
```

---

### Upload Image

`POST /upload`

Uploads an image with metadata. and also uses Authorization user as the uploader out of the box

#### Request
```json
{
  "image_base64": "<base64-image-data>",
  "metadata": {
    "filename": "cat.jpg",
    "tags": ["cat", "cute"],
    "uploader": "user1"
  }
}
```

#### Response
```json
{
  "message": "Image uploaded successfully",
  "image_id": "img123"
}
```

---

###  List Images
Allows to search by listing the items in dynamodb table using search parameters as tag and uploader
has no boundages on search items and gives the list of all the items in the table,
i allowed it so users can search what is there in the table 

`GET /list?tag=cat&uploader=user1`

Filters:
- `tag` (optional)
- `uploader` (optional)

#### Response
```json
[
  {
    "image_id": "img123",
    "filename": "cat.jpg",
    "tags": ["cat", "cute"],
    "uploader": "user1"
  }
]
```

---

###  View Image
Give a presigned s3 url with the image, provided the image is uploaded by the user who is authorizing the api gateway means the userid passed in the authorization header is validated against the uploader field from the dynamodb to check if the download url should be permitted else 403 unauthized entry error is returned


`GET /view/{image_id}`

Returns a pre-signed S3 URL.

#### Response
```json
{
  "download_url": "https://s3.amazonaws.com/yourbucket/..."
}
```

---

### ❌ Delete Image
Deletes the image, Give a presigned s3 url with the image, provided the image is uploaded by the user who is authorizing the api gateway means the userid passed in the authorization header is validated against the uploader field from the dynamodb to check if the download url should be permitted else 403 unauthized delete error is returned or if image id not found 404 is returned

`DELETE /delete/{image_id}`

Deletes the image from S3 and DynamoDB. Only the uploader is authorized.

#### Response
```json
{
  "message": "Deleted successfully"
}
```

---

## 🧪 Running Tests

All unit tests are in the `test/` directory. To run:
also $env:TABLE_NAME = "test-table"
$env:BUCKET_NAME = "image-bucket-segregations"
should be passed to the pytest

```bash
pip install -r requirements.txt
pytest test/
```

Mocks AWS services with `moto` and `unittest.mock`.

---

## 🔧 Deployment (Terraform)

1. Configure your variables in `terraform/variables.tf`
2. Deploy:

```bash
cd terraform/
terraform init
terraform apply
```

This will create:
- API Gateway with routes
- Lambda functions
- IAM roles
- DynamoDB table
- S3 bucket
- Lambda authorizer

---

## 📥 Example Upload Script

```python
import base64, json, requests

with open("cat.jpg", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "image_base64": encoded,
    "metadata": {
        "filename": "cat.jpg",
        "tags": ["cat", "cute"],
        "uploader": "user1"
    }
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "user1"
}

res = requests.post("https://<your-api>/upload", headers=headers, json=payload)
print(res.status_code, res.json())
```

---

## 🔐 Authorizer Logic

The Lambda Authorizer checks if a parameter exists in SSM:

```
/auth/users/user1 = enabled
```

Only enabled users are allowed access.
i have made two users user1 , user2 who are allowed entry in ssm parameter store

---


## 🧑‍💻 Author

Built with ❤️ using AWS by Shwetanshu singh
