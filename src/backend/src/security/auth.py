"""
Authentication and Authorization Manager for Intelligence OS
Implements JWT-based authentication with role-based access control
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from typing import Dict, List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Comprehensive authentication and authorization manager"""
    
    def __init__(self, app=None):
        self.app = app
        self.jwt_manager = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the authentication manager with Flask app"""
        self.app = app
        
        # Configure JWT
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY'))
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))
        
        self.jwt_manager = JWTManager(app)
        
        # Register JWT callbacks
        self._register_jwt_callbacks()
        
        logger.info("AuthManager initialized successfully")
    
    def _register_jwt_callbacks(self):
        """Register JWT callback functions"""
        
        @self.jwt_manager.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            """Check if token is revoked"""
            # Implement token blacklist logic here
            # For now, return False (no tokens are revoked)
            return False
        
        @self.jwt_manager.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            """Handle expired token"""
            return jsonify({
                'success': False,
                'error': 'token_expired',
                'message': 'The token has expired'
            }), 401
        
        @self.jwt_manager.invalid_token_loader
        def invalid_token_callback(error):
            """Handle invalid token"""
            return jsonify({
                'success': False,
                'error': 'invalid_token',
                'message': 'Invalid token provided'
            }), 401
        
        @self.jwt_manager.unauthorized_loader
        def missing_token_callback(error):
            """Handle missing token"""
            return jsonify({
                'success': False,
                'error': 'missing_token',
                'message': 'Authorization token is required'
            }), 401
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_tokens(self, user_id: str, user_role: str = 'user', additional_claims: Dict = None) -> Dict[str, str]:
        """Generate access and refresh tokens for a user"""
        additional_claims = additional_claims or {}
        additional_claims.update({
            'role': user_role,
            'iat': datetime.utcnow(),
            'type': 'access'
        })
        
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims
        )
        
        refresh_claims = additional_claims.copy()
        refresh_claims['type'] = 'refresh'
        
        refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims=refresh_claims
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
        }
    
    def require_auth(self, roles: List[str] = None):
        """Decorator to require authentication and optionally specific roles"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                try:
                    current_user_id = get_jwt_identity()
                    current_claims = get_jwt()
                    current_user_role = current_claims.get('role', 'user')
                    
                    # Store user info in Flask g object for use in route handlers
                    g.current_user_id = current_user_id
                    g.current_user_role = current_user_role
                    g.current_user_claims = current_claims
                    
                    # Check role requirements
                    if roles and current_user_role not in roles:
                        return jsonify({
                            'success': False,
                            'error': 'insufficient_permissions',
                            'message': f'Required roles: {roles}. Current role: {current_user_role}'
                        }), 403
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"Authentication error: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'authentication_error',
                        'message': 'Authentication failed'
                    }), 401
            
            return decorated_function
        return decorator
    
    def require_admin(self):
        """Decorator to require admin role"""
        return self.require_auth(roles=['admin'])
    
    def require_user_or_admin(self):
        """Decorator to require user or admin role"""
        return self.require_auth(roles=['user', 'admin'])
    
    def optional_auth(self):
        """Decorator for optional authentication"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Try to get JWT token, but don't fail if it's missing
                    from flask_jwt_extended import verify_jwt_in_request
                    verify_jwt_in_request(optional=True)
                    
                    current_user_id = get_jwt_identity()
                    if current_user_id:
                        current_claims = get_jwt()
                        g.current_user_id = current_user_id
                        g.current_user_role = current_claims.get('role', 'user')
                        g.current_user_claims = current_claims
                    else:
                        g.current_user_id = None
                        g.current_user_role = None
                        g.current_user_claims = None
                        
                except Exception:
                    # If there's any error with JWT, treat as unauthenticated
                    g.current_user_id = None
                    g.current_user_role = None
                    g.current_user_claims = None
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user information"""
        if hasattr(g, 'current_user_id') and g.current_user_id:
            return {
                'id': g.current_user_id,
                'role': g.current_user_role,
                'claims': g.current_user_claims
            }
        return None
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key for external integrations"""
        # Implement API key validation logic
        # This could check against a database of valid API keys
        valid_api_keys = os.getenv('VALID_API_KEYS', '').split(',')
        return api_key in valid_api_keys
    
    def require_api_key(self):
        """Decorator to require valid API key"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key')
                if not api_key:
                    return jsonify({
                        'success': False,
                        'error': 'missing_api_key',
                        'message': 'API key is required'
                    }), 401
                
                if not self.validate_api_key(api_key):
                    return jsonify({
                        'success': False,
                        'error': 'invalid_api_key',
                        'message': 'Invalid API key'
                    }), 401
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

# Global auth manager instance
auth_manager = AuthManager()