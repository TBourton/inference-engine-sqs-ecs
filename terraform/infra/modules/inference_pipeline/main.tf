terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.37.0"
    }
  }
}

locals {
  tags = merge(
    var.tags,
    { "ProjectName" = var.name },
    { "ManagedBy" = "terraform" },
  )

  queue_name = "${var.name}.fifo"
}


data "aws_caller_identity" "current" {}
