# Kubernetes Applications Module
# Deploys Intelligence OS Platform applications to Kubernetes

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_name" {
  description = "Kubernetes cluster name"
  type        = string
}

variable "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  type        = string
}

variable "frontend_image" {
  description = "Frontend container image"
  type        = string
}

variable "backend_image" {
  description = "Backend container image"
  type        = string
}

variable "voice_image" {
  description = "Voice processor container image"
  type        = string
}

variable "frontend_replicas" {
  description = "Number of frontend replicas"
  type        = number
  default     = 2
}

variable "backend_replicas" {
  description = "Number of backend replicas"
  type        = number
  default     = 2
}

variable "voice_replicas" {
  description = "Number of voice processor replicas"
  type        = number
  default     = 2
}

variable "frontend_cpu_limit" {
  description = "Frontend CPU limit"
  type        = string
  default     = "1000m"
}

variable "frontend_memory_limit" {
  description = "Frontend memory limit"
  type        = string
  default     = "1Gi"
}

variable "backend_cpu_limit" {
  description = "Backend CPU limit"
  type        = string
  default     = "2000m"
}

variable "backend_memory_limit" {
  description = "Backend memory limit"
  type        = string
  default     = "2Gi"
}

variable "voice_cpu_limit" {
  description = "Voice processor CPU limit"
  type        = string
  default     = "4000m"
}

variable "voice_memory_limit" {
  description = "Voice processor memory limit"
  type        = string
  default     = "4Gi"
}

# Namespace
resource "kubernetes_namespace" "main" {
  metadata {
    name = "intelligence-os-${var.environment}"
    
    labels = {
      environment = var.environment
      app         = "intelligence-os"
    }
  }
}

# ConfigMap for application configuration
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "intelligence-os-config"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  data = {
    NODE_ENV                = var.environment
    LOG_LEVEL              = var.environment == "production" ? "warn" : "info"
    FRONTEND_URL           = var.environment == "production" ? "https://intelligence-os.example.com" : "https://staging.intelligence-os.example.com"
    API_URL                = var.environment == "production" ? "https://api.intelligence-os.example.com" : "https://api.staging.intelligence-os.example.com"
    REDIS_HOST             = "redis-service"
    REDIS_PORT             = "6379"
    ENABLE_CACHING         = "true"
    RATE_LIMIT_REQUESTS    = "100"
    RATE_LIMIT_WINDOW_MS   = "60000"
    VOICE_PROCESSOR_URL    = "http://voice-processor-service:5000"
    AI_CONDUCTOR_URL       = "http://backend-service:8000/api/ai-conductor"
  }
}

# Secrets (these would be populated from external secret management)
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "intelligence-os-secrets"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  type = "Opaque"

  data = {
    # These are placeholders - actual secrets should come from AWS Secrets Manager
    DATABASE_URL    = base64encode("postgresql://user:password@db-service:5432/intelligenceos")
    JWT_SECRET      = base64encode("your-jwt-secret-key")
    OPENAI_API_KEY  = base64encode("your-openai-api-key")
    REDIS_PASSWORD  = base64encode("your-redis-password")
  }
}

# Frontend Deployment
resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app         = "frontend"
      environment = var.environment
    }
  }

  spec {
    replicas = var.frontend_replicas

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    strategy {
      type = "RollingUpdate"
      
      rolling_update {
        max_surge       = "1"
        max_unavailable = "0"
      }
    }

    template {
      metadata {
        labels = {
          app         = "frontend"
          environment = var.environment
        }
        
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "3000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name  = "frontend"
          image = var.frontend_image

          port {
            container_port = 3000
            name          = "http"
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = var.frontend_cpu_limit
              memory = var.frontend_memory_limit
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 3000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 3000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            success_threshold     = 1
            failure_threshold     = 3
          }

          startup_probe {
            http_get {
              path = "/health"
              port = 3000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 30
          }
        }

        restart_policy = "Always"
      }
    }
  }
}

# Backend Deployment
resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app         = "backend"
      environment = var.environment
    }
  }

  spec {
    replicas = var.backend_replicas

    selector {
      match_labels = {
        app = "backend"
      }
    }

    strategy {
      type = "RollingUpdate"
      
      rolling_update {
        max_surge       = "1"
        max_unavailable = "0"
      }
    }

    template {
      metadata {
        labels = {
          app         = "backend"
          environment = var.environment
        }
        
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name  = "backend"
          image = var.backend_image

          port {
            container_port = 8000
            name          = "http"
          }

          resources {
            requests = {
              cpu    = "200m"
              memory = "256Mi"
            }
            limits = {
              cpu    = var.backend_cpu_limit
              memory = var.backend_memory_limit
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.app_secrets.metadata[0].name
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            success_threshold     = 1
            failure_threshold     = 3
          }

          startup_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 30
          }
        }

        restart_policy = "Always"
      }
    }
  }
}

# Voice Processor Deployment
resource "kubernetes_deployment" "voice_processor" {
  metadata {
    name      = "voice-processor"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app         = "voice-processor"
      environment = var.environment
    }
  }

  spec {
    replicas = var.voice_replicas

    selector {
      match_labels = {
        app = "voice-processor"
      }
    }

    strategy {
      type = "RollingUpdate"
      
      rolling_update {
        max_surge       = "1"
        max_unavailable = "0"
      }
    }

    template {
      metadata {
        labels = {
          app         = "voice-processor"
          environment = var.environment
        }
        
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name  = "voice-processor"
          image = var.voice_image

          port {
            container_port = 5000
            name          = "http"
          }

          resources {
            requests = {
              cpu    = "300m"
              memory = "512Mi"
            }
            limits = {
              cpu    = var.voice_cpu_limit
              memory = var.voice_memory_limit
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.app_secrets.metadata[0].name
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            success_threshold     = 1
            failure_threshold     = 3
          }

          startup_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 30
          }
        }

        restart_policy = "Always"
      }
    }
  }
}

# Services
resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app = "frontend"
    }
  }

  spec {
    selector = {
      app = "frontend"
    }

    port {
      port        = 80
      target_port = 3000
      protocol    = "TCP"
      name        = "http"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app = "backend"
    }
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      port        = 80
      target_port = 8000
      protocol    = "TCP"
      name        = "http"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service" "voice_processor" {
  metadata {
    name      = "voice-processor-service"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    labels = {
      app = "voice-processor"
    }
  }

  spec {
    selector = {
      app = "voice-processor"
    }

    port {
      port        = 80
      target_port = 5000
      protocol    = "TCP"
      name        = "http"
    }

    type = "ClusterIP"
  }
}

# Horizontal Pod Autoscalers
resource "kubernetes_horizontal_pod_autoscaler_v2" "frontend" {
  metadata {
    name      = "frontend-hpa"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.frontend.metadata[0].name
    }

    min_replicas = var.frontend_replicas
    max_replicas = var.frontend_replicas * 3

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "backend" {
  metadata {
    name      = "backend-hpa"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.backend.metadata[0].name
    }

    min_replicas = var.backend_replicas
    max_replicas = var.backend_replicas * 3

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "voice_processor" {
  metadata {
    name      = "voice-processor-hpa"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.voice_processor.metadata[0].name
    }

    min_replicas = var.voice_replicas
    max_replicas = var.voice_replicas * 2

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

# Ingress
resource "kubernetes_ingress_v1" "main" {
  metadata {
    name      = "intelligence-os-ingress"
    namespace = kubernetes_namespace.main.metadata[0].name
    
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "true"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/rate-limit"         = "100"
      "nginx.ingress.kubernetes.io/rate-limit-window"  = "1m"
    }
  }

  spec {
    tls {
      hosts       = [var.environment == "production" ? "intelligence-os.example.com" : "staging.intelligence-os.example.com"]
      secret_name = "intelligence-os-tls"
    }

    rule {
      host = var.environment == "production" ? "intelligence-os.example.com" : "staging.intelligence-os.example.com"
      
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          
          backend {
            service {
              name = kubernetes_service.frontend.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }

    rule {
      host = var.environment == "production" ? "api.intelligence-os.example.com" : "api.staging.intelligence-os.example.com"
      
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          
          backend {
            service {
              name = kubernetes_service.backend.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

# Network Policies
resource "kubernetes_network_policy" "default_deny" {
  metadata {
    name      = "default-deny-all"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    pod_selector {}
    policy_types = ["Ingress", "Egress"]
  }
}

resource "kubernetes_network_policy" "allow_frontend" {
  metadata {
    name      = "allow-frontend"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "frontend"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            name = "ingress-nginx"
          }
        }
      }
      ports {
        port     = "3000"
        protocol = "TCP"
      }
    }

    egress {
      to {
        pod_selector {
          match_labels = {
            app = "backend"
          }
        }
      }
      ports {
        port     = "8000"
        protocol = "TCP"
      }
    }
  }
}

resource "kubernetes_network_policy" "allow_backend" {
  metadata {
    name      = "allow-backend"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "backend"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        pod_selector {
          match_labels = {
            app = "frontend"
          }
        }
      }
      from {
        namespace_selector {
          match_labels = {
            name = "ingress-nginx"
          }
        }
      }
      ports {
        port     = "8000"
        protocol = "TCP"
      }
    }

    egress {
      to {
        pod_selector {
          match_labels = {
            app = "voice-processor"
          }
        }
      }
      ports {
        port     = "5000"
        protocol = "TCP"
      }
    }

    egress {
      # Allow external API calls
      ports {
        port     = "443"
        protocol = "TCP"
      }
    }
  }
}

# Pod Disruption Budgets
resource "kubernetes_pod_disruption_budget_v1" "frontend" {
  metadata {
    name      = "frontend-pdb"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    min_available = "50%"
    
    selector {
      match_labels = {
        app = "frontend"
      }
    }
  }
}

resource "kubernetes_pod_disruption_budget_v1" "backend" {
  metadata {
    name      = "backend-pdb"
    namespace = kubernetes_namespace.main.metadata[0].name
  }

  spec {
    min_available = "50%"
    
    selector {
      match_labels = {
        app = "backend"
      }
    }
  }
}

# Outputs
output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.main.metadata[0].name
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = kubernetes_ingress_v1.main.status[0].load_balancer[0].ingress[0].hostname
}

output "service_endpoints" {
  description = "Service endpoints"
  value = {
    frontend       = "${kubernetes_service.frontend.metadata[0].name}.${kubernetes_namespace.main.metadata[0].name}.svc.cluster.local"
    backend        = "${kubernetes_service.backend.metadata[0].name}.${kubernetes_namespace.main.metadata[0].name}.svc.cluster.local"
    voice_processor = "${kubernetes_service.voice_processor.metadata[0].name}.${kubernetes_namespace.main.metadata[0].name}.svc.cluster.local"
  }
}