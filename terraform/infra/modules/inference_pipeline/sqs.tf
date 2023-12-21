# https://github.com/terraform-aws-modules/terraform-aws-sqs

module "sqs" {
  source  = "terraform-aws-modules/sqs/aws"
  version = ">= 4.0.1"

  content_based_deduplication     = var.queue_content_based_deduplication
  create                          = true
  create_dlq                      = true
  deduplication_scope             = var.queue_deduplication_scope
  delay_seconds                   = var.queue_delay_seconds
  dlq_content_based_deduplication = var.queue_content_based_deduplication
  dlq_deduplication_scope         = var.queue_deduplication_scope
  dlq_delay_seconds               = var.dlq_delay_seconds
  dlq_message_retention_seconds   = var.dlq_message_retention_seconds
  dlq_name                        = "dlq_${local.queue_name}"
  dlq_receive_wait_time_seconds   = var.dlq_receive_wait_time_seconds
  dlq_tags                        = local.tags
  dlq_visibility_timeout_seconds  = var.dlq_visibility_timeout_seconds
  fifo_queue                      = true
  fifo_throughput_limit           = "perMessageGroupId"
  message_retention_seconds       = var.queue_message_retention_seconds
  name                            = local.queue_name
  receive_wait_time_seconds       = var.queue_receive_wait_time_seconds
  redrive_policy = {
    maxReceiveCount = var.queue_max_receive_count
  }
  tags                       = local.tags
  visibility_timeout_seconds = var.queue_visibility_timeout_seconds
}
