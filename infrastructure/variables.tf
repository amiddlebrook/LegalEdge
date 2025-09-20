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

variable "ssl_certificate_arn" {
  description = "SSL certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "alarm_actions" {
  description = "SNS topics or email addresses for CloudWatch alarms"
  type        = list(string)
  default     = []
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
    production = {
      desired_count = 3
      task_cpu = 1024
      task_memory = 2048
    }
  }
}
