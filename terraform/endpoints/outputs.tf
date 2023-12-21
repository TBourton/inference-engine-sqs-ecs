output "endpoints" {
  value       = { for k, v in module.endpoints : k => v }
  description = "All outputs from endpoints module."
}

output "vpc_id" {
  value       = data.aws_vpc.existing_vpc.id
  description = "Used VPC ID"
}

output "subnet_ids" {
  value       = data.aws_subnets.default.ids
  description = "Subnet IDs"
}

output "vpc_endpoint_ids" {
  value       = { for k, v in module.endpoints.endpoints : k => v.id }
  description = "Created VPC endpoint IDs"
}
