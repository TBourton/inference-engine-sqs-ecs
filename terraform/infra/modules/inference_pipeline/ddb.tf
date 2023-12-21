# https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table

module "dynamodb_table" { # tfsec:ignore:aws-dynamodb-enable-recovery

  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = ">= 3.2.0"

  attributes = [
    {
      name = "message_id"
      type = "S"
    }
  ]
  deletion_protection_enabled    = var.dynamodb_deletion_protection_enabled
  hash_key                       = "message_id"
  name                           = "${var.name}-results"
  point_in_time_recovery_enabled = var.dynamodb_point_in_time_recovery_enabled
  server_side_encryption_enabled = true
  tags                           = local.tags
  ttl_attribute_name             = "expiration" # Needs to match code
  ttl_enabled                    = true
}
