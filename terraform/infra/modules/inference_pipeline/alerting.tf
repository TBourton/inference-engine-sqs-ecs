######### ECS ###############
# https://serverfault.com/questions/1012603/create-a-cloudwatch-alarm-when-an-ecs-service-unable-to-consistently-start-tasks

resource "aws_cloudwatch_event_rule" "ecs_service_error" {
  name        = "${module.ecs_service.name}-ecs-service-error-event-rule"
  description = "Rule for catching unable to start service tasks"
  event_pattern = jsonencode({
    "source" : ["aws.ecs"],
    "detail-type" : ["ECS Service Action"],
    "resources" : [module.ecs_service.id]
    "detail" : {
      "clusterArn" : [module.ecs_cluster.arn]
      "eventType" : ["WARN", "ERROR"]
    }
  })
}

resource "aws_cloudwatch_event_target" "ecs_service_error" {
  rule      = aws_cloudwatch_event_rule.ecs_service_error.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.ecs_service_error.arn
}


resource "aws_sns_topic" "ecs_service_error" { #tfsec:ignore:aws-sns-enable-topic-encryption
  name = "${var.name}-ecs-service-errors"
}

resource "aws_sns_topic_policy" "ecs_service_error" {
  arn    = aws_sns_topic.ecs_service_error.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [aws_sns_topic.ecs_service_error.arn]
  }
}


resource "aws_cloudwatch_metric_alarm" "ecs_service_error_events" {
  alarm_name                = "${module.ecs_service.name}-ecs-service-error"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "TriggeredRules"
  namespace                 = "AWS/Events"
  period                    = 30
  statistic                 = "SampleCount"
  threshold                 = 1
  datapoints_to_alarm       = 1
  alarm_description         = "Number of failed deployments for ${module.ecs_service.name}"
  treat_missing_data        = "ignore"
  alarm_actions             = var.metric_alarm_alarm_actions
  ok_actions                = var.metric_alarm_ok_actions
  insufficient_data_actions = var.metric_alarm_insufficient_data_actions
  dimensions = {
    RuleName = aws_cloudwatch_event_rule.ecs_service_error.name
  }
  tags = local.tags
}

resource "aws_cloudwatch_metric_alarm" "sqs_dead_letter_queue_alarm" {
  alarm_name                = "${module.sqs.dead_letter_queue_name}-alarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = 60
  statistic                 = "Average"
  threshold                 = 1
  datapoints_to_alarm       = 1
  alarm_description         = "Number of messages in the dead-letter queue is greater than zero"
  treat_missing_data        = "missing"
  alarm_actions             = var.metric_alarm_alarm_actions
  ok_actions                = var.metric_alarm_ok_actions
  insufficient_data_actions = var.metric_alarm_insufficient_data_actions
  dimensions = {
    QueueName = module.sqs.dead_letter_queue_name
  }
  tags = local.tags
}

resource "aws_cloudwatch_metric_alarm" "sqs_queue_no_running_tasks" {
  alarm_name                = "${module.sqs.queue_name}-messages-with-no-running-tasks-alarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 5
  threshold                 = 1
  datapoints_to_alarm       = 1
  alarm_description         = "Number of messages in queue with no tasks running"
  treat_missing_data        = "missing"
  alarm_actions             = var.metric_alarm_alarm_actions
  ok_actions                = var.metric_alarm_ok_actions
  insufficient_data_actions = var.metric_alarm_insufficient_data_actions

  metric_query {
    id          = "e1"
    expression  = "IF(m1>0 AND m2<1, m1, 0)"
    label       = "Number of messages when no task running"
    return_data = "true"
    period      = 60
  }

  metric_query {
    id = "m1"

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = 60
      stat        = "Average"
      unit        = "Count"
      dimensions = {
        QueueName = module.sqs.queue_name
      }
    }
  }

  metric_query {
    id = "m2"

    metric {
      metric_name = "RunningTaskCount"
      namespace   = "ECS/ContainerInsights"
      period      = 60
      stat        = "Average"
      unit        = "Count"

      dimensions = {
        ServiceName = module.ecs_service.name
        ClusterName = module.ecs_cluster.name

      }
    }
  }
  tags = local.tags
}
