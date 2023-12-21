resource "aws_ssm_parameter" "producer_aws_access_key_id" {
  name        = "/inference/${terraform.workspace}/producer/aws_access_key_id"
  type        = "String"
  value       = resource.aws_iam_access_key.producer_user.id
  description = "AWS_ACCESS_KEY_ID for the producer user"
}


resource "aws_ssm_parameter" "producer_aws_secret_access_key" {
  name        = "/inference/${terraform.workspace}/inference/producer/aws_secret_access_key"
  type        = "SecureString"
  value       = resource.aws_iam_access_key.producer_user.secret
  description = "AWS_SECRET_ACCESS_KEY for the producer user"
}

resource "aws_ssm_parameter" "queue_name" {
  name        = "/inference/${terraform.workspace}/sqs/queue_name"
  type        = "String"
  value       = module.inference_pipeline.sqs.queue_name
  description = "SQS queue name"
}

resource "aws_ssm_parameter" "table_name" {
  name        = "/inference/${terraform.workspace}/dynamodb/table_name"
  type        = "String"
  value       = module.inference_pipeline.dynamodb_table.dynamodb_table_id
  description = "DynamoDB table name"
}
