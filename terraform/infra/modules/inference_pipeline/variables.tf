variable "tags" {
  type        = map(string)
  description = "A mapping of tags to assign to all resources"
  default     = {}
}

variable "name" {
  description = "Project name"
  type        = string
  default     = "inference"
}

variable "vpc_id" {
  description = "VPC id"
  type        = string
}

# ################ ECS ################
variable "ecr" {
  description = "ECR name"
  type        = string
}

variable "vpc_endpoint_ids_to_associate_to_ecs_sg" {
  type        = set(string)
  description = "List of VPC endpoint ids that should be associated with the ECS service SG"
  default     = []
}

variable "container_tag" {
  description = "Container tag in ECR. If null, latest image tag is used."
  type        = string
  default     = null
}

variable "container_environment" {
  type        = list(any)
  description = "List of environment variables to add to container. Each list entry should be of the form {name=X, value=y}."
  default     = []
}

variable "subnet_ids" {
  description = "Subnet ids in VPC"
  type        = list(string)
}

variable "rollback" {
  description = "Whether deployment_circuit_breaker should rollback"
  type        = bool
  default     = false
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

variable "wait_for_steady_state" {
  description = "Whether to wait for ECS steady state"
  type        = bool
  default     = true
}

variable "service_autoscaling_scalein_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-in operation can take place."
  default     = 60
  type        = number
}

variable "service_autoscaling_scaleout_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-out operation can take place."
  default     = 60
  type        = number
}

variable "service_autoscaling_rampup_capacity" {
  description = "Number of tasks to start as the immediate response to a QueueRequiresConsumer non-zero value."
  default     = 1
  type        = number
}

variable "service_est_secs_per_msg" {
  description = "Non-negative integer that represents the estimated number of seconds it takes the service to consume a single message from its queue."
  type        = number
  default     = 1
}

variable "queue_backlog_target_value" {
  description = "Queue backlog (in seconds) to maintain for the service when under maximum load. Queue backlog is defined as (metric*secs_per_msg/num_tasks). Defaults to 600 seconds (10 minutes)."
  default     = 0
  type        = number
}

variable "compute_queue_backlog_lambda_invocation_interval" {
  description = "Rate or cron expression to determine the interval for QueueBacklog metric refresh."
  default     = "rate(1 minute)"
  type        = string
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


# ################ DynamoDB ################

variable "dynamodb_deletion_protection_enabled" {
  description = "Enables deletion protection for table"
  type        = bool
  default     = true
}

variable "dynamodb_point_in_time_recovery_enabled" {
  description = "Enables point in time recovery for table"
  type        = bool
  default     = false
}



# ################ SQS ################
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


# ################ Alerts ################
variable "metric_alarm_ok_actions" {
  type        = list(string)
  default     = []
  description = "The list of actions to execute when this alarm transitions into an OK state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns."
}

variable "metric_alarm_alarm_actions" {
  type        = list(string)
  default     = []
  description = "The list of actions to execute when this alarm transitions into an ALARM state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns."
}
variable "metric_alarm_insufficient_data_actions" {
  type        = list(string)
  default     = []
  description = "The list of actions to execute when this alarm transitions into an INSUFFICIENT_DATA state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns."
}
