# Import all AWS service modules to register MCP tools
from .services.billing import ce
from .services.compute import ec2
from .services.database import rds
from .services.generic import sdk_wrapper
from .services.monitoring import cloudwatch
from .services.storage import s3
