# Monitoring and Observability Module
# Prometheus, Grafana, Jaeger, ELK Stack

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_name" {
  description = "Kubernetes cluster name"
  type        = string
}

variable "prometheus_enabled" {
  description = "Enable Prometheus monitoring"
  type        = bool
  default     = true
}

variable "grafana_enabled" {
  description = "Enable Grafana dashboards"
  type        = bool
  default     = true
}

variable "alertmanager_enabled" {
  description = "Enable Alertmanager"
  type        = bool
  default     = true
}

variable "elasticsearch_enabled" {
  description = "Enable Elasticsearch for logging"
  type        = bool
  default     = true
}

variable "kibana_enabled" {
  description = "Enable Kibana for log visualization"
  type        = bool
  default     = true
}

variable "fluentd_enabled" {
  description = "Enable Fluentd for log collection"
  type        = bool
  default     = true
}

variable "jaeger_enabled" {
  description = "Enable Jaeger for distributed tracing"
  type        = bool
  default     = true
}

# Monitoring namespace
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
    
    labels = {
      name = "monitoring"
    }
  }
}

# Prometheus Operator
resource "helm_release" "prometheus_operator" {
  count = var.prometheus_enabled ? 1 : 0
  
  name       = "prometheus-operator"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "55.5.0"

  values = [
    yamlencode({
      prometheus = {
        prometheusSpec = {
          retention = var.environment == "production" ? "30d" : "7d"
          storageSpec = {
            volumeClaimTemplate = {
              spec = {
                storageClassName = "gp3"
                accessModes      = ["ReadWriteOnce"]
                resources = {
                  requests = {
                    storage = var.environment == "production" ? "100Gi" : "20Gi"
                  }
                }
              }
            }
          }
          resources = {
            requests = {
              cpu    = "500m"
              memory = "2Gi"
            }
            limits = {
              cpu    = "2000m"
              memory = "4Gi"
            }
          }
          serviceMonitorSelectorNilUsesHelmValues = false
          podMonitorSelectorNilUsesHelmValues     = false
          ruleSelectorNilUsesHelmValues           = false
        }
      }
      
      grafana = {
        enabled = var.grafana_enabled
        adminPassword = "admin123" # Change in production
        persistence = {
          enabled = true
          size    = "10Gi"
        }
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
        dashboardProviders = {
          "dashboardproviders.yaml" = {
            apiVersion = 1
            providers = [
              {
                name    = "default"
                orgId   = 1
                folder  = ""
                type    = "file"
                disableDeletion = false
                editable = true
                options = {
                  path = "/var/lib/grafana/dashboards/default"
                }
              }
            ]
          }
        }
        dashboards = {
          default = {
            "intelligence-os-overview" = {
              gnetId = 1860
              revision = 27
              datasource = "Prometheus"
            }
            "kubernetes-cluster-monitoring" = {
              gnetId = 7249
              revision = 1
              datasource = "Prometheus"
            }
          }
        }
      }
      
      alertmanager = {
        enabled = var.alertmanager_enabled
        alertmanagerSpec = {
          storage = {
            volumeClaimTemplate = {
              spec = {
                storageClassName = "gp3"
                accessModes      = ["ReadWriteOnce"]
                resources = {
                  requests = {
                    storage = "10Gi"
                  }
                }
              }
            }
          }
          resources = {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }
        config = {
          global = {
            smtp_smarthost = "localhost:587"
            smtp_from      = "alertmanager@intelligence-os.example.com"
          }
          route = {
            group_by        = ["alertname"]
            group_wait      = "10s"
            group_interval  = "10s"
            repeat_interval = "1h"
            receiver        = "web.hook"
          }
          receivers = [
            {
              name = "web.hook"
              webhook_configs = [
                {
                  url = "http://localhost:5001/"
                }
              ]
            }
          ]
        }
      }
      
      nodeExporter = {
        enabled = true
      }
      
      kubeStateMetrics = {
        enabled = true
      }
    })
  ]

  depends_on = [kubernetes_namespace.monitoring]
}

# Custom ServiceMonitor for Intelligence OS applications
resource "kubernetes_manifest" "intelligence_os_service_monitor" {
  count = var.prometheus_enabled ? 1 : 0
  
  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "intelligence-os-monitor"
      namespace = kubernetes_namespace.monitoring.metadata[0].name
      labels = {
        app = "intelligence-os"
      }
    }
    spec = {
      selector = {
        matchLabels = {
          app = "intelligence-os"
        }
      }
      namespaceSelector = {
        matchNames = ["intelligence-os-${var.environment}"]
      }
      endpoints = [
        {
          port     = "http"
          path     = "/metrics"
          interval = "30s"
        }
      ]
    }
  }

  depends_on = [helm_release.prometheus_operator]
}

# Elasticsearch for logging
resource "helm_release" "elasticsearch" {
  count = var.elasticsearch_enabled ? 1 : 0
  
  name       = "elasticsearch"
  repository = "https://helm.elastic.co"
  chart      = "elasticsearch"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "8.5.1"

  values = [
    yamlencode({
      replicas = var.environment == "production" ? 3 : 1
      
      esConfig = {
        "elasticsearch.yml" = <<-EOF
          cluster.name: "intelligence-os-logs"
          network.host: 0.0.0.0
          discovery.type: single-node
          xpack.security.enabled: false
          xpack.monitoring.collection.enabled: true
        EOF
      }
      
      resources = {
        requests = {
          cpu    = "1000m"
          memory = "2Gi"
        }
        limits = {
          cpu    = "2000m"
          memory = "4Gi"
        }
      }
      
      volumeClaimTemplate = {
        accessModes = ["ReadWriteOnce"]
        storageClassName = "gp3"
        resources = {
          requests = {
            storage = var.environment == "production" ? "100Gi" : "30Gi"
          }
        }
      }
      
      persistence = {
        enabled = true
      }
    })
  ]

  depends_on = [kubernetes_namespace.monitoring]
}

# Kibana for log visualization
resource "helm_release" "kibana" {
  count = var.kibana_enabled ? 1 : 0
  
  name       = "kibana"
  repository = "https://helm.elastic.co"
  chart      = "kibana"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "8.5.1"

  values = [
    yamlencode({
      elasticsearchHosts = "http://elasticsearch-master:9200"
      
      kibanaConfig = {
        "kibana.yml" = <<-EOF
          server.host: 0.0.0.0
          elasticsearch.hosts: ["http://elasticsearch-master:9200"]
          monitoring.ui.container.elasticsearch.enabled: true
        EOF
      }
      
      resources = {
        requests = {
          cpu    = "500m"
          memory = "1Gi"
        }
        limits = {
          cpu    = "1000m"
          memory = "2Gi"
        }
      }
      
      service = {
        type = "ClusterIP"
        port = 5601
      }
    })
  ]

  depends_on = [helm_release.elasticsearch]
}

# Fluentd for log collection
resource "helm_release" "fluentd" {
  count = var.fluentd_enabled ? 1 : 0
  
  name       = "fluentd"
  repository = "https://fluent.github.io/helm-charts"
  chart      = "fluentd"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "0.4.0"

  values = [
    yamlencode({
      image = {
        repository = "fluent/fluentd-kubernetes-daemonset"
        tag        = "v1.16-debian-elasticsearch7-1"
      }
      
      env = [
        {
          name  = "FLUENT_ELASTICSEARCH_HOST"
          value = "elasticsearch-master"
        },
        {
          name  = "FLUENT_ELASTICSEARCH_PORT"
          value = "9200"
        },
        {
          name  = "FLUENT_ELASTICSEARCH_SCHEME"
          value = "http"
        }
      ]
      
      resources = {
        requests = {
          cpu    = "100m"
          memory = "200Mi"
        }
        limits = {
          cpu    = "500m"
          memory = "500Mi"
        }
      }
      
      tolerations = [
        {
          key    = "node-role.kubernetes.io/master"
          effect = "NoSchedule"
        }
      ]
      
      configMaps = {
        "fluentd.conf" = <<-EOF
          <source>
            @type tail
            @id in_tail_container_logs
            path /var/log/containers/*.log
            pos_file /var/log/fluentd-containers.log.pos
            tag kubernetes.*
            read_from_head true
            <parse>
              @type json
              time_format %Y-%m-%dT%H:%M:%S.%NZ
            </parse>
          </source>
          
          <filter kubernetes.**>
            @type kubernetes_metadata
            @id filter_kube_metadata
          </filter>
          
          <match kubernetes.**>
            @type elasticsearch
            @id out_es
            @log_level info
            include_tag_key true
            host elasticsearch-master
            port 9200
            scheme http
            logstash_format true
            logstash_prefix intelligence-os
            <buffer>
              @type file
              path /var/log/fluentd-buffers/kubernetes.system.buffer
              flush_mode interval
              retry_type exponential_backoff
              flush_thread_count 2
              flush_interval 5s
              retry_forever
              retry_max_interval 30
              chunk_limit_size 2M
              queue_limit_length 8
              overflow_action block
            </buffer>
          </match>
        EOF
      }
    })
  ]

  depends_on = [helm_release.elasticsearch]
}

# Jaeger for distributed tracing
resource "helm_release" "jaeger" {
  count = var.jaeger_enabled ? 1 : 0
  
  name       = "jaeger"
  repository = "https://jaegertracing.github.io/helm-charts"
  chart      = "jaeger"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "0.71.2"

  values = [
    yamlencode({
      provisionDataStore = {
        cassandra = false
        elasticsearch = true
      }
      
      storage = {
        type = "elasticsearch"
        elasticsearch = {
          host = "elasticsearch-master"
          port = 9200
          scheme = "http"
        }
      }
      
      agent = {
        enabled = true
        daemonset = {
          useHostPort = true
        }
      }
      
      collector = {
        enabled = true
        replicaCount = var.environment == "production" ? 3 : 1
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
      
      query = {
        enabled = true
        replicaCount = var.environment == "production" ? 2 : 1
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
    })
  ]

  depends_on = [helm_release.elasticsearch]
}

# Custom Grafana dashboards for Intelligence OS
resource "kubernetes_config_map" "grafana_dashboards" {
  count = var.grafana_enabled ? 1 : 0
  
  metadata {
    name      = "intelligence-os-dashboards"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
    labels = {
      grafana_dashboard = "1"
    }
  }

  data = {
    "intelligence-os-overview.json" = jsonencode({
      dashboard = {
        id    = null
        title = "Intelligence OS - Overview"
        tags  = ["intelligence-os"]
        timezone = "browser"
        panels = [
          {
            id = 1
            title = "Request Rate"
            type = "graph"
            targets = [
              {
                expr = "sum(rate(http_requests_total{job=\"intelligence-os\"}[5m]))"
                legendFormat = "Requests/sec"
              }
            ]
            yAxes = [
              {
                label = "requests/sec"
              }
            ]
          },
          {
            id = 2
            title = "Response Time"
            type = "graph"
            targets = [
              {
                expr = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=\"intelligence-os\"}[5m])) by (le))"
                legendFormat = "95th percentile"
              },
              {
                expr = "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{job=\"intelligence-os\"}[5m])) by (le))"
                legendFormat = "50th percentile"
              }
            ]
            yAxes = [
              {
                label = "seconds"
              }
            ]
          },
          {
            id = 3
            title = "Error Rate"
            type = "graph"
            targets = [
              {
                expr = "sum(rate(http_requests_total{job=\"intelligence-os\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{job=\"intelligence-os\"}[5m]))"
                legendFormat = "Error Rate"
              }
            ]
            yAxes = [
              {
                label = "percentage"
                max = 1
                min = 0
              }
            ]
          },
          {
            id = 4
            title = "Active Users"
            type = "stat"
            targets = [
              {
                expr = "intelligence_os_active_users"
                legendFormat = "Active Users"
              }
            ]
          },
          {
            id = 5
            title = "AI Processing Queue"
            type = "graph"
            targets = [
              {
                expr = "intelligence_os_ai_queue_size"
                legendFormat = "Queue Size"
              }
            ]
          },
          {
            id = 6
            title = "Memory Usage"
            type = "graph"
            targets = [
              {
                expr = "sum(container_memory_usage_bytes{pod=~\"intelligence-os-.*\"}) by (pod)"
                legendFormat = "{{pod}}"
              }
            ]
            yAxes = [
              {
                label = "bytes"
              }
            ]
          }
        ]
        time = {
          from = "now-1h"
          to   = "now"
        }
        refresh = "30s"
      }
    })
  }
}

# Prometheus rules for Intelligence OS
resource "kubernetes_manifest" "prometheus_rules" {
  count = var.prometheus_enabled ? 1 : 0
  
  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "PrometheusRule"
    metadata = {
      name      = "intelligence-os-rules"
      namespace = kubernetes_namespace.monitoring.metadata[0].name
      labels = {
        app = "intelligence-os"
      }
    }
    spec = {
      groups = [
        {
          name = "intelligence-os.rules"
          rules = [
            {
              alert = "HighErrorRate"
              expr  = "sum(rate(http_requests_total{job=\"intelligence-os\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{job=\"intelligence-os\"}[5m])) > 0.05"
              for   = "5m"
              labels = {
                severity = "warning"
              }
              annotations = {
                summary     = "High error rate detected"
                description = "Error rate is above 5% for more than 5 minutes"
              }
            },
            {
              alert = "HighResponseTime"
              expr  = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=\"intelligence-os\"}[5m])) by (le)) > 2"
              for   = "5m"
              labels = {
                severity = "warning"
              }
              annotations = {
                summary     = "High response time detected"
                description = "95th percentile response time is above 2 seconds"
              }
            },
            {
              alert = "PodCrashLooping"
              expr  = "rate(kube_pod_container_status_restarts_total{namespace=\"intelligence-os-${var.environment}\"}[15m]) > 0"
              for   = "5m"
              labels = {
                severity = "critical"
              }
              annotations = {
                summary     = "Pod is crash looping"
                description = "Pod {{$labels.pod}} in namespace {{$labels.namespace}} is restarting frequently"
              }
            },
            {
              alert = "HighMemoryUsage"
              expr  = "sum(container_memory_usage_bytes{pod=~\"intelligence-os-.*\"}) / sum(container_spec_memory_limit_bytes{pod=~\"intelligence-os-.*\"}) > 0.9"
              for   = "5m"
              labels = {
                severity = "warning"
              }
              annotations = {
                summary     = "High memory usage"
                description = "Memory usage is above 90% of the limit"
              }
            },
            {
              alert = "AIProcessingQueueBacklog"
              expr  = "intelligence_os_ai_queue_size > 100"
              for   = "10m"
              labels = {
                severity = "warning"
              }
              annotations = {
                summary     = "AI processing queue backlog"
                description = "AI processing queue has more than 100 items for over 10 minutes"
              }
            }
          ]
        }
      ]
    }
  }

  depends_on = [helm_release.prometheus_operator]
}

# Ingress for monitoring services
resource "kubernetes_ingress_v1" "monitoring" {
  metadata {
    name      = "monitoring-ingress"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
    
    annotations = {
      "kubernetes.io/ingress.class"           = "nginx"
      "nginx.ingress.kubernetes.io/ssl-redirect" = "true"
      "cert-manager.io/cluster-issuer"        = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/auth-type" = "basic"
      "nginx.ingress.kubernetes.io/auth-secret" = "monitoring-auth"
      "nginx.ingress.kubernetes.io/auth-realm" = "Authentication Required"
    }
  }

  spec {
    tls {
      hosts       = ["monitoring.intelligence-os.example.com"]
      secret_name = "monitoring-tls"
    }

    rule {
      host = "monitoring.intelligence-os.example.com"
      
      http {
        path {
          path      = "/grafana"
          path_type = "Prefix"
          
          backend {
            service {
              name = "prometheus-operator-grafana"
              port {
                number = 80
              }
            }
          }
        }
        
        path {
          path      = "/prometheus"
          path_type = "Prefix"
          
          backend {
            service {
              name = "prometheus-operator-kube-p-prometheus"
              port {
                number = 9090
              }
            }
          }
        }
        
        path {
          path      = "/kibana"
          path_type = "Prefix"
          
          backend {
            service {
              name = "kibana-kibana"
              port {
                number = 5601
              }
            }
          }
        }
        
        path {
          path      = "/jaeger"
          path_type = "Prefix"
          
          backend {
            service {
              name = "jaeger-query"
              port {
                number = 16686
              }
            }
          }
        }
      }
    }
  }
}

# Basic auth secret for monitoring services
resource "kubernetes_secret" "monitoring_auth" {
  metadata {
    name      = "monitoring-auth"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
  }

  type = "Opaque"

  data = {
    # admin:admin (change in production)
    auth = base64encode("admin:$2y$10$2b2cu/bigjU/XG6zU4b5KuF8wJlhHyoJfnvpiYj6aDnHOKTlBe8AW")
  }
}

# Outputs
output "service_urls" {
  description = "Monitoring service URLs"
  value = {
    grafana    = var.grafana_enabled ? "https://monitoring.intelligence-os.example.com/grafana" : null
    prometheus = var.prometheus_enabled ? "https://monitoring.intelligence-os.example.com/prometheus" : null
    kibana     = var.kibana_enabled ? "https://monitoring.intelligence-os.example.com/kibana" : null
    jaeger     = var.jaeger_enabled ? "https://monitoring.intelligence-os.example.com/jaeger" : null
  }
}

output "namespace" {
  description = "Monitoring namespace"
  value       = kubernetes_namespace.monitoring.metadata[0].name
}