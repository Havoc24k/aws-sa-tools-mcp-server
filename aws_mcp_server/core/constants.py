"""Modern constants using StrEnum and Final types."""

from enum import StrEnum
from typing import Final


class AWSService(StrEnum):
    """AWS service names for client creation."""
    EC2 = "ec2"
    S3 = "s3"
    RDS = "rds"
    CLOUDWATCH = "cloudwatch"
    COST_EXPLORER = "ce"
    LAMBDA = "lambda"
    IAM = "iam"
    STS = "sts"


class DocumentationType(StrEnum):
    """Documentation string constants to eliminate repetition."""
    PROFILE_PARAM = "AWS profile name from ~/.aws/credentials"
    REGION_PARAM = "AWS region (e.g., 'us-east-1', 'eu-west-1')"
    REQUIRED_PARAMS = "Required Parameters:"
    OPTIONAL_PARAMS = "Optional Parameters:"
    COMMON_USE_CASES = "Common Use Cases:"


class ChunkDefaults:
    """Text processing defaults as Final constants."""
    CHUNK_SIZE: Final[int] = 1200
    OVERLAP_SIZE: Final[int] = 200
    MIN_CHUNK_RATIO: Final[float] = 0.5


class AWSDefaults:
    """AWS operation defaults."""
    MAX_RESULTS: Final[int] = 1000
    TIMEOUT_SECONDS: Final[int] = 30
    REGION: Final[str] = "us-east-1"
    PROFILE: Final[str] = "default"
