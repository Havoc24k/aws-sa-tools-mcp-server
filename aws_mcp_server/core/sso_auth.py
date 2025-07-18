"""Simple AWS SSO authentication for MCP server."""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

import boto3


class SSOSession:
    """Simple in-memory SSO session manager."""
    
    def __init__(self):
        self._profile_name: str | None = None
        self._credentials: dict[str, Any] | None = None
        self._sso_config: dict[str, str] | None = None
    
    def authenticate(
        self,
        sso_start_url: str,
        sso_region: str,
        account_id: str,
        role_name: str
    ) -> dict[str, Any]:
        """Authenticate with AWS SSO and store session."""
        try:
            # Create temporary AWS config for this SSO session
            profile_name = f"mcp-sso-{account_id}-{role_name}"
            
            config_content = f"""[profile {profile_name}]
sso_start_url = {sso_start_url}
sso_region = {sso_region}
sso_account_id = {account_id}
sso_role_name = {role_name}
region = {sso_region}
"""
            
            # Write temporary config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.config', delete=False) as f:
                f.write(config_content)
                temp_config_path = f.name
            
            # Run AWS CLI SSO login
            result = subprocess.run([
                'aws', 'sso', 'login',
                '--profile', profile_name,
                '--config-file', temp_config_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'SSO login failed: {result.stderr}'
                }
            
            # Test the credentials
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            # Store session info
            self._profile_name = profile_name
            self._sso_config = {
                'sso_start_url': sso_start_url,
                'sso_region': sso_region,
                'account_id': account_id,
                'role_name': role_name
            }
            
            # Clean up temp file
            Path(temp_config_path).unlink()
            
            return {
                'success': True,
                'account_id': identity['Account'],
                'user_id': identity['UserId'],
                'arn': identity['Arn']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session(self) -> boto3.Session | None:
        """Get current boto3 session or None if not authenticated."""
        if not self._profile_name:
            return None
        
        try:
            session = boto3.Session(profile_name=self._profile_name)
            # Quick test to see if credentials are still valid
            sts = session.client('sts')
            sts.get_caller_identity()
            return session
        except Exception:
            # Credentials expired, clear session
            self._profile_name = None
            self._sso_config = None
            return None
    
    def get_status(self) -> dict[str, Any]:
        """Get authentication status."""
        if not self._profile_name or not self._sso_config:
            return {'authenticated': False}
        
        session = self.get_session()
        if not session:
            return {'authenticated': False, 'error': 'Session expired'}
        
        try:
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            return {
                'authenticated': True,
                'account_id': identity['Account'],
                'user_id': identity['UserId'],
                'arn': identity['Arn'],
                'sso_config': self._sso_config
            }
        except Exception as e:
            return {'authenticated': False, 'error': str(e)}
    
    def clear(self):
        """Clear current session."""
        self._profile_name = None
        self._credentials = None
        self._sso_config = None


# Global session instance
sso_session = SSOSession()