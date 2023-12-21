variable "vpc_id" {
  type        = string
  description = "VPC id"
  default     = "vpc-08fc6d74ba4394cdb"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnets to use. Should be matching the endpoints stack."
  default = [
    "subnet-0420455530e05e0e6",
    "subnet-043d88697dd85a9bd",
    "subnet-0ba54d80bde8feb2c"
  ]
}

variable "sqs_vpc_endpoint_id" {
  type        = string
  description = "SQS VPC endpoint - to be associated with the ECS service SG"
}

variable "container_tag" {
  type        = string
  description = "Container tag in ECR"
}

variable "avg_msg_proc_time_seconds" {
  type        = number
  description = "Average time Consumer needs to process a single message"
  default     = 60
}

variable "ecr" {
  description = "ECR name"
  type        = string
  default     = "ct"
}

variable "rollback" {
  description = "Whether deployment_circuit_breaker should rollback"
  type        = bool
  default     = true
}

variable "cpu" {
  description = "Number of cpu units used by the ECS task."
  type        = number
  default     = 1024
}

variable "memory" {
  description = "Amount (in MiB) of memory used by the ECS task."
  type        = number
  default     = 4096
}

variable "enable_autoscaling" {
  description = "Determines whether to enable autoscaling for the service."
  type        = bool
  default     = true
}

variable "service_autoscaling_max_capacity" {
  description = "Maximum number of tasks to run in ECS service"
  type        = number
  default     = 10
}

variable "service_autoscaling_min_capacity" {
  description = "Minimum number of tasks to run in ECS service"
  type        = number
  default     = 1
}

variable "desired_count" {
  description = "Number of instances of the task definition to place and keep running. Defaults to 0"
  type        = number
  default     = 1
}

variable "approx_num_backlog_messages" {
  description = "Approximate number of acceptable backlogged messages before triggering autoscaling. Computed as queue_backlog_target_value (seconds) / avg_msg_proc_time_seconds."
  default     = 1
  type        = number
}

variable "compute_queue_backlog_lambda_invocation_interval" {
  description = "Rate or cron expression to determine the interval for QueueBacklog metric refresh."
  default     = "rate(1 minute)"
  type        = string
}

variable "wait_for_steady_state" {
  description = "Whether to wait for ECS steady state"
  type        = bool
  default     = true
}

variable "heartbeat_visibility_timeout_seconds" {
  description = "The visibility timeout that should be set by the Consumer heartbeat. An integer from 0 to 43200 (12 hours) as a string"
  default     = 30
  type        = number
}

variable "heartbeat_interval" {
  description = "The interval to use for the Consumer heartbeat. This should be set ~= (heartbeat_visibility_timeout_seconds / 3). A float as a string."
  default     = 10
  type        = number
}

variable "enable_ecs_scalein_protection" {
  description = "Enable ECS scale in task protection."
  default     = true
  type        = bool
}

variable "dynamodb_deletion_protection_enabled" {
  type        = bool
  default     = false
  description = "Enables deletion protection for table"
}


variable "dynamodb_point_in_time_recovery_enabled" {
  description = "Enables point in time recovery for table"
  type        = bool
  default     = false
}

variable "queue_content_based_deduplication" {
  description = "Enables content-based deduplication for FIFO queues"
  type        = bool
  default     = true
}

variable "queue_deduplication_scope" {
  description = "Specifies whether message deduplication occurs at the message group or queue level (messageGroup or queue)"
  type        = string
  default     = "messageGroup"
}

variable "queue_delay_seconds" {
  description = "The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes)"
  type        = number
  default     = 5
}

variable "queue_message_retention_seconds" {
  type        = number
  default     = 86400
  description = "The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days)"
}

variable "queue_receive_wait_time_seconds" {
  type        = number
  default     = 5
  description = "The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds)"
}

variable "queue_max_receive_count" {
  type        = number
  default     = 10
  description = "The max receive count for a message before being dead-lettered"
}

variable "queue_visibility_timeout_seconds" {
  description = "The visibility timeout for the queue. An integer from 0 to 43200 (12 hours). If Consumer does not use a heartbeat, this should be set >~ max amount of time a Consumer can run for. With a heartbeat it can be set lower as the heartbeat can signal whether the Consumer process is alive or not, in this case, this value acts as an initial visibility timeout."
  default     = 30
  type        = number
}

variable "dlq_delay_seconds" {
  description = "The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes)"
  type        = number
  default     = 5
}

variable "dlq_message_retention_seconds" {
  description = "The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days)"
  type        = number
  default     = 1209600
}

variable "dlq_receive_wait_time_seconds" {
  type        = number
  default     = 5
  description = "The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds)"
}

variable "dlq_visibility_timeout_seconds" {
  type        = number
  default     = 30
  description = "The visibility timeout for the queue. An integer from 0 to 43200 (12 hours)"
}
