terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.37.0"
    }
  }
}


module "autoscale_service" {
  source = "./modules/service-autoscaling"

  cluster_name                                     = var.cluster_name
  service_name                                     = var.service_name
  max_capacity                                     = var.service_max_capacity
  min_capacity                                     = var.service_min_capacity
  queue_name                                       = var.queue_name
  target_value                                     = var.queue_backlog_target_value
  scalein_cooldown                                 = var.service_scalein_cooldown
  scaleout_cooldown                                = var.service_scaleout_cooldown
  rampup_capacity                                  = var.service_rampup_capacity
  queue_requires_consumer_alarm_prefix             = var.queue_name
  queue_requires_consumer_alarm_period             = var.queue_requires_consumer_alarm_period
  queue_requires_consumer_alarm_evaluation_periods = var.queue_requires_consumer_alarm_evaluation_periods
  queue_requires_consumer_alarm_tags               = var.queue_requires_consumer_alarm_tags

  depends_on_service = var.depends_on_service
}

module "compute_queue_backlog_lambda" {
  source = "./modules/lambda-function"

  name      = var.lambda_name
  log_level = var.lambda_log_level
  tags      = var.lambda_tags
}


# Create cloudwatch event resources to invoke the compute-queue-backlog lambda
resource "aws_cloudwatch_event_rule" "compute_queue_backlog" {
  name                = "${module.compute_queue_backlog_lambda.name}-${var.service_name}"
  description         = "Schedule execution of ${module.compute_queue_backlog_lambda.name} to compute queue backlog metrics for ${var.service_name} ${var.queue_name} queue."
  schedule_expression = var.lambda_invocation_interval

  tags = merge(
    {
      Name        = "${module.compute_queue_backlog_lambda.name}-${var.service_name}"
      Description = "Schedule execution of ${module.compute_queue_backlog_lambda.name} to compute queue backlog metrics for ${var.service_name} ${var.queue_name} queue."
    },
    var.cloudwatch_event_rule_tags
  )
}

resource "aws_cloudwatch_event_target" "compute_queue_backlog" {
  rule      = aws_cloudwatch_event_rule.compute_queue_backlog.name
  target_id = "${module.compute_queue_backlog_lambda.name}-${var.service_name}"
  arn       = module.compute_queue_backlog_lambda.arn
  input = templatefile(
    "${path.module}/files/cw_event_target_args.json.tpl",
    {
      cluster_name               = var.cluster_name,
      service_name               = var.service_name,
      metric_name                = var.metric_name,
      queue_name                 = var.queue_name,
      queue_owner_aws_account_id = var.queue_owner_aws_account_id != "" ? var.queue_owner_aws_account_id : data.aws_caller_identity.current.account_id,
      est_secs_per_msg           = var.service_est_secs_per_msg,
  })
}

resource "aws_lambda_permission" "compute_queue_backlog" {
  action        = "lambda:InvokeFunction"
  function_name = module.compute_queue_backlog_lambda.name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.compute_queue_backlog.arn
}

resource "aws_sqs_queue_policy" "main" {
  queue_url = var.queue_url
  policy    = data.aws_iam_policy_document.sqs.json
}

data "aws_iam_policy_document" "sqs" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:GetQueueUrl", "sqs:GetQueueAttributes"]
    resources = [var.queue_arn]

    principals {
      identifiers = [module.compute_queue_backlog_lambda.execution_role_arn]
      type        = "AWS"
    }
  }
}
data "aws_caller_identity" "current" {}
