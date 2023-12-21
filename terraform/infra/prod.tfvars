# prod
rollback                                = true
service_autoscaling_max_capacity        = 10
service_autoscaling_min_capacity        = 1
desired_count                           = 1
dynamodb_deletion_protection_enabled    = true
dynamodb_point_in_time_recovery_enabled = true
sqs_vpc_endpoint_id                     = "vpce-09df8411dd89b0073"
