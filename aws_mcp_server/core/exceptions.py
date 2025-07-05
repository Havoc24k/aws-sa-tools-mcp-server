"""Custom exception classes for AWS MCP server."""


class AWSMCPError(Exception):
    """Base exception for AWS MCP server errors."""
    pass


class InvalidProfileError(AWSMCPError):
    """Raised when an invalid AWS profile is specified."""
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Invalid or inaccessible AWS profile: {profile_name}")


class InvalidRegionError(AWSMCPError):
    """Raised when an invalid AWS region is specified."""
    
    def __init__(self, region: str):
        self.region = region
        super().__init__(f"Invalid AWS region: {region}")


class AWSServiceError(AWSMCPError):
    """Raised when an AWS service operation fails."""
    
    def __init__(self, service: str, operation: str, error_message: str):
        self.service = service
        self.operation = operation
        self.error_message = error_message
        super().__init__(f"AWS {service} {operation} failed: {error_message}")


class ParameterValidationError(AWSMCPError):
    """Raised when parameter validation fails."""
    
    def __init__(self, parameter: str, message: str):
        self.parameter = parameter
        self.message = message
        super().__init__(f"Parameter validation failed for '{parameter}': {message}")