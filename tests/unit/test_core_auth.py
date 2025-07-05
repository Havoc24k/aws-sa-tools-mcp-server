"""Unit tests for core authentication utilities."""

import pytest
from unittest.mock import Mock, patch
from aws_mcp_server.core.auth import (
    validate_aws_profile,
    list_available_profiles,
    get_default_region,
    validate_region
)


class TestValidateAWSProfile:
    """Test validate_aws_profile function."""
    
    @patch('boto3.Session')
    def test_valid_profile(self, mock_session):
        """Test validation of valid AWS profile."""
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {
            'UserId': 'test-user',
            'Account': '123456789012',
            'Arn': 'arn:aws:iam::123456789012:user/test-user'
        }
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_sts
        mock_session.return_value = mock_session_instance
        
        result = validate_aws_profile('test-profile')
        
        assert result is True
        mock_session.assert_called_once_with(profile_name='test-profile')
        mock_session_instance.client.assert_called_once_with('sts')
        mock_sts.get_caller_identity.assert_called_once()
    
    @patch('boto3.Session')
    def test_invalid_profile(self, mock_session):
        """Test validation of invalid AWS profile."""
        mock_session.side_effect = Exception('Profile not found')
        
        result = validate_aws_profile('invalid-profile')
        
        assert result is False
        mock_session.assert_called_once_with(profile_name='invalid-profile')
    
    @patch('boto3.Session')
    def test_profile_with_invalid_credentials(self, mock_session):
        """Test profile with invalid credentials."""
        mock_sts = Mock()
        mock_sts.get_caller_identity.side_effect = Exception('Invalid credentials')
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_sts
        mock_session.return_value = mock_session_instance
        
        result = validate_aws_profile('test-profile')
        
        assert result is False


class TestListAvailableProfiles:
    """Test list_available_profiles function."""
    
    @patch('boto3.Session')
    def test_list_profiles_success(self, mock_session):
        """Test successful listing of profiles."""
        expected_profiles = ['default', 'dev', 'prod', 'test']
        
        mock_session_instance = Mock()
        mock_session_instance.available_profiles = expected_profiles
        mock_session.return_value = mock_session_instance
        
        result = list_available_profiles()
        
        assert result == expected_profiles
        mock_session.assert_called_once()
    
    @patch('boto3.Session')
    def test_list_profiles_exception(self, mock_session):
        """Test listing profiles with exception."""
        mock_session.side_effect = Exception('Config error')
        
        result = list_available_profiles()
        
        assert result == []
        mock_session.assert_called_once()


class TestGetDefaultRegion:
    """Test get_default_region function."""
    
    @patch('boto3.Session')
    def test_get_region_with_profile(self, mock_session):
        """Test getting region with specific profile."""
        mock_session_instance = Mock()
        mock_session_instance.region_name = 'us-west-2'
        mock_session.return_value = mock_session_instance
        
        result = get_default_region('test-profile')
        
        assert result == 'us-west-2'
        mock_session.assert_called_once_with(profile_name='test-profile')
    
    @patch('boto3.Session')
    def test_get_region_default_profile(self, mock_session):
        """Test getting region with default profile."""
        mock_session_instance = Mock()
        mock_session_instance.region_name = 'us-east-1'
        mock_session.return_value = mock_session_instance
        
        result = get_default_region()
        
        assert result == 'us-east-1'
        mock_session.assert_called_once_with(profile_name=None)
    
    @patch('boto3.Session')
    def test_get_region_none(self, mock_session):
        """Test getting region when none configured."""
        mock_session_instance = Mock()
        mock_session_instance.region_name = None
        mock_session.return_value = mock_session_instance
        
        result = get_default_region('test-profile')
        
        assert result is None
    
    @patch('boto3.Session')
    def test_get_region_exception(self, mock_session):
        """Test getting region with exception."""
        mock_session.side_effect = Exception('Profile error')
        
        result = get_default_region('invalid-profile')
        
        assert result is None


class TestValidateRegion:
    """Test validate_region function."""
    
    def test_valid_us_regions(self):
        """Test valid US regions."""
        valid_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
        for region in valid_regions:
            assert validate_region(region) is True
    
    def test_valid_eu_regions(self):
        """Test valid EU regions."""
        valid_regions = ['eu-west-1', 'eu-west-2', 'eu-central-1', 'eu-north-1']
        for region in valid_regions:
            assert validate_region(region) is True
    
    def test_valid_ap_regions(self):
        """Test valid Asia Pacific regions."""
        valid_regions = ['ap-south-1', 'ap-southeast-1', 'ap-northeast-1']
        for region in valid_regions:
            assert validate_region(region) is True
    
    def test_valid_other_regions(self):
        """Test valid other regions."""
        valid_regions = ['sa-east-1', 'ca-central-1', 'me-south-1', 'af-south-1']
        for region in valid_regions:
            assert validate_region(region) is True
    
    def test_invalid_regions(self):
        """Test invalid regions."""
        invalid_regions = [
            'invalid-region',
            'us-invalid-1',
            'eu-fake-1',
            'ap-nonexistent-1',
            '',
            'us-east',  # Missing number
            'us-east-1a'  # Extra character
        ]
        for region in invalid_regions:
            assert validate_region(region) is False
    
    def test_case_sensitivity(self):
        """Test region validation is case sensitive."""
        assert validate_region('US-EAST-1') is False
        assert validate_region('Us-East-1') is False
        assert validate_region('us-east-1') is True