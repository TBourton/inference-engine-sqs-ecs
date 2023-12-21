
variable "cluster_name" {
  description = "ECS cluster name. Uses default cluster if not supplied."
  type        = string
}

variable "service_name" {
  description = "ECS service name"
  type        = string
}

variable "service_max_capacity" {
  description = "Maximum number of tasks that the autoscaling policy can set for the service."
  default     = 10
  type        = number
}

variable "service_min_capacity" {
  description = "Minimum number of tasks that the autoscaling policy can set for the service."
  default     = 1
  type        = number
}

variable "service_est_secs_per_msg" {
  description = "Non-negative integer that represents the estimated number of seconds it takes the service to consume a single message from its queue."
  type        = number
}

variable "service_scalein_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-in operation can take place."
  default     = 60
  type        = number
}

variable "service_scaleout_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-out operation can take place."
  default     = 30
  type        = number
}

variable "service_rampup_capacity" {
  description = "Number of tasks to start as the immediate response to a QueueRequiresConsumer non-zero value."
  default     = 1
  type        = number
}

variable "metric_name" {
  description = "The name of the metric the lambda uses to derive the queue backlog value."
  default     = "ApproximateNumberOfMessages"
  type        = string
}

variable "queue_name" {
  description = "Name of the queue to compute QueueBacklog metric for. For the 'AWS/SQS' metric provider, the name must be the name of the SQS queue. It can be any value you wish for other metric providers."
  type        = string
}

variable "queue_url" {
  description = "Name of the queue URL"
  type        = string
}

variable "queue_arn" {
  description = "ARN of the queue"
  type        = string
}

variable "queue_backlog_target_value" {
  description = "Queue backlog (in seconds) to maintain for the service when under maximum load. Queue backlog is defined as (metric*secs_per_msg/num_tasks). Defaults to 600 seconds (10 minutes)."
  default     = 0
  type        = number
}

variable "queue_requires_consumer_alarm_period" {
  description = "Number of seconds to aggregate QueueRequiresConsumer metric before testing against the alarm threshold."
  default     = 60
  type        = number
}

variable "queue_requires_consumer_alarm_evaluation_periods" {
  description = "Number of periods to aggregate QueueRequiresConsumer metric over when comparing against the alarm threshold."
  default     = 1
  type        = number
}

variable "lambda_name" {
  description = "The lambda function name."
  default     = "compute-queue-backlog"
  type        = string
}

variable "lambda_log_level" {
  description = "Log level to use for Lambda logs. Accepts the standard Python log levels."
  default     = "INFO"
  type        = string
}

variable "lambda_tags" {
  description = "Map of AWS tags to add to the Lambda. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well."
  default     = {}
  type        = any
}

variable "lambda_invocation_interval" {
  description = "Rate or cron expression to determine the interval for QueueBacklog metric refresh."
  default     = "rate(1 minute)"
  type        = string
}

variable "cloudwatch_event_rule_tags" {
  description = "Map of AWS tags to add to the CloudWatch Event Rule that invokes the queue backlog lambda. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default."
  default     = {}
  type        = any
}

variable "queue_requires_consumer_alarm_tags" {
  description = "Map of AWS tags to add to the alarm. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well."
  default     = {}
  type        = any
}

variable "depends_on_service" {
  description = "aws_ecs_service object that you can pass to the module to ensure resources are recreated properly on service recreate."
  type        = any
  default     = null
}

variable "queue_owner_aws_account_id" {
  description = "AWS account id that provides the queue. If not provided, will use the caller's account id. Only valid for 'AWS/SQS' metric provider."
  default     = ""
  type        = string
}
