module "autoscaling" {
  source = "../ecs-sqs-autoscaling"
  count  = var.enable_autoscaling ? 1 : 0

  cluster_name                       = module.ecs_cluster.name
  service_name                       = module.ecs_service.name
  service_max_capacity               = var.service_autoscaling_max_capacity
  service_min_capacity               = var.service_autoscaling_min_capacity
  service_est_secs_per_msg           = var.service_est_secs_per_msg
  service_scalein_cooldown           = var.service_autoscaling_scalein_cooldown
  service_scaleout_cooldown          = var.service_autoscaling_scaleout_cooldown
  service_rampup_capacity            = var.service_autoscaling_rampup_capacity
  queue_name                         = module.sqs.queue_name
  queue_arn                          = module.sqs.queue_arn
  queue_url                          = module.sqs.queue_url
  queue_backlog_target_value         = var.queue_backlog_target_value
  lambda_name                        = "${var.name}-lambda"
  lambda_invocation_interval         = var.compute_queue_backlog_lambda_invocation_interval
  lambda_tags                        = local.tags
  cloudwatch_event_rule_tags         = local.tags
  queue_requires_consumer_alarm_tags = local.tags
  # depends_on_service = var.create_service ? aws_ecs_service.main[0] : null
  queue_owner_aws_account_id = data.aws_caller_identity.current.account_id
}
