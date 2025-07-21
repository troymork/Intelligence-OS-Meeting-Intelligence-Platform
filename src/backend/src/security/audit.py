"""
Audit Logger for Intelligence OS
Handles security auditing and compliance logging
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)

class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    SECURITY_VIOLATION = "security_violation"
    CONFIGURATION_CHANGE = "configuration_change"
    USER_ACTION = "user_action"
    API_ACCESS = "api_access"
    ERROR = "error"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLogger:
    """Security audit logging manager"""
    
    def __init__(self):
        self.audit_log_file = os.getenv('AUDIT_LOG_FILE', 'logs/audit.log')
        self.enable_console_output = os.getenv('AUDIT_CONSOLE_OUTPUT', 'false').lower() == 'true'
        self.audit_retention_days = int(os.getenv('AUDIT_RETENTION_DAYS', '90'))
        
        # Ensure audit log directory exists
        os.makedirs(os.path.dirname(self.audit_log_file), exist_ok=True)
        
        # Configure audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        file_handler = logging.FileHandler(self.audit_log_file)
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        self.audit_logger.addHandler(file_handler)
        
        # Console handler if enabled
        if self.enable_console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.audit_logger.addHandler(console_handler)
    
    def log_event(self, event_type: AuditEventType, severity: AuditSeverity,
                  message: str, user_id: Optional[str] = None,
                  session_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, resource: Optional[str] = None,
                  action: Optional[str] = None, outcome: str = "success",
                  additional_data: Optional[Dict[str, Any]] = None):
        """Log an audit event"""
        try:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type.value,
                'severity': severity.value,
                'message': message,
                'outcome': outcome,
                'user_id': user_id,
                'session_id': session_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'resource': resource,
                'action': action,
                'additional_data': additional_data or {}
            }
            
            # Log as JSON
            self.audit_logger.info(json.dumps(audit_entry))
            
        except Exception as e:
            logger.error("Audit logging failed", error=str(e))
    
    def log_authentication(self, user_id: str, outcome: str, ip_address: str = None,
                          user_agent: str = None, additional_data: Dict[str, Any] = None):
        """Log authentication event"""
        severity = AuditSeverity.MEDIUM if outcome == "success" else AuditSeverity.HIGH
        message = f"User authentication {outcome}"
        
        self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            severity=severity,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action="authenticate",
            outcome=outcome,
            additional_data=additional_data
        )
    
    def log_authorization(self, user_id: str, resource: str, action: str,
                         outcome: str, ip_address: str = None,
                         additional_data: Dict[str, Any] = None):
        """Log authorization event"""
        severity = AuditSeverity.LOW if outcome == "success" else AuditSeverity.MEDIUM
        message = f"Authorization {outcome} for {action} on {resource}"
        
        self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            severity=severity,
            message=message,
            user_id=user_id,
            resource=resource,
            action=action,
            outcome=outcome,
            ip_address=ip_address,
            additional_data=additional_data
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str = "read",
                       session_id: str = None, ip_address: str = None,
                       additional_data: Dict[str, Any] = None):
        """Log data access event"""
        message = f"Data access: {action} on {resource}"
        
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.LOW,
            message=message,
            user_id=user_id,
            session_id=session_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            additional_data=additional_data
        )
    
    def log_data_modification(self, user_id: str, resource: str, action: str,
                             session_id: str = None, ip_address: str = None,
                             changes: Dict[str, Any] = None):
        """Log data modification event"""
        message = f"Data modification: {action} on {resource}"
        additional_data = {'changes': changes} if changes else None
        
        self.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.MEDIUM,
            message=message,
            user_id=user_id,
            session_id=session_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            additional_data=additional_data
        )
    
    def log_security_violation(self, violation_type: str, ip_address: str = None,
                              user_id: str = None, user_agent: str = None,
                              details: Dict[str, Any] = None):
        """Log security violation"""
        message = f"Security violation: {violation_type}"
        
        self.log_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            severity=AuditSeverity.HIGH,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=violation_type,
            outcome="violation",
            additional_data=details
        )
    
    def log_api_access(self, endpoint: str, method: str, user_id: str = None,
                      session_id: str = None, ip_address: str = None,
                      user_agent: str = None, response_code: int = None,
                      processing_time: float = None):
        """Log API access"""
        message = f"API access: {method} {endpoint}"
        outcome = "success" if response_code and response_code < 400 else "error"
        
        additional_data = {}
        if response_code:
            additional_data['response_code'] = response_code
        if processing_time:
            additional_data['processing_time'] = processing_time
        
        self.log_event(
            event_type=AuditEventType.API_ACCESS,
            severity=AuditSeverity.LOW,
            message=message,
            user_id=user_id,
            session_id=session_id,
            resource=endpoint,
            action=method,
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=outcome,
            additional_data=additional_data
        )
    
    def log_user_action(self, user_id: str, action: str, resource: str = None,
                       session_id: str = None, ip_address: str = None,
                       outcome: str = "success", details: Dict[str, Any] = None):
        """Log user action"""
        message = f"User action: {action}"
        if resource:
            message += f" on {resource}"
        
        self.log_event(
            event_type=AuditEventType.USER_ACTION,
            severity=AuditSeverity.LOW,
            message=message,
            user_id=user_id,
            session_id=session_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            outcome=outcome,
            additional_data=details
        )
    
    def log_system_error(self, error_type: str, error_message: str,
                        user_id: str = None, session_id: str = None,
                        resource: str = None, stack_trace: str = None):
        """Log system error"""
        message = f"System error: {error_type} - {error_message}"
        
        additional_data = {}
        if stack_trace:
            additional_data['stack_trace'] = stack_trace
        
        self.log_event(
            event_type=AuditEventType.ERROR,
            severity=AuditSeverity.MEDIUM,
            message=message,
            user_id=user_id,
            session_id=session_id,
            resource=resource,
            action=error_type,
            outcome="error",
            additional_data=additional_data
        )
    
    def log_configuration_change(self, user_id: str, setting: str, old_value: Any,
                                new_value: Any, ip_address: str = None):
        """Log configuration change"""
        message = f"Configuration change: {setting}"
        
        additional_data = {
            'setting': setting,
            'old_value': str(old_value),
            'new_value': str(new_value)
        }
        
        self.log_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            severity=AuditSeverity.HIGH,
            message=message,
            user_id=user_id,
            resource=setting,
            action="modify",
            ip_address=ip_address,
            additional_data=additional_data
        )
    
    def search_audit_logs(self, start_date: datetime = None, end_date: datetime = None,
                         event_type: AuditEventType = None, user_id: str = None,
                         severity: AuditSeverity = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search audit logs (basic implementation)"""
        try:
            results = []
            
            with open(self.audit_log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Apply filters
                        if start_date and datetime.fromisoformat(entry['timestamp']) < start_date:
                            continue
                        if end_date and datetime.fromisoformat(entry['timestamp']) > end_date:
                            continue
                        if event_type and entry['event_type'] != event_type.value:
                            continue
                        if user_id and entry['user_id'] != user_id:
                            continue
                        if severity and entry['severity'] != severity.value:
                            continue
                        
                        results.append(entry)
                        
                        if len(results) >= limit:
                            break
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return results
            
        except FileNotFoundError:
            logger.warning("Audit log file not found")
            return []
        except Exception as e:
            logger.error("Audit log search failed", error=str(e))
            return []
    
    def get_audit_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get audit statistics for the specified number of days"""
        try:
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            stats = {
                'total_events': 0,
                'events_by_type': {},
                'events_by_severity': {},
                'events_by_outcome': {},
                'unique_users': set(),
                'security_violations': 0,
                'failed_authentications': 0
            }
            
            with open(self.audit_log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Check if within date range
                        if datetime.fromisoformat(entry['timestamp']) < cutoff_date:
                            continue
                        
                        stats['total_events'] += 1
                        
                        # Count by type
                        event_type = entry['event_type']
                        stats['events_by_type'][event_type] = stats['events_by_type'].get(event_type, 0) + 1
                        
                        # Count by severity
                        severity = entry['severity']
                        stats['events_by_severity'][severity] = stats['events_by_severity'].get(severity, 0) + 1
                        
                        # Count by outcome
                        outcome = entry['outcome']
                        stats['events_by_outcome'][outcome] = stats['events_by_outcome'].get(outcome, 0) + 1
                        
                        # Track unique users
                        if entry['user_id']:
                            stats['unique_users'].add(entry['user_id'])
                        
                        # Count security violations
                        if event_type == AuditEventType.SECURITY_VIOLATION.value:
                            stats['security_violations'] += 1
                        
                        # Count failed authentications
                        if event_type == AuditEventType.AUTHENTICATION.value and outcome != 'success':
                            stats['failed_authentications'] += 1
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Convert set to count
            stats['unique_users'] = len(stats['unique_users'])
            
            return stats
            
        except FileNotFoundError:
            logger.warning("Audit log file not found")
            return {'total_events': 0}
        except Exception as e:
            logger.error("Audit statistics generation failed", error=str(e))
            return {'error': str(e)}

# Global audit logger instance
audit_logger = AuditLogger()