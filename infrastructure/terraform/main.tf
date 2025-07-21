# Infrastructure as Code - Main Terraform Configuration
# Multi-cloud deployment support for AWS, Azure, and GCP

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket         = "intelligence-os-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "cloud_provider" {
  description = "Primary cloud provider (aws, azure, gcp)"
  type        = string
  default     = "aws"
}

variable "region" {
  description = "Primary region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "multi_cloud_enabled" {
  description = "Enable multi-cloud deployment"
  type        = bool
  default     = false
}

variable "auto_scaling_enabled" {
  description = "Enable auto-scaling for services"
  type        = bool
  default     = true
}

variable "backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# Local values
locals {
  common_tags = {
    Project     = "Intelligence-OS-Platform"
    Environment = var.environment
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }

  cluster_name = "intelligence-os-${var.environment}"
}

# AWS Provider Configuration
provider "aws" {
  region = var.region
  
  default_tags {
    tags = local.common_tags
  }
}

# Azure Provider Configuration
provider "azurerm" {
  count = var.multi_cloud_enabled ? 1 : 0
  features {}
}

# GCP Provider Configuration
provider "google" {
  count   = var.multi_cloud_enabled ? 1 : 0
  project = "intelligence-os-platform"
  region  = var.region
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# AWS Infrastructure
module "aws_infrastructure" {
  source = "./modules/aws"
  
  environment          = var.environment
  region              = var.region
  availability_zones  = data.aws_availability_zones.available.names
  cluster_name        = local.cluster_name
  auto_scaling_enabled = var.auto_scaling_enabled
  backup_enabled      = var.backup_enabled
  
  tags = local.common_tags
}

# Azure Infrastructure (optional)
module "azure_infrastructure" {
  count  = var.multi_cloud_enabled ? 1 : 0
  source = "./modules/azure"
  
  environment    = var.environment
  location       = "West US 2"
  cluster_name   = local.cluster_name
  
  tags = local.common_tags
}

# GCP Infrastructure (optional)
module "gcp_infrastructure" {
  count  = var.multi_cloud_enabled ? 1 : 0
  source = "./modules/gcp"
  
  environment    = var.environment
  region         = var.region
  cluster_name   = local.cluster_name
  
  labels = local.common_tags
}

# Kubernetes Configuration
provider "kubernetes" {
  host                   = module.aws_infrastructure.cluster_endpoint
  cluster_ca_certificate = base64decode(module.aws_infrastructure.cluster_ca_certificate)
  token                  = module.aws_infrastructure.cluster_token
}

provider "helm" {
  kubernetes {
    host                   = module.aws_infrastructure.cluster_endpoint
    cluster_ca_certificate = base64decode(module.aws_infrastructure.cluster_ca_certificate)
    token                  = module.aws_infrastructure.cluster_token
  }
}

# Kubernetes Applications
module "kubernetes_applications" {
  source = "./modules/kubernetes"
  
  environment     = var.environment
  cluster_name    = local.cluster_name
  cluster_endpoint = module.aws_infrastructure.cluster_endpoint
  
  # Application configuration
  frontend_image    = "ghcr.io/intelligence-os/frontend:latest"
  backend_image     = "ghcr.io/intelligence-os/backend:latest"
  voice_image       = "ghcr.io/intelligence-os/voice-processor:latest"
  
  # Scaling configuration
  frontend_replicas = var.environment == "production" ? 3 : 2
  backend_replicas  = var.environment == "production" ? 3 : 2
  voice_replicas    = var.environment == "production" ? 3 : 2
  
  # Resource limits
  frontend_cpu_limit    = "1000m"
  frontend_memory_limit = "1Gi"
  backend_cpu_limit     = "2000m"
  backend_memory_limit  = "2Gi"
  voice_cpu_limit       = "4000m"
  voice_memory_limit    = "4Gi"
  
  depends_on = [module.aws_infrastructure]
}

# Monitoring and Observability
module "monitoring" {
  source = "./modules/monitoring"
  
  environment    = var.environment
  cluster_name   = local.cluster_name
  
  # Prometheus configuration
  prometheus_enabled = true
  grafana_enabled    = true
  alertmanager_enabled = true
  
  # Logging configuration
  elasticsearch_enabled = true
  kibana_enabled       = true
  fluentd_enabled      = true
  
  depends_on = [module.kubernetes_applications]
}

# Security and Compliance
module "security" {
  source = "./modules/security"
  
  environment  = var.environment
  cluster_name = local.cluster_name
  
  # Security scanning
  falco_enabled = true
  opa_enabled   = true
  
  # Network policies
  network_policies_enabled = true
  
  # Secrets management
  external_secrets_enabled = true
  vault_enabled           = var.environment == "production"
  
  depends_on = [module.kubernetes_applications]
}

# Outputs
output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = module.aws_infrastructure.cluster_endpoint
  sensitive   = true
}

output "cluster_name" {
  description = "Kubernetes cluster name"
  value       = local.cluster_name
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = module.kubernetes_applications.load_balancer_dns
}

output "monitoring_urls" {
  description = "Monitoring service URLs"
  value       = module.monitoring.service_urls
  sensitive   = true
}

output "database_endpoints" {
  description = "Database connection endpoints"
  value       = module.aws_infrastructure.database_endpoints
  sensitive   = true
}