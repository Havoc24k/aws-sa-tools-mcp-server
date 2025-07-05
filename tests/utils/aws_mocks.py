"""AWS service mocking utilities for tests."""

import boto3
from moto import mock_aws
from typing import Dict, Any, List
from datetime import datetime, timezone


class AWSMockManager:
    """Manager for AWS service mocks."""

    def __init__(self):
        self.mocks = {}
        self.clients = {}

    def setup_ec2_mock(self, region: str = "us-east-1"):
        """Set up EC2 mock with sample data."""
        if "aws" not in self.mocks:
            mock = mock_aws()
            mock.start()
            self.mocks["aws"] = mock

        client = boto3.client("ec2", region_name=region)
        self.clients["ec2"] = client

        # Create sample VPC
        vpc_response = client.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]

        # Create sample security group
        sg_response = client.create_security_group(
            GroupName="test-sg", Description="Test security group", VpcId=vpc_id
        )
        sg_id = sg_response["GroupId"]

        # Create sample instances
        instances = client.run_instances(
            ImageId="ami-12345678",
            MinCount=2,
            MaxCount=2,
            InstanceType="t2.micro",
            KeyName="test-key",
            SecurityGroupIds=[sg_id],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": "test-instance-1"},
                        {"Key": "Environment", "Value": "testing"},
                    ],
                }
            ],
        )

        return {
            "vpc_id": vpc_id,
            "security_group_id": sg_id,
            "instance_ids": [i["InstanceId"] for i in instances["Instances"]],
        }

    def setup_s3_mock(self, region: str = "us-east-1"):
        """Set up S3 mock with sample data."""
        if "aws" not in self.mocks:
            mock = mock_aws()
            mock.start()
            self.mocks["aws"] = mock

        client = boto3.client("s3", region_name=region)
        self.clients["s3"] = client

        # Create sample buckets
        buckets = ["test-bucket-1", "test-bucket-2", "production-bucket"]
        for bucket in buckets:
            client.create_bucket(Bucket=bucket)

            # Add sample objects
            for i in range(3):
                client.put_object(
                    Bucket=bucket,
                    Key=f"test-file-{i}.txt",
                    Body=f"Content of test file {i} in {bucket}",
                )

        return {"buckets": buckets}

    def setup_rds_mock(self, region: str = "us-east-1"):
        """Set up RDS mock with sample data."""
        if "aws" not in self.mocks:
            mock = mock_aws()
            mock.start()
            self.mocks["aws"] = mock

        client = boto3.client("rds", region_name=region)
        self.clients["rds"] = client

        # Create sample DB instances
        db_instances = []
        for i, engine in enumerate(["mysql", "postgres"], 1):
            db_id = f"test-db-{engine}-{i}"
            client.create_db_instance(
                DBInstanceIdentifier=db_id,
                DBInstanceClass="db.t3.micro",
                Engine=engine,
                MasterUsername="admin",
                MasterUserPassword="password123",
                AllocatedStorage=20,
                Tags=[
                    {"Key": "Name", "Value": f"Test {engine.title()} DB"},
                    {"Key": "Environment", "Value": "testing"},
                ],
            )
            db_instances.append(db_id)

        return {"db_instances": db_instances}

    def setup_cloudwatch_mock(self, region: str = "us-east-1"):
        """Set up CloudWatch mock with sample data."""
        if "aws" not in self.mocks:
            mock = mock_aws()
            mock.start()
            self.mocks["aws"] = mock

        client = boto3.client("cloudwatch", region_name=region)
        self.clients["cloudwatch"] = client

        # Put sample metric data
        client.put_metric_data(
            Namespace="AWS/EC2",
            MetricData=[
                {
                    "MetricName": "CPUUtilization",
                    "Dimensions": [
                        {"Name": "InstanceId", "Value": "i-1234567890abcdef0"}
                    ],
                    "Value": 80.0,
                    "Unit": "Percent",
                    "Timestamp": datetime.now(timezone.utc),
                }
            ],
        )

        return {"metrics": ["CPUUtilization"]}

    def setup_cost_explorer_mock(self, region: str = "us-east-1"):
        """Set up Cost Explorer mock with sample data."""
        if "aws" not in self.mocks:
            mock = mock_aws()
            mock.start()
            self.mocks["aws"] = mock

        client = boto3.client("ce", region_name=region)
        self.clients["ce"] = client

        return {"service": "cost_explorer"}

    def setup_all_services(self, region: str = "us-east-1"):
        """Set up all AWS service mocks."""
        return {
            "ec2": self.setup_ec2_mock(region),
            "s3": self.setup_s3_mock(region),
            "rds": self.setup_rds_mock(region),
            "cloudwatch": self.setup_cloudwatch_mock(region),
            "cost_explorer": self.setup_cost_explorer_mock(region),
        }

    def cleanup(self):
        """Clean up all mocks."""
        for mock in self.mocks.values():
            mock.stop()
        self.mocks.clear()
        self.clients.clear()


def create_sample_aws_responses():
    """Create sample AWS API responses for testing."""
    return {
        "ec2_describe_instances": {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "ImageId": "ami-12345678",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "KeyName": "test-key",
                            "VpcId": "vpc-12345678",
                            "SubnetId": "subnet-12345678",
                            "Tags": [
                                {"Key": "Name", "Value": "test-instance"},
                                {"Key": "Environment", "Value": "testing"},
                            ],
                        }
                    ]
                }
            ]
        },
        "s3_list_buckets": {
            "Buckets": [
                {"Name": "test-bucket-1", "CreationDate": datetime(2024, 1, 1)},
                {"Name": "test-bucket-2", "CreationDate": datetime(2024, 1, 2)},
            ]
        },
        "rds_describe_db_instances": {
            "DBInstances": [
                {
                    "DBInstanceIdentifier": "test-db",
                    "DBInstanceClass": "db.t3.micro",
                    "Engine": "mysql",
                    "EngineVersion": "8.0.35",
                    "DBInstanceStatus": "available",
                }
            ]
        },
    }
