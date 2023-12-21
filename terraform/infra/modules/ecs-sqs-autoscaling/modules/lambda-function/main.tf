terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.37.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.3.0"
    }

  }
}

data "archive_file" "compute_queue_backlog" {
  type        = "zip"
  source_file = "${path.module}/compute_queue_backlog.py"
  output_path = "${path.module}/compute_queue_backlog.zip"
}

resource "aws_lambda_function" "compute_queue_backlog" { # tfsec:ignore:aws-lambda-enable-tracing
  filename      = data.archive_file.compute_queue_backlog.output_path
  function_name = var.name
  role          = aws_iam_role.compute_queue_backlog.arn
  handler       = "compute_queue_backlog.lambda_handler"

  source_code_hash = filebase64sha256(data.archive_file.compute_queue_backlog.output_path)

  layers = var.lambda_layers

  environment {
    variables = {
      LOG_LEVEL = var.log_level
    }
  }

  runtime = "python3.7"

  tags = merge(
    {
      Name        = var.name
      Description = "Computes the QueueBacklog and QueueRequiresConsumer metrics."
    },
    var.tags
  )
}

#
#   Lambda Role
#
resource "aws_iam_role" "compute_queue_backlog" {
  name               = "${var.name}-role"
  description        = "Grants ${var.name} lambda access to necessary AWS services."
  assume_role_policy = data.aws_iam_policy_document.compute_queue_backlog_trust_relationship.json

  tags = merge(
    {
      Name        = "${var.name}-role"
      Description = "Grants ${var.name} lambda access to necessary AWS services."
    },
    var.execution_role_tags
  )
}

#
#   Trust policy
#
data "aws_iam_policy_document" "compute_queue_backlog_trust_relationship" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "compute_queue_backlog" {
  name   = "${var.name}-role-policy"
  role   = aws_iam_role.compute_queue_backlog.name
  policy = data.aws_iam_policy_document.compute_queue_backlog.json
}

resource "aws_iam_role_policy" "compute_queue_backlog_sqs" {
  name   = "${var.name}-role-policy-sqs"
  role   = aws_iam_role.compute_queue_backlog.name
  policy = data.aws_iam_policy_document.compute_queue_backlog_sqs.json
}

data "aws_iam_policy_document" "compute_queue_backlog" {
  statement {
    effect = "Allow"

    actions = [
      "cloudwatch:PutMetricData",
      "ecs:DescribeServices",
    ]

    resources = ["*"] #tfsec:ignore:aws-iam-no-policy-wildcards
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup"]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.name}:*"]
  }
}

data "aws_iam_policy_document" "compute_queue_backlog_sqs" {
  statement {
    effect = "Allow"

    actions = [
      "sqs:GetQueueUrl",
      "sqs:GetQueueAttributes",
    ]

    resources = ["*"] #tfsec:ignore:aws-iam-no-policy-wildcards
  }
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
