"""Configuration settings for AWS MCP server."""

from typing import Dict, Any, Optional
import os


class Settings:
    """Application settings and configuration."""
    
    # Default server settings
    DEFAULT_PORT = 8888
    DEFAULT_TRANSPORT = 'stdio'
    
    # AWS service limits and defaults
    DEFAULT_MAX_RESULTS = {
        'ec2_instances': 1000,
        'ec2_security_groups': 1000,
        'ec2_vpcs': 1000,
        'rds_instances': 100,
        's3_objects': 1000,
    }
    
    # Timeout settings (in seconds)
    DEFAULT_TIMEOUTS = {
        'aws_api_call': 30,
        'pagination_timeout': 300,
    }
    
    def __init__(self):
        """Initialize settings from environment variables."""
        self.port = int(os.getenv('AWS_MCP_PORT', self.DEFAULT_PORT))
        self.transport = os.getenv('AWS_MCP_TRANSPORT', self.DEFAULT_TRANSPORT)
        self.debug = os.getenv('AWS_MCP_DEBUG', 'false').lower() == 'true'
        
        # AWS specific settings
        self.default_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.default_profile = os.getenv('AWS_PROFILE', 'default')
        
        # Performance settings
        self.max_concurrent_requests = int(os.getenv('AWS_MCP_MAX_CONCURRENT', '10'))
        self.enable_pagination = os.getenv('AWS_MCP_ENABLE_PAGINATION', 'true').lower() == 'true'
    
    def get_max_results(self, service_operation: str) -> int:
        """Get maximum results for a service operation.
        
        Args:
            service_operation: Service operation key (e.g., 'ec2_instances')
            
        Returns:
            Maximum results limit
        """
        env_key = f'AWS_MCP_MAX_RESULTS_{service_operation.upper()}'
        env_value = os.getenv(env_key)
        
        if env_value:
            try:
                return int(env_value)
            except ValueError:
                pass
        
        return self.DEFAULT_MAX_RESULTS.get(service_operation, 100)
    
    def get_timeout(self, operation_type: str) -> int:
        """Get timeout for an operation type.
        
        Args:
            operation_type: Type of operation (e.g., 'aws_api_call')
            
        Returns:
            Timeout in seconds
        """
        env_key = f'AWS_MCP_TIMEOUT_{operation_type.upper()}'
        env_value = os.getenv(env_key)
        
        if env_value:
            try:
                return int(env_value)
            except ValueError:
                pass
        
        return self.DEFAULT_TIMEOUTS.get(operation_type, 30)


# Global settings instance
settings = Settings()