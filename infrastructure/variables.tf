variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "task_cpu" {
  description = "ECS task CPU units"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "ECS task memory"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "legaledge-app:latest"
}

variable "domain_name" {
  description = "Domain name for the application (e.g., api.legaledge.com)"
  type        = string
  default     = ""
}

variable "create_route53_record" {
  description = "Whether to create Route 53 records for the domain"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone ID (required if create_route53_record is true)"
  type        = string
  default     = ""
}

variable "alarm_actions" {
  description = "SNS topics or email addresses for CloudWatch alarms"
  type        = list(string)
  default     = []
}

variable "monthly_budget" {
  description = "Monthly AWS budget in USD"
  type        = number
  default     = 500
}

variable "budget_alert_emails" {
  description = "Email addresses for budget alerts"
  type        = list(string)
  default     = []
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

variable "data_retention_days" {
  description = "Number of days to retain data before archiving"
  type        = number
  default     = 2555  # 7 years
}

variable "log_retention_days" {
  description = "Number of days to retain log files"
  type        = number
  default     = 365
}

variable "enable_backup_encryption" {
  description = "Enable encryption for backups"
  type        = bool
  default     = true
}

variable "cost_optimization_enabled" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "rds_cost_threshold" {
  description = "RDS cost threshold in USD per 6-hour period"
  type        = number
  default     = 100
}

variable "ecs_cost_threshold" {
  description = "ECS cost threshold in USD per 6-hour period"
  type        = number
  default     = 80
}

variable "s3_cost_threshold" {
  description = "S3 cost threshold in USD per 6-hour period"
  type        = number
  default     = 50
}

variable "legislative_data_retention_years" {
  description = "Years to retain legislative data"
  type        = number
  default     = 7
}

variable "trade_data_retention_years" {
  description = "Years to retain trade disclosure data"
  type        = number
  default     = 10
}

variable "audit_log_retention_years" {
  description = "Years to retain audit logs"
  type        = number
  default     = 7
}

# Environment-specific configurations
locals {
  # Database configuration
  db_config = {
    development = {
      instance_class = "db.t3.micro"
      allocated_storage = 20
    }
    staging = {
      instance_class = "db.t3.small"
      allocated_storage = 50
    }
    production = {
      instance_class = "db.t3.medium"
      allocated_storage = 100
    }
  }

  # Redis configuration
  redis_config = {
    development = {
      node_type = "cache.t3.micro"
      num_cache_nodes = 1
    }
    staging = {
      node_type = "cache.t3.small"
      num_cache_nodes = 1
    }
    production = {
      node_type = "cache.t3.medium"
      num_cache_nodes = 2
    }
  }

  # ECS configuration
  ecs_config = {
    development = {
      desired_count = 1
      task_cpu = 256
      task_memory = 512
    }
    staging = {
      desired_count = 2
      task_cpu = 512
      task_memory = 1024
    }
  # Cost and backup configuration
  cost_backup_config = {
    development = {
      monthly_budget = 500
      backup_retention_days = 7
      data_retention_days = 365
      enable_backup_encryption = true
    }
    staging = {
      monthly_budget = 1000
      backup_retention_days = 30
      data_retention_days = 1825  # 5 years
      enable_backup_encryption = true
    }
    production = {
      monthly_budget = 5000
      backup_retention_days = 90
      data_retention_days = 2555  # 7 years
      enable_backup_encryption = true
    }
  }
