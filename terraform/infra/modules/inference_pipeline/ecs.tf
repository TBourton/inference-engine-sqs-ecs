# https://github.com/terraform-aws-modules/terraform-aws-ecs
#
data "aws_vpc" "existing_vpc" {
  id = var.vpc_id
}


data "aws_ecr_repository" "ecr" {
  name = var.ecr
}

data "aws_ecr_image" "ecr_image" {
  repository_name = data.aws_ecr_repository.ecr.name
  most_recent     = var.container_tag == null ? true : null
  image_tag       = var.container_tag
}


resource "aws_security_group" "ecs_service_sg" {
  name        = "${var.name}-ecs-service-security-group"
  description = "Security group for ECS service"
  vpc_id      = data.aws_vpc.existing_vpc.id
}

resource "aws_security_group_rule" "ingress_vpc_endpoint" {
  description       = "Security group rule for ECS - ingress from VPC"
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  security_group_id = aws_security_group.ecs_service_sg.id
  self              = true
}

resource "aws_security_group_rule" "egress_vpc_endpoint" { # tfsec:ignore:aws-ec2-no-public-egress-sgr
  description       = "Security group rule for ECS - egress all"
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"] # Egress to internet for ECR
  security_group_id = aws_security_group.ecs_service_sg.id
  # self = true
}

data "aws_vpc_endpoint" "vpc_endpoints" {
  for_each = var.vpc_endpoint_ids_to_associate_to_ecs_sg
  vpc_id   = data.aws_vpc.existing_vpc.id
  id       = each.key
}

resource "aws_vpc_endpoint_security_group_association" "sg_associate" {
  for_each          = data.aws_vpc_endpoint.vpc_endpoints
  vpc_endpoint_id   = each.value.id
  security_group_id = aws_security_group.ecs_service_sg.id
}


module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = ">= 5.0.1"

  cluster_name                          = var.name
  default_capacity_provider_use_fargate = true
  tags                                  = local.tags
}

locals {
  image_url = "${data.aws_ecr_repository.ecr.repository_url}@${data.aws_ecr_image.ecr_image.id}"
}

module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = ">= 5.0.1"

  assign_public_ip = true
  # autoscaling_max_capacity = var.autoscaling_max_capacity
  # autoscaling_min_capacity = var.autoscaling_min_capacity
  cluster_arn = module.ecs_cluster.arn
  container_definitions = {
    consumer_task = {
      enable_cloudwatch_logging = true
      environment = concat([
        {
          name  = "SQS_QUEUE_NAME"
          value = module.sqs.queue_name
        },
        {
          name  = "DDB_TABLE_NAME"
          value = module.dynamodb_table.dynamodb_table_id
        },
        {
          name  = "HEARTBEAT_VISIBILITY_TIMEOUT"
          value = var.heartbeat_visibility_timeout_seconds
        },
        {
          name  = "HEARTBEAT_INTERVAL"
          value = var.heartbeat_interval
        },
        {
          name  = "ENABLE_ESC_SCALEIN_PROTECTION"
          value = var.enable_ecs_scalein_protection
        },
        ],
        var.container_environment
      )
      essential = true
      port_mappings = [
        {
          name          = "consumer"
          containerPort = 80
          protocol      = "tcp"
        }
      ]
      health_check = {
        command = ["CMD-SHELL", "curl -f http://localhost:80/health || exit 1"]
        # command     = ["CMD-SHELL", "curl -f http://localhost:80/health >> /proc/1/fd/1 2>&1"]
        retries     = 3
        interval    = 30
        startPeriod = 5
        timeout     = 5
      }
      image = local.image_url
      name  = "${var.name}-consumer-task"
      tags  = local.tags
    }
  }
  cpu                   = var.cpu
  create_security_group = false
  deployment_circuit_breaker = {
    enable   = true
    rollback = var.rollback
  }
  desired_count         = var.desired_count
  enable_autoscaling    = false # Do custom SQS autoscaling instead
  family                = var.name
  force_delete          = true
  force_new_deployment  = true
  memory                = var.memory
  name                  = "${var.name}-consumer-service"
  security_group_ids    = [aws_security_group.ecs_service_sg.id]
  skip_destroy          = false
  subnet_ids            = var.subnet_ids
  tags                  = local.tags
  task_tags             = local.tags
  wait_for_steady_state = var.wait_for_steady_state
  wait_until_stable     = var.wait_for_steady_state
}
