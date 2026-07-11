resource "aws_sqs_queue" "notifications" {
  name                       = "${local.name_prefix}-notifications"
  message_retention_seconds  = 1209600 # 14 days
  visibility_timeout_seconds = 30

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notifications_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "notifications_dlq" {
  name = "${local.name_prefix}-notifications-dlq"
}

resource "aws_sqs_queue" "sms_outbound" {
  name                       = "${local.name_prefix}-sms-outbound"
  message_retention_seconds  = 604800 # 7 days
  visibility_timeout_seconds = 60
}

resource "aws_sqs_queue" "recovery_tasks" {
  name                       = "${local.name_prefix}-recovery-tasks"
  message_retention_seconds  = 259200 # 3 days
  visibility_timeout_seconds = 300
}

resource "aws_sns_topic" "user_notifications" {
  name = "${local.name_prefix}-user-notifications"
}

# ponytail: Lambda handlers scaffolded separately; wire triggers when handlers exist
resource "aws_cloudwatch_event_rule" "weather_refresh" {
  name                = "${local.name_prefix}-weather-refresh"
  schedule_expression = "rate(15 minutes)"
}

resource "aws_cloudwatch_event_rule" "daily_reminders" {
  name                = "${local.name_prefix}-daily-reminders"
  schedule_expression = "cron(0 9 * * ? *)"
}

resource "aws_cloudwatch_event_rule" "emergency_alert" {
  name = "${local.name_prefix}-emergency-alert"

  event_pattern = jsonencode({
    source      = ["vayuassist.chat-service"]
    detail-type = ["Emergency"]
  })
}

resource "aws_cloudwatch_event_target" "emergency_sns" {
  rule      = aws_cloudwatch_event_rule.emergency_alert.name
  target_id = "sns-alerts"
  arn       = aws_sns_topic.alerts.arn
}
