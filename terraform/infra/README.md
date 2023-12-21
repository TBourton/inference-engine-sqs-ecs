<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.12.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.37.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.67.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_inference_pipeline"></a> [inference\_pipeline](#module\_inference\_pipeline) | ./modules/inference_pipeline | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_iam_access_key.consumer_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_access_key) | resource |
| [aws_iam_access_key.producer_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_access_key) | resource |
| [aws_iam_policy.ddb_full](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.ddb_read](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.sqs_publish](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.sqs_receive](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_user.consumer_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user.producer_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user_policy_attachment.consumer_ddb_full](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [aws_iam_user_policy_attachment.consumer_sqs_receive](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [aws_iam_user_policy_attachment.producer_ddb_read](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [aws_iam_user_policy_attachment.producer_sqs_publish](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy_attachment) | resource |
| [aws_ssm_parameter.producer_aws_access_key_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.producer_aws_secret_access_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.queue_name](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.table_name](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ecr_repository.ecr](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecr_repository) | data source |
| [aws_vpc.existing_vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_approx_num_backlog_messages"></a> [approx\_num\_backlog\_messages](#input\_approx\_num\_backlog\_messages) | Approximate number of acceptable backlogged messages before triggering autoscaling. Computed as queue\_backlog\_target\_value (seconds) / avg\_msg\_proc\_time\_seconds. | `number` | `1` | no |
| <a name="input_avg_msg_proc_time_seconds"></a> [avg\_msg\_proc\_time\_seconds](#input\_avg\_msg\_proc\_time\_seconds) | Average time Consumer needs to process a single message | `number` | `60` | no |
| <a name="input_compute_queue_backlog_lambda_invocation_interval"></a> [compute\_queue\_backlog\_lambda\_invocation\_interval](#input\_compute\_queue\_backlog\_lambda\_invocation\_interval) | Rate or cron expression to determine the interval for QueueBacklog metric refresh. | `string` | `"rate(1 minute)"` | no |
| <a name="input_container_tag"></a> [container\_tag](#input\_container\_tag) | Container tag in ECR | `string` | n/a | yes |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | Number of cpu units used by the ECS task. | `number` | `1024` | no |
| <a name="input_desired_count"></a> [desired\_count](#input\_desired\_count) | Number of instances of the task definition to place and keep running. Defaults to 0 | `number` | `1` | no |
| <a name="input_dlq_delay_seconds"></a> [dlq\_delay\_seconds](#input\_dlq\_delay\_seconds) | The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes) | `number` | `5` | no |
| <a name="input_dlq_message_retention_seconds"></a> [dlq\_message\_retention\_seconds](#input\_dlq\_message\_retention\_seconds) | The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days) | `number` | `1209600` | no |
| <a name="input_dlq_receive_wait_time_seconds"></a> [dlq\_receive\_wait\_time\_seconds](#input\_dlq\_receive\_wait\_time\_seconds) | The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds) | `number` | `5` | no |
| <a name="input_dlq_visibility_timeout_seconds"></a> [dlq\_visibility\_timeout\_seconds](#input\_dlq\_visibility\_timeout\_seconds) | The visibility timeout for the queue. An integer from 0 to 43200 (12 hours) | `number` | `30` | no |
| <a name="input_dynamodb_deletion_protection_enabled"></a> [dynamodb\_deletion\_protection\_enabled](#input\_dynamodb\_deletion\_protection\_enabled) | Enables deletion protection for table | `bool` | `false` | no |
| <a name="input_dynamodb_point_in_time_recovery_enabled"></a> [dynamodb\_point\_in\_time\_recovery\_enabled](#input\_dynamodb\_point\_in\_time\_recovery\_enabled) | Enables point in time recovery for table | `bool` | `false` | no |
| <a name="input_ecr"></a> [ecr](#input\_ecr) | ECR name | `string` | `"ct"` | no |
| <a name="input_enable_autoscaling"></a> [enable\_autoscaling](#input\_enable\_autoscaling) | Determines whether to enable autoscaling for the service. | `bool` | `true` | no |
| <a name="input_enable_ecs_scalein_protection"></a> [enable\_ecs\_scalein\_protection](#input\_enable\_ecs\_scalein\_protection) | Enable ECS scale in task protection. | `bool` | `true` | no |
| <a name="input_heartbeat_interval"></a> [heartbeat\_interval](#input\_heartbeat\_interval) | The interval to use for the Consumer heartbeat. This should be set ~= (heartbeat\_visibility\_timeout\_seconds / 3). A float as a string. | `number` | `10` | no |
| <a name="input_heartbeat_visibility_timeout_seconds"></a> [heartbeat\_visibility\_timeout\_seconds](#input\_heartbeat\_visibility\_timeout\_seconds) | The visibility timeout that should be set by the Consumer heartbeat. An integer from 0 to 43200 (12 hours) as a string | `number` | `30` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Amount (in MiB) of memory used by the ECS task. | `number` | `4096` | no |
| <a name="input_queue_content_based_deduplication"></a> [queue\_content\_based\_deduplication](#input\_queue\_content\_based\_deduplication) | Enables content-based deduplication for FIFO queues | `bool` | `true` | no |
| <a name="input_queue_deduplication_scope"></a> [queue\_deduplication\_scope](#input\_queue\_deduplication\_scope) | Specifies whether message deduplication occurs at the message group or queue level (messageGroup or queue) | `string` | `"messageGroup"` | no |
| <a name="input_queue_delay_seconds"></a> [queue\_delay\_seconds](#input\_queue\_delay\_seconds) | The time in seconds that the delivery of all messages in the queue will be delayed. An integer from 0 to 900 (15 minutes) | `number` | `5` | no |
| <a name="input_queue_max_receive_count"></a> [queue\_max\_receive\_count](#input\_queue\_max\_receive\_count) | The max receive count for a message before being dead-lettered | `number` | `10` | no |
| <a name="input_queue_message_retention_seconds"></a> [queue\_message\_retention\_seconds](#input\_queue\_message\_retention\_seconds) | The number of seconds Amazon SQS retains a message. Integer representing seconds, from 60 (1 minute) to 1209600 (14 days) | `number` | `86400` | no |
| <a name="input_queue_receive_wait_time_seconds"></a> [queue\_receive\_wait\_time\_seconds](#input\_queue\_receive\_wait\_time\_seconds) | The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning. An integer from 0 to 20 (seconds) | `number` | `5` | no |
| <a name="input_queue_visibility_timeout_seconds"></a> [queue\_visibility\_timeout\_seconds](#input\_queue\_visibility\_timeout\_seconds) | The visibility timeout for the queue. An integer from 0 to 43200 (12 hours). If Consumer does not use a heartbeat, this should be set >~ max amount of time a Consumer can run for. With a heartbeat it can be set lower as the heartbeat can signal whether the Consumer process is alive or not, in this case, this value acts as an initial visibility timeout. | `number` | `30` | no |
| <a name="input_rollback"></a> [rollback](#input\_rollback) | Whether deployment\_circuit\_breaker should rollback | `bool` | `true` | no |
| <a name="input_service_autoscaling_max_capacity"></a> [service\_autoscaling\_max\_capacity](#input\_service\_autoscaling\_max\_capacity) | Maximum number of tasks to run in ECS service | `number` | `10` | no |
| <a name="input_service_autoscaling_min_capacity"></a> [service\_autoscaling\_min\_capacity](#input\_service\_autoscaling\_min\_capacity) | Minimum number of tasks to run in ECS service | `number` | `1` | no |
| <a name="input_sqs_vpc_endpoint_id"></a> [sqs\_vpc\_endpoint\_id](#input\_sqs\_vpc\_endpoint\_id) | SQS VPC endpoint - to be associated with the ECS service SG | `string` | n/a | yes |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | List of subnets to use. Should be matching the endpoints stack. | `list(string)` | <pre>[<br>  "subnet-0420455530e05e0e6",<br>  "subnet-043d88697dd85a9bd",<br>  "subnet-0ba54d80bde8feb2c"<br>]</pre> | no |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC id | `string` | `"vpc-08fc6d74ba4394cdb"` | no |
| <a name="input_wait_for_steady_state"></a> [wait\_for\_steady\_state](#input\_wait\_for\_steady\_state) | Whether to wait for ECS steady state | `bool` | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_consumer_aws_access_key_id"></a> [consumer\_aws\_access\_key\_id](#output\_consumer\_aws\_access\_key\_id) | AWS\_ACCESS\_KEY\_ID for the consumer user |
| <a name="output_consumer_aws_secret_access_key"></a> [consumer\_aws\_secret\_access\_key](#output\_consumer\_aws\_secret\_access\_key) | AWS\_SECRET\_ACCESS\_KEY for the consumer user |
| <a name="output_inference_pipeline_outputs"></a> [inference\_pipeline\_outputs](#output\_inference\_pipeline\_outputs) | inference\_pipeline module outputs. |
| <a name="output_producer_aws_access_key_id"></a> [producer\_aws\_access\_key\_id](#output\_producer\_aws\_access\_key\_id) | AWS\_ACCESS\_KEY\_ID for the producer user |
| <a name="output_producer_aws_secret_access_key"></a> [producer\_aws\_secret\_access\_key](#output\_producer\_aws\_secret\_access\_key) | AWS\_SECRET\_ACCESS\_KEY for the producer user |
| <a name="output_ssm_producer_aws_access_key_id"></a> [ssm\_producer\_aws\_access\_key\_id](#output\_ssm\_producer\_aws\_access\_key\_id) | SSM parameter name for AWS\_ACCESS\_KEY\_ID for the producer user |
| <a name="output_ssm_producer_aws_secret_access_key"></a> [ssm\_producer\_aws\_secret\_access\_key](#output\_ssm\_producer\_aws\_secret\_access\_key) | SSM parameter name for AWS\_SECRET\_ACCESS\_KEY for the producer user |
| <a name="output_ssm_queue_name"></a> [ssm\_queue\_name](#output\_ssm\_queue\_name) | SSM parameter name for queue\_name |
| <a name="output_ssm_table_name"></a> [ssm\_table\_name](#output\_ssm\_table\_name) | SSM parameter name for DynamoDB table name. |
<!-- END_TF_DOCS -->
