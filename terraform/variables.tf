variable "region" {
  default = "eu-north-1"
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.api.api_endpoint
}