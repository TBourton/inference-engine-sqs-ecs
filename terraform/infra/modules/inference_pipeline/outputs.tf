output "sqs" {
  value       = { for k, v in module.sqs : k => v }
  description = "All outputs from sqs module."
}

output "dynamodb_table" {
  value       = { for k, v in module.dynamodb_table : k => v }
  description = "All outputs from dynamodb_table module."

}

output "ecs_cluster" {
  value = { for k, v in module.ecs_cluster : k => v }

  description = "All outputs from ecs_cluster module."
}

output "ecs_service" {
  value       = { for k, v in module.ecs_service : k => v }
  description = "All outputs from ecs_service module."

}

output "ecr_image_digest" {
  value       = data.aws_ecr_image.ecr_image.id
  description = "Digest associated with the given ECR image"
}

output "ecr_image_url" {
  value       = local.image_url
  description = "Image URL associated with the given ECR image"
}
