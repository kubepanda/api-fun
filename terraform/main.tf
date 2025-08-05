provider "aws" {
  region = "eu-north-1"
  
}

resource "aws_s3_bucket" "image_bucket" {
  bucket = "image-bucket-segregations"
}

resource "aws_dynamodb_table" "metadata_table" {
  name           = "ImagesMetadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "image_id"
  attribute {
    name = "image_id"
    type = "S"
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exddrole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "basic_policy" {
  name = "api-sslambda-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = [
          aws_s3_bucket.image_bucket.arn,
          "${aws_s3_bucket.image_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["dynamodb:*"]
        Resource = aws_dynamodb_table.metadata_table.arn
      },
      {
        Effect: "Allow",
        Action: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource: "*"
      },
      {
      Effect = "Allow"
      Action = ["ssm:GetParameter"]
      Resource = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/auth/users/*"
    }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.basic_policy.arn
}

resource "aws_lambda_function" "upload_image" {
  function_name = "upload_image"
  filename      = data.archive_file.upload_zip.output_path
  handler       = "handler_upload.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.upload_zip.output_path)
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec_role.arn
  timeout       = 15
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.bucket
      TABLE_NAME  = aws_dynamodb_table.metadata_table.name
    }
  }
}

resource "aws_apigatewayv2_api" "api" {
  name          = "ImageUploadAPI"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "upload_integration" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.upload_image.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "upload_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /upload"
  target    = "integrations/${aws_apigatewayv2_integration.upload_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.lambda_auth.id
  authorization_type = "CUSTOM"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload_image.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

data "archive_file" "upload_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions"
  output_path = "${path.module}/lambda_upload.zip"
  excludes    = ["handler_view.py", "handler_list.py", "handler_delete.py"]
}

data "archive_file" "list_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions"
  output_path = "${path.module}/lambda_list.zip"
  excludes    = ["handler_upload.py", "handler_view.py", "handler_delete.py"]
}

data "archive_file" "view_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions"
  output_path = "${path.module}/lambda_view.zip"
  excludes    = ["handler_upload.py", "handler_list.py", "handler_delete.py"]
}

data "archive_file" "delete_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions"
  output_path = "${path.module}/lambda_delete.zip"
  excludes    = ["handler_upload.py", "handler_list.py", "handler_view.py"]
}

resource "aws_lambda_function" "list_images" {
  function_name = "list_images"
  filename      = data.archive_file.list_zip.output_path
  handler       = "handler_list.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.list_zip.output_path)
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.metadata_table.name
    }
  }
}

resource "aws_lambda_function" "view_image" {
  function_name = "view_image"
  filename      = data.archive_file.view_zip.output_path
  handler       = "handler_view.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.view_zip.output_path)
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.bucket
      TABLE_NAME  = aws_dynamodb_table.metadata_table.name
    }
  }
}

resource "aws_lambda_function" "delete_image" {
  function_name = "delete_image"
  filename      = data.archive_file.delete_zip.output_path
  handler       = "handler_delete.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.delete_zip.output_path)
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.bucket
      TABLE_NAME  = aws_dynamodb_table.metadata_table.name
    }
  }
}


# Integrations
resource "aws_apigatewayv2_integration" "list_integration" {
  api_id               = aws_apigatewayv2_api.api.id
  integration_type     = "AWS_PROXY"
  integration_uri      = aws_lambda_function.list_images.invoke_arn
  integration_method   = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "view_integration" {
  api_id               = aws_apigatewayv2_api.api.id
  integration_type     = "AWS_PROXY"
  integration_uri      = aws_lambda_function.view_image.invoke_arn
  integration_method   = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "delete_integration" {
  api_id               = aws_apigatewayv2_api.api.id
  integration_type     = "AWS_PROXY"
  integration_uri      = aws_lambda_function.delete_image.invoke_arn
  integration_method   = "POST"
  payload_format_version = "2.0"
}

# Routes
resource "aws_apigatewayv2_route" "list_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /images"
  target    = "integrations/${aws_apigatewayv2_integration.list_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.lambda_auth.id
  authorization_type = "CUSTOM"
}

resource "aws_apigatewayv2_route" "view_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /image/{image_id}"
  target    = "integrations/${aws_apigatewayv2_integration.view_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.lambda_auth.id
  authorization_type = "CUSTOM"
}

resource "aws_apigatewayv2_route" "delete_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "DELETE /image/{image_id}"
  target    = "integrations/${aws_apigatewayv2_integration.delete_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.lambda_auth.id
  authorization_type = "CUSTOM"
}

resource "aws_lambda_permission" "apigw_list" {
  statement_id  = "AllowAPIGatewayList"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_images.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_view" {
  statement_id  = "AllowAPIGatewayView"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.view_image.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_delete" {
  statement_id  = "AllowAPIGatewayDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_image.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}


data "archive_file" "authorizer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions"
  output_path = "${path.module}/lambda_authorizer.zip"
  excludes    = ["handler_upload.py", "handler_view.py", "handler_list.py", "handler_delete.py"]
}

resource "aws_lambda_function" "authorizer" {
  function_name = "image-api-authorizer"
  filename      = data.archive_file.authorizer_zip.output_path
  handler       = "authorizer.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.authorizer_zip.output_path)
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_exec_role.arn
}


data "aws_caller_identity" "current" {}

resource "aws_apigatewayv2_authorizer" "lambda_auth" {
  name                       = "LambdaUsernameAuthorizer"
  api_id                     = aws_apigatewayv2_api.api.id
  authorizer_type            = "REQUEST"
  authorizer_uri             = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.authorizer.arn}/invocations"
  identity_sources           = ["$request.header.Authorization"]
  authorizer_payload_format_version = "2.0"
  enable_simple_responses    = true
  authorizer_result_ttl_in_seconds = 0
}

resource "aws_lambda_permission" "auth_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGatewayAuthorizer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}


resource "aws_ssm_parameter" "user1" {
  name  = "/auth/users/user1"
  type  = "String"
  value = "enabled"
}

resource "aws_ssm_parameter" "user2" {
  name  = "/auth/users/user2"
  type  = "String"
  value = "enabled"
}
