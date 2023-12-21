# AWS ECS Service Autoscaling by QueueBacklog

Forked from: https://github.com/dailymuse/terraform-aws-ecs-queue-backlog-autoscaling

This repo contains a [Terraform](https://www.terraform.io/) module to autoscale
an AWS ECS service based on the `QueueBacklog` and `QueueRequiresConsumer` [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)
metrics. Additionally, this repo contains a nested module to deploy an
[AWS Lambda](https://aws.amazon.com/lambda/) function that computes the two metrics.


## How to use this Module

This repo has the following folder structure:

* [modules](modules): This folder contains modules to create resources that use and compute `QueueBacklog` and `QueueRequiresConsumer`.
* root: The root directory exposes a simplified interface to the modules in order to implement service autoscaling.

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
| <a name="module_autoscale_service"></a> [autoscale\_service](#module\_autoscale\_service) | ./modules/service-autoscaling | n/a |
| <a name="module_compute_queue_backlog_lambda"></a> [compute\_queue\_backlog\_lambda](#module\_compute\_queue\_backlog\_lambda) | ./modules/lambda-function | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.compute_queue_backlog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.compute_queue_backlog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_lambda_permission.compute_queue_backlog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_sqs_queue_policy.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cloudwatch_event_rule_tags"></a> [cloudwatch\_event\_rule\_tags](#input\_cloudwatch\_event\_rule\_tags) | Map of AWS tags to add to the CloudWatch Event Rule that invokes the queue backlog lambda. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. | `any` | `{}` | no |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | ECS cluster name. Uses default cluster if not supplied. | `string` | n/a | yes |
| <a name="input_depends_on_service"></a> [depends\_on\_service](#input\_depends\_on\_service) | aws\_ecs\_service object that you can pass to the module to ensure resources are recreated properly on service recreate. | `any` | `null` | no |
| <a name="input_lambda_invocation_interval"></a> [lambda\_invocation\_interval](#input\_lambda\_invocation\_interval) | Rate or cron expression to determine the interval for QueueBacklog metric refresh. | `string` | `"rate(1 minute)"` | no |
| <a name="input_lambda_log_level"></a> [lambda\_log\_level](#input\_lambda\_log\_level) | Log level to use for Lambda logs. Accepts the standard Python log levels. | `string` | `"INFO"` | no |
| <a name="input_lambda_name"></a> [lambda\_name](#input\_lambda\_name) | The lambda function name. | `string` | `"compute-queue-backlog"` | no |
| <a name="input_lambda_tags"></a> [lambda\_tags](#input\_lambda\_tags) | Map of AWS tags to add to the Lambda. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well. | `any` | `{}` | no |
| <a name="input_metric_name"></a> [metric\_name](#input\_metric\_name) | The name of the metric the lambda uses to derive the queue backlog value. | `string` | `"ApproximateNumberOfMessages"` | no |
| <a name="input_queue_arn"></a> [queue\_arn](#input\_queue\_arn) | ARN of the queue | `string` | n/a | yes |
| <a name="input_queue_backlog_target_value"></a> [queue\_backlog\_target\_value](#input\_queue\_backlog\_target\_value) | Queue backlog (in seconds) to maintain for the service when under maximum load. Queue backlog is defined as (metric*secs\_per\_msg/num\_tasks). Defaults to 600 seconds (10 minutes). | `number` | `0` | no |
| <a name="input_queue_name"></a> [queue\_name](#input\_queue\_name) | Name of the queue to compute QueueBacklog metric for. For the 'AWS/SQS' metric provider, the name must be the name of the SQS queue. It can be any value you wish for other metric providers. | `string` | n/a | yes |
| <a name="input_queue_owner_aws_account_id"></a> [queue\_owner\_aws\_account\_id](#input\_queue\_owner\_aws\_account\_id) | AWS account id that provides the queue. If not provided, will use the caller's account id. Only valid for 'AWS/SQS' metric provider. | `string` | `""` | no |
| <a name="input_queue_requires_consumer_alarm_evaluation_periods"></a> [queue\_requires\_consumer\_alarm\_evaluation\_periods](#input\_queue\_requires\_consumer\_alarm\_evaluation\_periods) | Number of periods to aggregate QueueRequiresConsumer metric over when comparing against the alarm threshold. | `number` | `1` | no |
| <a name="input_queue_requires_consumer_alarm_period"></a> [queue\_requires\_consumer\_alarm\_period](#input\_queue\_requires\_consumer\_alarm\_period) | Number of seconds to aggregate QueueRequiresConsumer metric before testing against the alarm threshold. | `number` | `60` | no |
| <a name="input_queue_requires_consumer_alarm_tags"></a> [queue\_requires\_consumer\_alarm\_tags](#input\_queue\_requires\_consumer\_alarm\_tags) | Map of AWS tags to add to the alarm. Note that the 'Name' tag is always added, and is the same as the value of the resource's 'name' attribute by default. The 'Description' tag is added as well. | `any` | `{}` | no |
| <a name="input_queue_url"></a> [queue\_url](#input\_queue\_url) | Name of the queue URL | `string` | n/a | yes |
| <a name="input_service_est_secs_per_msg"></a> [service\_est\_secs\_per\_msg](#input\_service\_est\_secs\_per\_msg) | Non-negative integer that represents the estimated number of seconds it takes the service to consume a single message from its queue. | `number` | n/a | yes |
| <a name="input_service_max_capacity"></a> [service\_max\_capacity](#input\_service\_max\_capacity) | Maximum number of tasks that the autoscaling policy can set for the service. | `number` | `10` | no |
| <a name="input_service_min_capacity"></a> [service\_min\_capacity](#input\_service\_min\_capacity) | Minimum number of tasks that the autoscaling policy can set for the service. | `number` | `1` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | ECS service name | `string` | n/a | yes |
| <a name="input_service_rampup_capacity"></a> [service\_rampup\_capacity](#input\_service\_rampup\_capacity) | Number of tasks to start as the immediate response to a QueueRequiresConsumer non-zero value. | `number` | `1` | no |
| <a name="input_service_scalein_cooldown"></a> [service\_scalein\_cooldown](#input\_service\_scalein\_cooldown) | Number of seconds to wait after a scaling operation before a scale-in operation can take place. | `number` | `60` | no |
| <a name="input_service_scaleout_cooldown"></a> [service\_scaleout\_cooldown](#input\_service\_scaleout\_cooldown) | Number of seconds to wait after a scaling operation before a scale-out operation can take place. | `number` | `30` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aws_cloudwatch_event_rule_arn"></a> [aws\_cloudwatch\_event\_rule\_arn](#output\_aws\_cloudwatch\_event\_rule\_arn) | ARN for the CloudWatch Event Rule that invokes the compute queue backlog lambda at a user-defined interval. |
<!-- END_TF_DOCS -->
