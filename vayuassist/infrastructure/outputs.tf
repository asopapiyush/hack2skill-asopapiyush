output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "rds_cluster_endpoint" {
  value = aws_rds_cluster.main.endpoint
}

output "rds_cluster_reader_endpoint" {
  value = aws_rds_cluster.main.reader_endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "ecr_repository_urls" {
  value = {
    chat_service     = aws_ecr_repository.chat_service.repository_url
    planning_service = aws_ecr_repository.planning_service.repository_url
    advisory_service = aws_ecr_repository.advisory_service.repository_url
    frontend         = aws_ecr_repository.frontend.repository_url
  }
}

output "api_gateway_url" {
  value = aws_apigatewayv2_api.main.api_endpoint
}

output "cloudfront_domain" {
  value = try(aws_cloudfront_distribution.frontend.domain_name, null)
}

output "sqs_queue_urls" {
  value = {
    notifications  = aws_sqs_queue.notifications.url
    sms_outbound   = aws_sqs_queue.sms_outbound.url
    recovery_tasks = aws_sqs_queue.recovery_tasks.url
  }
}

output "sns_topic_arns" {
  value = {
    alerts              = aws_sns_topic.alerts.arn
    user_notifications  = aws_sns_topic.user_notifications.arn
  }
}
