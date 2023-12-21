variable "cluster_name" {
  description = "ECS cluster name. Uses default cluster if not supplied."
  type        = string
}

variable "service_name" {
  description = "ECS service name"
  type        = string
}

variable "max_capacity" {
  description = "Maximum number of tasks that the autoscaling policy can set for the service."
  default     = 1
  type        = number
}

variable "min_capacity" {
  description = "Minimum number of tasks that the autoscaling policy can set for the service."
  default     = 0
  type        = number
}

variable "queue_name" {
  description = "Name of the queue to compute QueueBacklog metric for."
  type        = string
}

variable "target_value" {
  description = "Queue backlog (in seconds) to maintain for the service when under maximum load. Defaults to 600 seconds (10 minutes)."
  default     = 600
  type        = number
}

variable "target_value_statistic" {
  description = "Metric statistic to use when aggregating QueueBacklog over a period."
  default     = "Average"
  type        = string
}

variable "scalein_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-in operation can take place."
  default     = 60
  type        = number
}

variable "scaleout_cooldown" {
  description = "Number of seconds to wait after a scaling operation before a scale-out operation can take place."
  default     = 60
  type        = number
}

variable "rampup_capacity" {
  description = "Number of tasks to start as the immediate response to a QueueRequiresConsumer non-zero value."
  default     = 1
  type        = number
}

variable "queue_requires_consumer_alarm_prefix" {
  description = "Prefix to apply to the QueueRequiresConsumer CloudWatch alarm, which may be necessary to ensure uniqueness in multi-environment deployments."
  default     = ""
  type        = string
}

variable "queue_requires_consumer_alarm_period" {
  description = "Number of seconds to aggregate QueueRequiresConsumer metric before testing against the alarm threshold."
  default     = 60
  type        = number
}

variable "queue_requires_consumer_alarm_statistic" {
  description = "Metric statistic to use when aggregating QueueBacklog over a period."
  default     = "Average"
  type        = string
}

variable "queue_requires_consumer_alarm_evaluation_periods" {
  description = "Number of periods to aggregate QueueRequiresConsumer metric over when comparing against the alarm threshold."
  default     = 1
  type        = number
}

variable "queue_requires_consumer_alarm_comparison_op" {
  description = "Operator to use when comparing QueueRequiresConsumer against the alarm threshold."
  default     = "GreaterThanThreshold"

  type = string
}

variable "queue_requires_consumer_alarm_tags" {
  description = "Map of AWS tags to add to the alarm. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well."
  default     = {}
  type        = any
}

variable "depends_on_service" {
  description = "aws_ecs_service object that you can pass to the module to ensure autoscaling resources are recreated properly."
  type        = any
  default     = null
}
