provider "aws" {
  region = "ap-northeast-2"  # 원하는 리전으로 변경하세요.
  profile = "default"
}

resource "aws_lambda_function" "example" {
  filename      = "lambda_function.zip"  # Lambda 함수 코드를 포함하는 ZIP 파일을 지정하세요.
  function_name = "upload-download-presigned-url"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"  # Python 파일명 및 핸들러 함수명을 지정하세요.
  runtime       = "python3.8"  # Python 런타임을 선택하세요.
}

# Lambda 함수에 대한 IAM 역할 생성
resource "aws_iam_role" "lambda_role" {
  name = "upload-download-presigned-url-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach1" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "attach2" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}


resource "aws_api_gateway_rest_api" "example" {
  name        = "upload-download-presigned-url-api"
  description = "Example API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  parent_id   = aws_api_gateway_rest_api.example.root_resource_id
  path_part   = "upload"

  
}

resource "aws_api_gateway_method" "get" {
  rest_api_id   = aws_api_gateway_rest_api.example.id
  resource_id   = aws_api_gateway_resource.root.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "example" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.get.http_method
  status_code = "200"

  # Method Response의 응답 모델 정의
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.example.function_name
  principal     = "apigateway.amazonaws.com"

  # API Gateway 리소스와 Lambda 함수 간의 연결을 설정합니다.
  source_arn = "${aws_api_gateway_rest_api.example.execution_arn}/*/${aws_api_gateway_method.get.http_method}${aws_api_gateway_resource.root.path}"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.example.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  content_handling = "CONVERT_TO_TEXT"

  # Lambda 함수와 API Gateway 간의 통합 설정
  uri = aws_lambda_function.example.invoke_arn
}

resource "aws_api_gateway_deployment" "example" {
  depends_on = [aws_lambda_permission.api_gateway, aws_api_gateway_rest_api.example]
  rest_api_id = aws_api_gateway_rest_api.example.id
  stage_name  = "v1"
}

output "api_endpoint" {
  value = "${aws_api_gateway_deployment.example.invoke_url}${aws_api_gateway_resource.root.path}"
}