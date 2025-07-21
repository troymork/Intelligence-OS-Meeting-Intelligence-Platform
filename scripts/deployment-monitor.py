#!/usr/bin/env python3

"""
Deployment Monitoring Dashboard
Real-time monitoring of deployment status and health metrics
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentMonitor:
    """Monitor deployment status and health metrics"""
    
    def __init__(self, namespace: str = "intelligence-os-production"):
        self.namespace = namespace
        self.k8s_client = None
        self.apps_v1 = None
        self.core_v1 = None
        self.metrics = {}
        
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()  # For running inside cluster
        except:
            try:
                config.load_kube_config()  # For running outside cluster
            except Exception as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        
    async def get_deployment_status(self) -> Dict:
        """Get status of all deployments"""
        deployments = {}
        
        try:
            deployment_list = self.apps_v1.list_namespaced_deployment(self.namespace)
            
            for deployment in deployment_list.items:
                name = deployment.metadata.name
                status = deployment.status
                
                deployments[name] = {
                    'name': name,
                    'replicas': {
                        'desired': status.replicas or 0,
                        'ready': status.ready_replicas or 0,
                        'available': status.available_replicas or 0,
                        'unavailable': status.unavailable_replicas or 0
                    },
                    'conditions': [
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason,
                            'message': condition.message,
                            'last_update': condition.last_update_time.isoformat() if condition.last_update_time else None
                        }
                        for condition in (status.conditions or [])
                    ],
                    'created': deployment.metadata.creation_timestamp.isoformat(),
                    'generation': deployment.metadata.generation,
                    'observed_generation': status.observed_generation
                }
                
        except ApiException as e:
            logger.error(f"Error getting deployment status: {e}")
            
        return deployments
    
    async def get_pod_status(self) -> Dict:
        """Get status of all pods"""
        pods = {}
        
        try:
            pod_list = self.core_v1.list_namespaced_pod(self.namespace)
            
            for pod in pod_list.items:
                name = pod.metadata.name
                status = pod.status
                
                pods[name] = {
                    'name': name,
                    'phase': status.phase,
                    'ready': sum(1 for condition in (status.conditions or []) 
                               if condition.type == 'Ready' and condition.status == 'True'),
                    'restarts': sum(container.restart_count for container in (status.container_statuses or [])),
                    'node': pod.spec.node_name,
                    'created': pod.metadata.creation_timestamp.isoformat(),
                    'containers': [
                        {
                            'name': container.name,
                            'ready': container.ready,
                            'restart_count': container.restart_count,
                            'state': self._get_container_state(container.state)
                        }
                        for container in (status.container_statuses or [])
                    ]
                }
                
        except ApiException as e:
            logger.error(f"Error getting pod status: {e}")
            
        return pods
    
    def _get_container_state(self, state) -> Dict:
        """Extract container state information"""
        if state.running:
            return {
                'status': 'running',
                'started_at': state.running.started_at.isoformat() if state.running.started_at else None
            }
        elif state.waiting:
            return {
                'status': 'waiting',
                'reason': state.waiting.reason,
                'message': state.waiting.message
            }
        elif state.terminated:
            return {
                'status': 'terminated',
                'reason': state.terminated.reason,
                'exit_code': state.terminated.exit_code,
                'finished_at': state.terminated.finished_at.isoformat() if state.terminated.finished_at else None
            }
        else:
            return {'status': 'unknown'}
    
    async def get_service_status(self) -> Dict:
        """Get status of all services"""
        services = {}
        
        try:
            service_list = self.core_v1.list_namespaced_service(self.namespace)
            
            for service in service_list.items:
                name = service.metadata.name
                spec = service.spec
                status = service.status
                
                services[name] = {
                    'name': name,
                    'type': spec.type,
                    'cluster_ip': spec.cluster_ip,
                    'ports': [
                        {
                            'port': port.port,
                            'target_port': port.target_port,
                            'protocol': port.protocol
                        }
                        for port in (spec.ports or [])
                    ],
                    'selector': spec.selector or {},
                    'load_balancer': {
                        'ingress': [
                            {
                                'ip': ingress.ip,
                                'hostname': ingress.hostname
                            }
                            for ingress in (status.load_balancer.ingress or [])
                        ] if status.load_balancer else []
                    }
                }
                
        except ApiException as e:
            logger.error(f"Error getting service status: {e}")
            
        return services
    
    async def check_health_endpoints(self) -> Dict:
        """Check health endpoints for all services"""
        health_status = {}
        
        # Define health check URLs based on environment
        if self.namespace == "intelligence-os-production":
            urls = {
                'frontend': 'https://intelligence-os.example.com/health',
                'backend': 'https://api.intelligence-os.example.com/health'
            }
        elif self.namespace == "intelligence-os-staging":
            urls = {
                'frontend': 'https://staging.intelligence-os.example.com/health',
                'backend': 'https://api.staging.intelligence-os.example.com/health'
            }
        else:
            # For local or other environments, skip external health checks
            return health_status
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for service, url in urls.items():
                try:
                    start_time = time.time()
                    async with session.get(url) as response:
                        response_time = time.time() - start_time
                        
                        health_status[service] = {
                            'url': url,
                            'status_code': response.status,
                            'response_time': response_time,
                            'healthy': response.status == 200,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                health_status[service]['response_data'] = data
                            except:
                                health_status[service]['response_data'] = await response.text()
                                
                except Exception as e:
                    health_status[service] = {
                        'url': url,
                        'error': str(e),
                        'healthy': False,
                        'timestamp': datetime.utcnow().isoformat()
                    }
        
        return health_status
    
    async def get_resource_usage(self) -> Dict:
        """Get resource usage metrics"""
        # This would typically integrate with Prometheus or similar monitoring
        # For now, we'll get basic resource requests/limits from deployments
        resource_usage = {}
        
        try:
            deployment_list = self.apps_v1.list_namespaced_deployment(self.namespace)
            
            for deployment in deployment_list.items:
                name = deployment.metadata.name
                containers = deployment.spec.template.spec.containers
                
                total_cpu_requests = 0
                total_memory_requests = 0
                total_cpu_limits = 0
                total_memory_limits = 0
                
                for container in containers:
                    if container.resources:
                        if container.resources.requests:
                            cpu_req = container.resources.requests.get('cpu', '0')
                            mem_req = container.resources.requests.get('memory', '0')
                            total_cpu_requests += self._parse_cpu(cpu_req)
                            total_memory_requests += self._parse_memory(mem_req)
                        
                        if container.resources.limits:
                            cpu_limit = container.resources.limits.get('cpu', '0')
                            mem_limit = container.resources.limits.get('memory', '0')
                            total_cpu_limits += self._parse_cpu(cpu_limit)
                            total_memory_limits += self._parse_memory(mem_limit)
                
                resource_usage[name] = {
                    'cpu': {
                        'requests': total_cpu_requests,
                        'limits': total_cpu_limits
                    },
                    'memory': {
                        'requests': total_memory_requests,
                        'limits': total_memory_limits
                    }
                }
                
        except ApiException as e:
            logger.error(f"Error getting resource usage: {e}")
            
        return resource_usage
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU resource string to millicores"""
        if not cpu_str or cpu_str == '0':
            return 0
        
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1])
        else:
            return float(cpu_str) * 1000
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory resource string to bytes"""
        if not memory_str or memory_str == '0':
            return 0
        
        units = {
            'Ki': 1024,
            'Mi': 1024**2,
            'Gi': 1024**3,
            'Ti': 1024**4
        }
        
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return int(float(memory_str[:-len(unit)]) * multiplier)
        
        return int(memory_str)
    
    async def get_deployment_history(self) -> Dict:
        """Get deployment history and rollout status"""
        history = {}
        
        try:
            deployment_list = self.apps_v1.list_namespaced_deployment(self.namespace)
            
            for deployment in deployment_list.items:
                name = deployment.metadata.name
                
                # Get replica sets for this deployment
                rs_list = self.apps_v1.list_namespaced_replica_set(
                    self.namespace,
                    label_selector=f"app={name}"
                )
                
                replica_sets = []
                for rs in rs_list.items:
                    replica_sets.append({
                        'name': rs.metadata.name,
                        'replicas': rs.status.replicas or 0,
                        'ready_replicas': rs.status.ready_replicas or 0,
                        'created': rs.metadata.creation_timestamp.isoformat(),
                        'revision': rs.metadata.annotations.get('deployment.kubernetes.io/revision', 'unknown')
                    })
                
                # Sort by creation time
                replica_sets.sort(key=lambda x: x['created'], reverse=True)
                
                history[name] = {
                    'current_revision': deployment.metadata.annotations.get('deployment.kubernetes.io/revision', 'unknown'),
                    'replica_sets': replica_sets[:5]  # Keep last 5 revisions
                }
                
        except ApiException as e:
            logger.error(f"Error getting deployment history: {e}")
            
        return history
    
    async def collect_all_metrics(self) -> Dict:
        """Collect all monitoring metrics"""
        logger.info(f"Collecting metrics for namespace: {self.namespace}")
        
        # Collect all metrics concurrently
        tasks = [
            self.get_deployment_status(),
            self.get_pod_status(),
            self.get_service_status(),
            self.check_health_endpoints(),
            self.get_resource_usage(),
            self.get_deployment_history()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'namespace': self.namespace,
            'deployments': results[0] if not isinstance(results[0], Exception) else {},
            'pods': results[1] if not isinstance(results[1], Exception) else {},
            'services': results[2] if not isinstance(results[2], Exception) else {},
            'health_checks': results[3] if not isinstance(results[3], Exception) else {},
            'resource_usage': results[4] if not isinstance(results[4], Exception) else {},
            'deployment_history': results[5] if not isinstance(results[5], Exception) else {}
        }
        
        # Calculate summary statistics
        metrics['summary'] = self._calculate_summary(metrics)
        
        return metrics
    
    def _calculate_summary(self, metrics: Dict) -> Dict:
        """Calculate summary statistics"""
        deployments = metrics.get('deployments', {})
        pods = metrics.get('pods', {})
        health_checks = metrics.get('health_checks', {})
        
        # Deployment summary
        total_deployments = len(deployments)
        healthy_deployments = sum(
            1 for d in deployments.values()
            if d['replicas']['ready'] == d['replicas']['desired'] and d['replicas']['desired'] > 0
        )
        
        # Pod summary
        total_pods = len(pods)
        running_pods = sum(1 for p in pods.values() if p['phase'] == 'Running')
        
        # Health check summary
        total_health_checks = len(health_checks)
        healthy_endpoints = sum(1 for h in health_checks.values() if h.get('healthy', False))
        
        return {
            'deployments': {
                'total': total_deployments,
                'healthy': healthy_deployments,
                'health_percentage': (healthy_deployments / total_deployments * 100) if total_deployments > 0 else 0
            },
            'pods': {
                'total': total_pods,
                'running': running_pods,
                'running_percentage': (running_pods / total_pods * 100) if total_pods > 0 else 0
            },
            'health_checks': {
                'total': total_health_checks,
                'healthy': healthy_endpoints,
                'health_percentage': (healthy_endpoints / total_health_checks * 100) if total_health_checks > 0 else 0
            },
            'overall_health': 'healthy' if (
                healthy_deployments == total_deployments and
                running_pods == total_pods and
                healthy_endpoints == total_health_checks
            ) else 'degraded'
        }
    
    def save_metrics(self, metrics: Dict, filename: str = None):
        """Save metrics to file"""
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"deployment_metrics_{self.namespace}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Metrics saved to {filename}")
    
    def print_summary(self, metrics: Dict):
        """Print a summary of the metrics"""
        summary = metrics.get('summary', {})
        
        print(f"\n{'='*60}")
        print(f"Deployment Monitor Summary - {self.namespace}")
        print(f"Timestamp: {metrics.get('timestamp', 'unknown')}")
        print(f"{'='*60}")
        
        # Overall health
        overall_health = summary.get('overall_health', 'unknown')
        health_emoji = '✅' if overall_health == 'healthy' else '⚠️'
        print(f"Overall Health: {health_emoji} {overall_health.upper()}")
        
        # Deployments
        dep_summary = summary.get('deployments', {})
        print(f"\nDeployments: {dep_summary.get('healthy', 0)}/{dep_summary.get('total', 0)} healthy ({dep_summary.get('health_percentage', 0):.1f}%)")
        
        # Pods
        pod_summary = summary.get('pods', {})
        print(f"Pods: {pod_summary.get('running', 0)}/{pod_summary.get('total', 0)} running ({pod_summary.get('running_percentage', 0):.1f}%)")
        
        # Health checks
        health_summary = summary.get('health_checks', {})
        print(f"Health Checks: {health_summary.get('healthy', 0)}/{health_summary.get('total', 0)} healthy ({health_summary.get('health_percentage', 0):.1f}%)")
        
        # Detailed deployment status
        deployments = metrics.get('deployments', {})
        if deployments:
            print(f"\nDetailed Deployment Status:")
            for name, deployment in deployments.items():
                replicas = deployment['replicas']
                status_emoji = '✅' if replicas['ready'] == replicas['desired'] else '❌'
                print(f"  {status_emoji} {name}: {replicas['ready']}/{replicas['desired']} replicas ready")
        
        # Health check details
        health_checks = metrics.get('health_checks', {})
        if health_checks:
            print(f"\nHealth Check Details:")
            for service, health in health_checks.items():
                status_emoji = '✅' if health.get('healthy', False) else '❌'
                response_time = health.get('response_time', 0)
                print(f"  {status_emoji} {service}: {health.get('status_code', 'N/A')} ({response_time:.3f}s)")
        
        print(f"{'='*60}\n")

async def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Monitor')
    parser.add_argument('--namespace', '-n', default='intelligence-os-production',
                       help='Kubernetes namespace to monitor')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Monitoring interval in seconds')
    parser.add_argument('--output', '-o', help='Output file for metrics')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    
    args = parser.parse_args()
    
    monitor = DeploymentMonitor(args.namespace)
    
    if args.once:
        # Run once and exit
        metrics = await monitor.collect_all_metrics()
        monitor.print_summary(metrics)
        
        if args.output:
            monitor.save_metrics(metrics, args.output)
    else:
        # Continuous monitoring
        logger.info(f"Starting continuous monitoring of namespace: {args.namespace}")
        logger.info(f"Monitoring interval: {args.interval} seconds")
        
        while True:
            try:
                metrics = await monitor.collect_all_metrics()
                monitor.print_summary(metrics)
                
                if args.output:
                    monitor.save_metrics(metrics, args.output)
                
                await asyncio.sleep(args.interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                await asyncio.sleep(args.interval)

if __name__ == "__main__":
    asyncio.run(main())