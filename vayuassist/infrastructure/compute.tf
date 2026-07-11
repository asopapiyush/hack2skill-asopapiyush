resource "aws_ecs_cluster" "main" {
  name = local.name_prefix

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecr_repository" "chat_service" {
  name                 = "vayuassist/chat-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment == "dev"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "planning_service" {
  name                 = "vayuassist/planning-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment == "dev"
}

resource "aws_ecr_repository" "advisory_service" {
  name                 = "vayuassist/advisory-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment == "dev"
}

resource "aws_ecr_repository" "frontend" {
  name                 = "vayuassist/frontend"
  image_tag_mutability = "MUTABLE"
  force_delete         = var.environment == "dev"
}

resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "chat" {
  name        = "${local.name_prefix}-chat"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "planning" {
  name        = "${local.name_prefix}-planning"
  port        = 8001
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_target_group" "advisory" {
  name        = "${local.name_prefix}-advisory"
  port        = 8002
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_target_group" "frontend" {
  name        = "${local.name_prefix}-frontend"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path = "/"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

resource "aws_lb_listener_rule" "chat" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.chat.arn
  }

  condition {
    path_pattern {
      values = ["/api/chat/*", "/auth/*", "/health"]
    }
  }
}

resource "aws_lb_listener_rule" "planning" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.planning.arn
  }

  condition {
    path_pattern {
      values = ["/api/plans/*"]
    }
  }
}

resource "aws_lb_listener_rule" "advisory" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 30

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.advisory.arn
  }

  condition {
    path_pattern {
      values = ["/api/advisories/*"]
    }
  }
}

locals {
  services = {
    chat-service = {
      port          = 8000
      target_group  = aws_lb_target_group.chat.arn
      ecr_repo      = aws_ecr_repository.chat_service.repository_url
      log_group     = aws_cloudwatch_log_group.ecs["chat-service"].name
    }
    planning-service = {
      port          = 8001
      target_group  = aws_lb_target_group.planning.arn
      ecr_repo      = aws_ecr_repository.planning_service.repository_url
      log_group     = aws_cloudwatch_log_group.ecs["planning-service"].name
    }
    advisory-service = {
      port          = 8002
      target_group  = aws_lb_target_group.advisory.arn
      ecr_repo      = aws_ecr_repository.advisory_service.repository_url
      log_group     = aws_cloudwatch_log_group.ecs["advisory-service"].name
    }
    frontend-web = {
      port          = 80
      target_group  = aws_lb_target_group.frontend.arn
      ecr_repo      = aws_ecr_repository.frontend.repository_url
      log_group     = aws_cloudwatch_log_group.ecs["frontend-web"].name
    }
  }
}

resource "aws_ecs_task_definition" "service" {
  for_each = local.services

  family                   = "${local.name_prefix}-${each.key}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = each.key
    image = "${each.value.ecr_repo}:latest"
    portMappings = [{
      containerPort = each.value.port
      protocol      = "tcp"
    }]
    environment = [
      { name = "ENV", value = var.environment },
      { name = "AWS_REGION", value = var.aws_region },
    ]
    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.database.arn}:database_url::"
      },
      {
        name      = "REDIS_URL"
        valueFrom = "${aws_secretsmanager_secret.redis.arn}:url::"
      },
      {
        name      = "OPENAI_API_KEY"
        valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:openai_api_key::"
      },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = each.value.log_group
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = each.key
      }
    }
    essential = true
  }])
}

resource "aws_ecs_service" "service" {
  for_each = local.services

  name            = each.key
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.service[each.key].arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = var.environment == "dev"
  }

  load_balancer {
    target_group_arn = each.value.target_group
    container_name   = each.key
    container_port   = each.value.port
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

resource "aws_appautoscaling_target" "ecs" {
  for_each = { for k, v in local.services : k => v if k != "frontend-web" }

  max_capacity       = var.ecs_max_capacity
  min_capacity       = var.ecs_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${each.key}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu" {
  for_each = aws_appautoscaling_target.ecs

  name               = "${each.key}-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  service_namespace  = each.value.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value                 = 70.0
    scale_in_cooldown            = 300
    scale_out_cooldown           = 60
  }
}

# --- S3 + CloudFront for static frontend ---

resource "aws_s3_bucket" "frontend" {
  bucket = "${local.name_prefix}-frontend"
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${local.name_prefix}-frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "s3-frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = "s3-frontend"
    viewer_protocol_policy   = "redirect-to-https"
    compress                 = true
    min_ttl                  = 0
    default_ttl              = 3600
    max_ttl                  = 86400
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
