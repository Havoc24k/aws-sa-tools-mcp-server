"""AWS SSO authentication tools for MCP server."""

from aws_mcp_server.core.sso_auth import sso_session
from aws_mcp_server.mcp import mcp


@mcp.tool(
    name="aws_sso_login",
    description="Authenticate with AWS SSO using your organization's credentials"
)
async def aws_sso_login(
    sso_start_url: str,
    sso_region: str,
    account_id: str,
    role_name: str
) -> dict:
    """Authenticate with AWS SSO.
    
    Args:
        sso_start_url: Your organization's SSO start URL (e.g., https://mycompany.awsapps.com/start)
        sso_region: AWS region for SSO (e.g., us-east-1)
        account_id: AWS account ID to access
        role_name: IAM role name to assume (e.g., PowerUserAccess)
    
    Returns:
        Authentication result with success status and user info
    """
    result = sso_session.authenticate(
        sso_start_url=sso_start_url,
        sso_region=sso_region,
        account_id=account_id,
        role_name=role_name
    )
    
    if result['success']:
        return {
            'message': 'Successfully authenticated with AWS SSO',
            'account_id': result['account_id'],
            'user_arn': result['arn'],
            'status': 'authenticated'
        }
    else:
        return {
            'message': 'Authentication failed',
            'error': result['error'],
            'status': 'failed'
        }


@mcp.tool(
    name="aws_sso_status",
    description="Check current AWS SSO authentication status"
)
async def aws_sso_status() -> dict:
    """Check current SSO authentication status.
    
    Returns:
        Current authentication status and user info
    """
    status = sso_session.get_status()
    
    if status['authenticated']:
        return {
            'message': 'Authenticated with AWS SSO',
            'account_id': status['account_id'],
            'user_arn': status['arn'],
            'sso_start_url': status['sso_config']['sso_start_url'],
            'status': 'authenticated'
        }
    else:
        return {
            'message': 'Not authenticated with AWS SSO',
            'error': status.get('error', 'No active session'),
            'status': 'unauthenticated'
        }


@mcp.tool(
    name="aws_sso_logout",
    description="Clear current AWS SSO session"
)
async def aws_sso_logout() -> dict:
    """Clear current SSO session.
    
    Returns:
        Logout confirmation
    """
    sso_session.clear()
    return {
        'message': 'SSO session cleared',
        'status': 'logged_out'
    }