variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be dev or prod"
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

# --- Database ---

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "db_backup_retention_days" {
  type    = number
  default = 7
}

variable "db_multi_az" {
  type    = bool
  default = false
}

# --- Cache ---

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "redis_num_cache_nodes" {
  type    = number
  default = 1
}

# --- Compute ---

variable "ecs_cpu" {
  type    = number
  default = 256
}

variable "ecs_memory" {
  type    = number
  default = 512
}

variable "ecs_desired_count" {
  type    = number
  default = 1
}

variable "ecs_min_capacity" {
  type    = number
  default = 1
}

variable "ecs_max_capacity" {
  type    = number
  default = 4
}

variable "frontend_domain" {
  description = "CloudFront CNAME (optional)"
  type        = string
  default     = ""
}
