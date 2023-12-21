resource "aws_iam_user" "producer_user" { # tfsec:ignore:aws-iam-no-user-attached-policies
  name          = "producer-user-${terraform.workspace}"
  force_destroy = false
}


resource "aws_iam_access_key" "producer_user" {
  user = aws_iam_user.producer_user.name
}

resource "aws_iam_user" "consumer_user" { # tfsec:ignore:aws-iam-no-user-attached-policies
  name          = "consumer-user-${terraform.workspace}"
  force_destroy = false
}


resource "aws_iam_access_key" "consumer_user" {
  user = aws_iam_user.consumer_user.name
}


resource "aws_iam_user_policy_attachment" "producer_ddb_read" {
  user       = aws_iam_user.producer_user.name
  policy_arn = aws_iam_policy.ddb_read.arn
}

resource "aws_iam_user_policy_attachment" "producer_sqs_publish" {
  user       = aws_iam_user.producer_user.name
  policy_arn = aws_iam_policy.sqs_publish.arn
}


resource "aws_iam_user_policy_attachment" "consumer_ddb_full" {
  user       = aws_iam_user.consumer_user.name
  policy_arn = aws_iam_policy.ddb_full.arn
}

resource "aws_iam_user_policy_attachment" "consumer_sqs_receive" {
  user       = aws_iam_user.consumer_user.name
  policy_arn = aws_iam_policy.sqs_receive.arn
}


resource "aws_iam_policy" "sqs_receive" {
  name_prefix = "sqs_receive"
  description = "Policy for consumer to SQS receive."
  tags        = local.tags
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:GetQueueAttributes",
          "sqs:DeleteMessage",
          "sqs:GetQueueUrl",
          "sqs:ListQueues",
          "sqs:ChangeMessageVisibility",
          "sqs:GetQueueAttributes",
        ]
        Effect   = "Allow"
        Resource = module.inference_pipeline.sqs.queue_arn
      },
    ]
  })
}

resource "aws_iam_policy" "ddb_full" {
  name_prefix = "ddb_full"
  description = "Policy for consumer to interact with DDB."
  tags        = local.tags
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeStream",
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:BatchWriteItem",
          "dynamodb:DeleteItem",
          "dynamodb:UpdateItem",
          "dynamodb:PutItem"
        ],
        Effect   = "Allow"
        Resource = module.inference_pipeline.dynamodb_table.dynamodb_table_arn
      },
    ]
  })
}

resource "aws_iam_policy" "sqs_publish" {
  name_prefix = "sqs_publish"
  description = "Policy for producer to SQS publish."
  tags        = local.tags
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ChangeMessageVisibility",
          "sqs:DeleteMessage",
          "sqs:SendMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl",
          "sqs:ListQueues",
          "sqs:SendMessageBatch",
          "sqs:GetQueueAttributes",
        ]
        Effect   = "Allow"
        Resource = module.inference_pipeline.sqs.queue_arn
      },
    ]
  })
}

resource "aws_iam_policy" "ddb_read" {
  name_prefix = "ddb_read"
  description = "Policy for producer to read DDB table."
  tags        = local.tags
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeStream",
          "dynamodb:DescribeTable",
        ]
        Effect   = "Allow"
        Resource = module.inference_pipeline.dynamodb_table.dynamodb_table_arn
      },
    ]
  })
}
