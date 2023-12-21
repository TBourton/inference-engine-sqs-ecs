<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.12.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.37.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.37.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_autoscaling"></a> [autoscaling](#module\_autoscaling) | ../ecs-sqs-autoscaling | n/a |
| <a name="module_dynamodb_table"></a> [dynamodb\_table](#module\_dynamodb\_table) | terraform-aws-modules/dynamodb-table/aws | >= 3.2.0 |
| <a name="module_ecs_cluster"></a> [ecs\_cluster](#module\_ecs\_cluster) | terraform-aws-modules/ecs/aws//modules/cluster | >= 5.0.1 |
| <a name="module_ecs_service"></a> [ecs\_service](#module\_ecs\_service) | terraform-aws-modules/ecs/aws//modules/service | >= 5.0.1 |
| <a name="module_sqs"></a> [sqs](#module\_sqs) | terraform-aws-modules/sqs/aws | >= 4.0.1 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.ecs_service_error](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.ecs_service_error](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_metric_alarm.ecs_service_error_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm) | resource |
| [aws_cloudwatch_metric_alarm.sqs_dead_letter_queue_alarm](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm) | resource |
| [aws_cloudwatch_metric_alarm.sqs_queue_no_running_tasks](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm) | resource |
| [aws_iam_policy.ddb_full](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.ecs_task_protection](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.sqs_receive](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role_policy_attachment.ddb_full](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ecs_task_protection](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.sqs_receive](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_security_group.ecs_service_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_security_group_rule.egress_vpc_endpoint](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule) | resource |
| [aws_security_group_rule.ingress_vpc_endpoint](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule) | resource |
| [aws_sns_topic.ecs_service_error](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_policy.ecs_service_error](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy) | resource |
| [aws_vpc_endpoint_security_group_association.sg_associate](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint_security_group_association) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_ecr_image.ecr_image](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecr_image) | data source |
| [aws_ecr_repository.ecr](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecr_repository) | data source |
| [aws_iam_policy_document.sns_topic_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_vpc.existing_vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc) | data source |
| [aws_vpc_endpoint.vpc_endpoints](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_compute_queue_backlog_lambda_invocation_interval"></a> [compute\_queue\_backlog\_lambda\_invocation\_interval](#input\_compute\_queue\_backlog\_lambda\_invocation\_interval) | Rate or cron expression to determine the interval for QueueBacklog metric refresh. | `string` | `"rate(1 minute)"` | no |
| <a name="input_container_environment"></a> [container\_environment](#input\_container\_environment) | List of environment variables to add to container. Each list entry should be of the form {name=X, value=y}. | `list(any)` | `[]` | no |
| <a name="input_container_tag"></a> [container\_tag](#input\_container\_tag) | Container tag in ECR. If null, latest image tag is used. | `string` | `null` | no |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | Number of cpu units used by the ECS task. | `number` | `1024` | no |
| <a name="input_desired_count"></a> [desired\_count](#input\_desired\_count) | Number of instances of the task definition to place and keep running. Defaults to 0 | `number` | `1` | no |
| <a name="input_dlq_delay_seconds"></a> [dlq\_delay\_seconds](#input\_dlq\_delay\_seconds) | The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes) | `number` | `5` | no |
| <a name="input_dlq_message_retention_seconds"></a> [dlq\_message\_retention\_seconds](#input\_dlq\_message\_retention\_seconds) | The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days) | `number` | `1209600` | no |
| <a name="input_dlq_receive_wait_time_seconds"></a> [dlq\_receive\_wait\_time\_seconds](#input\_dlq\_receive\_wait\_time\_seconds) | The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds) | `number` | `5` | no |
| <a name="input_dlq_visibility_timeout_seconds"></a> [dlq\_visibility\_timeout\_seconds](#input\_dlq\_visibility\_timeout\_seconds) | The visibility timeout for the queue. An integer from 0 to 43200 (12 hours) | `number` | `30` | no |
| <a name="input_dynamodb_deletion_protection_enabled"></a> [dynamodb\_deletion\_protection\_enabled](#input\_dynamodb\_deletion\_protection\_enabled) | Enables deletion protection for table | `bool` | `true` | no |
| <a name="input_dynamodb_point_in_time_recovery_enabled"></a> [dynamodb\_point\_in\_time\_recovery\_enabled](#input\_dynamodb\_point\_in\_time\_recovery\_enabled) | Enables point in time recovery for table | `bool` | `false` | no |
| <a name="input_ecr"></a> [ecr](#input\_ecr) | ECR name | `string` | n/a | yes |
| <a name="input_enable_autoscaling"></a> [enable\_autoscaling](#input\_enable\_autoscaling) | Determines whether to enable autoscaling for the service. | `bool` | `true` | no |
| <a name="input_enable_ecs_scalein_protection"></a> [enable\_ecs\_scalein\_protection](#input\_enable\_ecs\_scalein\_protection) | Enable ECS scale in task protection. | `bool` | `true` | no |
| <a name="input_heartbeat_interval"></a> [heartbeat\_interval](#input\_heartbeat\_interval) | The interval to use for the Consumer heartbeat. This should be set ~= (heartbeat\_visibility\_timeout\_seconds / 3). A float as a string. | `number` | `10` | no |
| <a name="input_heartbeat_visibility_timeout_seconds"></a> [heartbeat\_visibility\_timeout\_seconds](#input\_heartbeat\_visibility\_timeout\_seconds) | The visibility timeout that should be set by the Consumer heartbeat. An integer from 0 to 43200 (12 hours) as a string | `number` | `30` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Amount (in MiB) of memory used by the ECS task. | `number` | `4096` | no |
| <a name="input_metric_alarm_alarm_actions"></a> [metric\_alarm\_alarm\_actions](#input\_metric\_alarm\_alarm\_actions) | The list of actions to execute when this alarm transitions into an ALARM state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns. | `list(string)` | `[]` | no |
| <a name="input_metric_alarm_insufficient_data_actions"></a> [metric\_alarm\_insufficient\_data\_actions](#input\_metric\_alarm\_insufficient\_data\_actions) | The list of actions to execute when this alarm transitions into an INSUFFICIENT\_DATA state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns. | `list(string)` | `[]` | no |
| <a name="input_metric_alarm_ok_actions"></a> [metric\_alarm\_ok\_actions](#input\_metric\_alarm\_ok\_actions) | The list of actions to execute when this alarm transitions into an OK state from any other state. Each action is specified as an Amazon Resource Name (ARN). For example a list of SNS topic arns. | `list(string)` | `[]` | no |
| <a name="input_name"></a> [name](#input\_name) | Project name | `string` | `"inference"` | no |
| <a name="input_queue_backlog_target_value"></a> [queue\_backlog\_target\_value](#input\_queue\_backlog\_target\_value) | Queue backlog (in seconds) to maintain for the service when under maximum load. Queue backlog is defined as (metric*secs\_per\_msg/num\_tasks). Defaults to 600 seconds (10 minutes). | `number` | `0` | no |
| <a name="input_queue_content_based_deduplication"></a> [queue\_content\_based\_deduplication](#input\_queue\_content\_based\_deduplication) | Enables content-based deduplication for FIFO queues | `bool` | `true` | no |
| <a name="input_queue_deduplication_scope"></a> [queue\_deduplication\_scope](#input\_queue\_deduplication\_scope) | Specifies whether message deduplication occurs at the message group or queue level (messageGroup or queue) | `string` | `"messageGroup"` | no |
| <a name="input_queue_delay_seconds"></a> [queue\_delay\_seconds](#input\_queue\_delay\_seconds) | The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes) | `number` | `5` | no |
| <a name="input_queue_max_receive_count"></a> [queue\_max\_receive\_count](#input\_queue\_max\_receive\_count) | The max receive count for a message before being dead-lettered | `number` | `10` | no |
| <a name="input_queue_message_retention_seconds"></a> [queue\_message\_retention\_seconds](#input\_queue\_message\_retention\_seconds) | The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days) | `number` | `86400` | no |
| <a name="input_queue_receive_wait_time_seconds"></a> [queue\_receive\_wait\_time\_seconds](#input\_queue\_receive\_wait\_time\_seconds) | The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds) | `number` | `5` | no |
| <a name="input_queue_visibility_timeout_seconds"></a> [queue\_visibility\_timeout\_seconds](#input\_queue\_visibility\_timeout\_seconds) | The visibility timeout for the queue. An integer from 0 to 43200 (12 hours). If Consumer does not use a heartbeat, this should be set >~ max amount of time a Consumer can run for. With a heartbeat it can be set lower as the heartbeat can signal whether the Consumer process is alive or not, in this case, this value acts as an initial visibility timeout. | `number` | `30` | no |
| <a name="input_rollback"></a> [rollback](#input\_rollback) | Whether deployment\_circuit\_breaker should rollback | `bool` | `false` | no |
| <a name="input_service_autoscaling_max_capacity"></a> [service\_autoscaling\_max\_capacity](#input\_service\_autoscaling\_max\_capacity) | Maximum number of tasks to run in ECS service | `number` | `10` | no |
| <a name="input_service_autoscaling_min_capacity"></a> [service\_autoscaling\_min\_capacity](#input\_service\_autoscaling\_min\_capacity) | Minimum number of tasks to run in ECS service | `number` | `1` | no |
| <a name="input_service_autoscaling_rampup_capacity"></a> [service\_autoscaling\_rampup\_capacity](#input\_service\_autoscaling\_rampup\_capacity) | Number of tasks to start as the immediate response to a QueueRequiresConsumer non-zero value. | `number` | `1` | no |
| <a name="input_service_autoscaling_scalein_cooldown"></a> [service\_autoscaling\_scalein\_cooldown](#input\_service\_autoscaling\_scalein\_cooldown) | Number of seconds to wait after a scaling operation before a scale-in operation can take place. | `number` | `60` | no |
| <a name="input_service_autoscaling_scaleout_cooldown"></a> [service\_autoscaling\_scaleout\_cooldown](#input\_service\_autoscaling\_scaleout\_cooldown) | Number of seconds to wait after a scaling operation before a scale-out operation can take place. | `number` | `60` | no |
| <a name="input_service_est_secs_per_msg"></a> [service\_est\_secs\_per\_msg](#input\_service\_est\_secs\_per\_msg) | Non-negative integer that represents the estimated number of seconds it takes the service to consume a single message from its queue. | `number` | `1` | no |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | Subnet ids in VPC | `list(string)` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A mapping of tags to assign to all resources | `map(string)` | `{}` | no |
| <a name="input_vpc_endpoint_ids_to_associate_to_ecs_sg"></a> [vpc\_endpoint\_ids\_to\_associate\_to\_ecs\_sg](#input\_vpc\_endpoint\_ids\_to\_associate\_to\_ecs\_sg) | List of VPC endpoint ids that should be associated with the ECS service SG | `set(string)` | `[]` | no |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC id | `string` | n/a | yes |
| <a name="input_wait_for_steady_state"></a> [wait\_for\_steady\_state](#input\_wait\_for\_steady\_state) | Whether to wait for ECS steady state | `bool` | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_dynamodb_table"></a> [dynamodb\_table](#output\_dynamodb\_table) | All outputs from dynamodb\_table module. |
| <a name="output_ecr_image_digest"></a> [ecr\_image\_digest](#output\_ecr\_image\_digest) | Digest associated with the given ECR image |
| <a name="output_ecr_image_url"></a> [ecr\_image\_url](#output\_ecr\_image\_url) | Image URL associated with the given ECR image |
| <a name="output_ecs_cluster"></a> [ecs\_cluster](#output\_ecs\_cluster) | All outputs from ecs\_cluster module. |
| <a name="output_ecs_service"></a> [ecs\_service](#output\_ecs\_service) | All outputs from ecs\_service module. |
| <a name="output_sqs"></a> [sqs](#output\_sqs) | All outputs from sqs module. |
<!-- END_TF_DOCS -->
