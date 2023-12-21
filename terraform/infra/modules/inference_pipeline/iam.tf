resource "aws_iam_role_policy_attachment" "sqs_receive" {
  role       = module.ecs_service.tasks_iam_role_name
  policy_arn = aws_iam_policy.sqs_receive.arn
}


resource "aws_iam_role_policy_attachment" "ddb_full" {
  role       = module.ecs_service.tasks_iam_role_name
  policy_arn = aws_iam_policy.ddb_full.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_protection" {
  role       = module.ecs_service.tasks_iam_role_name
  policy_arn = aws_iam_policy.ecs_task_protection.arn
}


resource "aws_iam_policy" "ecs_task_protection" { # tfsec:ignore:aws-iam-no-policy-wildcards
  name_prefix = "ecs_task_protection"
  description = "Policy for consumer to change task protection."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecs:UpdateTaskProtection",
          "ecs:GetTaskProtection",
        ]
        Effect   = "Allow"
        Resource = "*"
        Condition = {
          "ArnEquals" : { "ecs:cluster" : module.ecs_cluster.arn },
        }
      }
    ]
  })
}

resource "aws_iam_policy" "sqs_receive" {
  name_prefix = "sqs_receive"
  description = "Policy for consumer to SQS receive."
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
        Resource = module.sqs.queue_arn
      },
    ]
  })
}



resource "aws_iam_policy" "ddb_full" {
  name_prefix = "ddb_full"
  description = "Policy for cosnumer to interact with DDB."
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
        Resource = module.dynamodb_table.dynamodb_table_arn
      },
    ]
  })
}
