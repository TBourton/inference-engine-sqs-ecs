provider "aws" {
  region = "eu-west-2"
}

terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.37.0"
    }
  }

  backend "s3" {
    bucket  = "my-s3-bucket"
    key     = "endpoints.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}

locals {
  tags = {
    "ManagedBy" = "terraform"
  }
}

data "aws_vpc" "existing_vpc" {
  id = var.vpc_id
}


data "aws_route_tables" "rts" {
  vpc_id = data.aws_vpc.existing_vpc.id
}


data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing_vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*utility subnet"]
  }
}

module "endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = ">= 4.0.2"

  endpoints = {
    dynamodb = {
      service_type    = "Gateway"
      service         = "dynamodb"
      route_table_ids = data.aws_route_tables.rts.ids
      tags            = { Name = "dynamodb-vpc-endpoint" }
    },
    sqs = {
      service_type        = "Interface"
      service             = "sqs"
      private_dns_enabled = true
      tags                = { Name = "sqs-vpc-endpoint" }
    },
  }
  subnet_ids = data.aws_subnets.default.ids
  tags       = local.tags
  vpc_id     = data.aws_vpc.existing_vpc.id
}
