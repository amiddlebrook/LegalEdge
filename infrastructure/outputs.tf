output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.database.endpoint
}

output "database_port" {
  description = "RDS database port"
  value       = aws_db_instance.database.port
}

output "database_name" {
  description = "RDS database name"
  value       = aws_db_instance.database.db_name
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_cluster.redis.port
}

output "application_url" {
  description = "Application load balancer URL"
  value       = "https://${aws_lb.app.dns_name}"
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain"
  value       = aws_cloudfront_distribution.app.domain_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}

output "s3_app_assets_bucket" {
  description = "S3 bucket for application assets"
  value       = aws_s3_bucket.app_assets.bucket
}

output "s3_data_storage_bucket" {
  description = "S3 bucket for data storage"
  value       = aws_s3_bucket.data_storage.bucket
}

output "secrets_manager_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.db_password.arn
}

# Environment-specific outputs
output "connection_strings" {
  description = "Database and Redis connection strings"
  value = {
    database_url = "postgresql+asyncpg://${aws_db_instance.database.username}:[PASSWORD]@${aws_db_instance.database.endpoint}/${aws_db_instance.database.db_name}"
    redis_url    = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.port}/0"
  }
  sensitive = true
}

output "monitoring_urls" {
  description = "URLs for monitoring and access"
  value = {
    application    = "https://${aws_lb.app.dns_name}"
    cloudfront     = "https://${aws_cloudfront_distribution.app.domain_name}"
    load_balancer  = "http://${aws_lb.app.dns_name}"
  }
}
