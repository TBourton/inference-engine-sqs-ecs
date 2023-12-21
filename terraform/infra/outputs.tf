output "inference_pipeline_outputs" { # Export all outputs dynamically
  value       = { for k, v in module.inference_pipeline : k => v }
  description = "inference_pipeline module outputs."
}

output "producer_aws_access_key_id" {
  value       = aws_iam_access_key.producer_user.id
  description = "AWS_ACCESS_KEY_ID for the producer user"
}

output "producer_aws_secret_access_key" {
  value       = aws_iam_access_key.producer_user.secret
  sensitive   = true
  description = "AWS_SECRET_ACCESS_KEY for the producer user"
}


output "consumer_aws_access_key_id" {
  value       = aws_iam_access_key.consumer_user.id
  description = "AWS_ACCESS_KEY_ID for the consumer user"
}

output "consumer_aws_secret_access_key" {
  value       = aws_iam_access_key.consumer_user.secret
  sensitive   = true
  description = "AWS_SECRET_ACCESS_KEY for the consumer user"
}

output "ssm_producer_aws_access_key_id" {
  value       = aws_ssm_parameter.producer_aws_access_key_id.name
  description = "SSM parameter name for AWS_ACCESS_KEY_ID for the producer user"

}

output "ssm_producer_aws_secret_access_key" {
  value       = aws_ssm_parameter.producer_aws_secret_access_key.name
  description = "SSM parameter name for AWS_SECRET_ACCESS_KEY for the producer user"

}

output "ssm_queue_name" {
  value       = aws_ssm_parameter.queue_name.name
  description = "SSM parameter name for queue_name"

}
output "ssm_table_name" {
  value       = aws_ssm_parameter.table_name.name
  description = "SSM parameter name for DynamoDB table name."
}
