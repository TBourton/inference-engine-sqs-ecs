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
    key     = "terraform.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}

locals {
  name = "inference-${terraform.workspace}"
  tags = {
    "ManagedBy"   = "terraform"
    "Environment" = terraform.workspace
    "ProjectName" = local.name
  }
}

data "aws_vpc" "existing_vpc" {
  id = var.vpc_id
}

data "aws_ecr_repository" "ecr" {
  name = var.ecr
}


module "inference_pipeline" {
  source = "./modules/inference_pipeline"

  tags   = local.tags
  name   = local.name
  vpc_id = data.aws_vpc.existing_vpc.id

  ecr                                              = data.aws_ecr_repository.ecr.name
  container_tag                                    = var.container_tag
  container_environment                            = [{ name = "FUNCTION_PROC_TIME", value = tostring(var.avg_msg_proc_time_seconds) }]
  subnet_ids                                       = var.subnet_ids
  vpc_endpoint_ids_to_associate_to_ecs_sg          = [var.sqs_vpc_endpoint_id]
  rollback                                         = var.rollback
  cpu                                              = var.cpu
  memory                                           = var.memory
  enable_autoscaling                               = var.enable_autoscaling
  service_autoscaling_min_capacity                 = var.service_autoscaling_min_capacity
  service_autoscaling_max_capacity                 = var.service_autoscaling_max_capacity
  desired_count                                    = var.desired_count
  queue_backlog_target_value                       = var.approx_num_backlog_messages * var.avg_msg_proc_time_seconds
  compute_queue_backlog_lambda_invocation_interval = var.compute_queue_backlog_lambda_invocation_interval
  wait_for_steady_state                            = var.wait_for_steady_state
  service_est_secs_per_msg                         = var.avg_msg_proc_time_seconds
  heartbeat_visibility_timeout_seconds             = var.heartbeat_visibility_timeout_seconds
  heartbeat_interval                               = var.heartbeat_interval
  enable_ecs_scalein_protection                    = var.enable_ecs_scalein_protection

  dynamodb_deletion_protection_enabled    = var.dynamodb_deletion_protection_enabled
  dynamodb_point_in_time_recovery_enabled = var.dynamodb_point_in_time_recovery_enabled

  queue_content_based_deduplication = var.queue_content_based_deduplication
  queue_deduplication_scope         = var.queue_deduplication_scope
  queue_delay_seconds               = var.queue_delay_seconds
  queue_message_retention_seconds   = var.queue_message_retention_seconds
  queue_receive_wait_time_seconds   = var.queue_receive_wait_time_seconds
  queue_max_receive_count           = var.queue_max_receive_count
  queue_visibility_timeout_seconds  = var.queue_visibility_timeout_seconds
  dlq_delay_seconds                 = var.dlq_delay_seconds
  dlq_message_retention_seconds     = var.dlq_message_retention_seconds
  dlq_receive_wait_time_seconds     = var.dlq_receive_wait_time_seconds
  dlq_visibility_timeout_seconds    = var.dlq_visibility_timeout_seconds
}
