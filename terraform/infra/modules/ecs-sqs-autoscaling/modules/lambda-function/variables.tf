variable "name" {
  description = "The lambda function name."
  type        = string
  default     = "compute-queue-backlog"
}

variable "log_level" {
  description = "Log level to use for Lambda logs. Accepts the standard Python log levels."
  default     = "INFO"
  type        = string
}

variable "tags" {
  description = "Map of AWS tags to add to the Lambda. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well."
  default     = {}
  type        = any
}

variable "lambda_layers" {
  description = "Additional lambda layers to add to the lambda."
  default     = []
  type        = any
}


variable "execution_role_tags" {
  description = "Map of AWS tags to add to the execution role. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well."
  default     = {}
  type        = any
}
