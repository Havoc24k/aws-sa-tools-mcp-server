# Import all AWS service modules to register MCP tools
from .services.billing import ce
from .services.monitoring import cloudwatch
from .services.compute import ec2
from .services.database import rds
from .services.storage import s3
from .services.generic import sdk_wrapper
