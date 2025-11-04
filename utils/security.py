"""
Security module for production GLASS Data Standardizer
"""

import hashlib
import hmac
import secrets
import time
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security management for production"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self.rate_limits = {}
        self.blocked_ips = set()
        self.suspicious_activities = []
        
        # Security patterns
        self.malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'<iframe.*?>',
            r'<object.*?>',
            r'<embed.*?>',
            r'<link.*?>',
            r'<meta.*?>'
        ]
        
        # File validation patterns
        self.allowed_file_signatures = {
            b'\x50\x4b\x03\x04': '.xlsx',  # Excel
            b'\x50\x4b\x05\x06': '.xlsx',  # Excel
            b'\x50\x4b\x07\x08': '.xlsx',  # Excel
            b'\xd0\xcf\x11\xe0': '.xls',   # Old Excel
            b'\x09\x08\x10\x00': '.xls',   # Old Excel
        }
    
    def validate_file_upload(self, uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file for security"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check file size
            file_size = len(uploaded_file.getvalue())
            max_size = 100 * 1024 * 1024  # 100MB
            
            if file_size > max_size:
                validation_result['valid'] = False
                validation_result['errors'].append(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (100MB)")
            
            # Check file extension
            file_extension = Path(uploaded_file.name).suffix.lower()
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            
            if file_extension not in allowed_extensions:
                validation_result['valid'] = False
                validation_result['errors'].append(f"File extension '{file_extension}' is not allowed. Allowed: {', '.join(allowed_extensions)}")
            
            # Check file signature
            file_content = uploaded_file.getvalue()
            file_signature = file_content[:8]
            
            if file_extension == '.xlsx' or file_extension == '.xls':
                if not any(file_signature.startswith(sig) for sig in self.allowed_file_signatures.keys()):
                    validation_result['warnings'].append("File signature doesn't match expected format")
            
            # Check for malicious content
            if self._contains_malicious_content(file_content):
                validation_result['valid'] = False
                validation_result['errors'].append("File contains potentially malicious content")
            
            # Check filename
            if self._is_suspicious_filename(uploaded_file.name):
                validation_result['warnings'].append("Filename contains suspicious characters")
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            validation_result['valid'] = False
            validation_result['errors'].append("File validation failed")
        
        return validation_result
    
    def _contains_malicious_content(self, content: bytes) -> bool:
        """Check if content contains malicious patterns"""
        try:
            content_str = content.decode('utf-8', errors='ignore').lower()
            
            for pattern in self.malicious_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return True  # If we can't decode, consider it suspicious
    
    def _is_suspicious_filename(self, filename: str) -> bool:
        """Check if filename is suspicious"""
        suspicious_patterns = [
            r'\.\.',  # Path traversal
            r'[<>:"|?*]',  # Invalid characters
            r'\.(exe|bat|cmd|scr|pif|com)$',  # Executable extensions
            r'\.(php|asp|jsp|py|rb|pl)$',  # Script extensions
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        
        return False
    
    def validate_input(self, input_data: str, input_type: str = 'general') -> Dict[str, Any]:
        """Validate user input for security"""
        validation_result = {
            'valid': True,
            'errors': [],
            'sanitized': input_data
        }
        
        try:
            # Check for SQL injection patterns
            sql_patterns = [
                r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
                r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
                r'(\'|\"|;|--|\/\*|\*\/)',
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    validation_result['errors'].append("Input contains potentially malicious SQL patterns")
                    validation_result['valid'] = False
            
            # Check for XSS patterns
            xss_patterns = [
                r'<script.*?>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe.*?>',
                r'<object.*?>',
                r'<embed.*?>'
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    validation_result['errors'].append("Input contains potentially malicious XSS patterns")
                    validation_result['valid'] = False
            
            # Sanitize input
            if validation_result['valid']:
                validation_result['sanitized'] = self._sanitize_input(input_data)
            
        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            validation_result['valid'] = False
            validation_result['errors'].append("Input validation failed")
        
        return validation_result
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize user input"""
        # Remove or escape potentially dangerous characters
        sanitized = input_data
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Escape special characters
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        sanitized = sanitized.replace('&', '&amp;')
        
        return sanitized
    
    def check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        key = f"{client_ip}:{endpoint}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old requests outside the window
        window_start = current_time - 3600  # 1 hour window
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        max_requests = 100  # 100 requests per hour
        if len(self.rate_limits[key]) >= max_requests:
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], client_ip: str = None):
        """Log security events"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'details': details,
            'client_ip': client_ip or self._get_client_ip(),
            'user_agent': self._get_user_agent()
        }
        
        self.suspicious_activities.append(event)
        logger.warning(f"Security event: {event_type} - {details}")
        
        # Keep only last 1000 events
        if len(self.suspicious_activities) > 1000:
            self.suspicious_activities = self.suspicious_activities[-1000:]
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            # This would need to be implemented based on your deployment
            # For now, return a placeholder
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_user_agent(self) -> str:
        """Get user agent"""
        try:
            # This would need to be implemented based on your deployment
            return "unknown"
        except Exception:
            return "unknown"
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return hmac.new(
            self.secret_key,
            f"{time.time()}".encode(),
            hashlib.sha256
        ).hexdigest()
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token"""
        try:
            # In a real implementation, you'd store and validate tokens
            # For now, just check if it's a valid format
            return len(token) == 64 and all(c in '0123456789abcdef' for c in token)
        except Exception:
            return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary for monitoring"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'suspicious_activities': len(self.suspicious_activities),
            'rate_limited_ips': len([
                ip for ip, requests in self.rate_limits.items() 
                if len(requests) > 50
            ]),
            'recent_events': self.suspicious_activities[-10:] if self.suspicious_activities else []
        }

# Global security manager instance
security_manager = SecurityManager(secrets.token_urlsafe(32))
