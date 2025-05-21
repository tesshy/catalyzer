"""Test for MotherDuck integration."""

import os
import pytest
from unittest.mock import patch
import duckdb

from cabinet.database import get_db_connection


@pytest.mark.parametrize(
    "token_available,expected_connection",
    [
        (True, "md:default"),  # With token, should connect to MotherDuck
        (False, None)   # Without token, should connect to local file
    ],
)
def test_motherduck_connection(token_available, expected_connection):
    """Test that database connection uses MotherDuck when token is available."""
    
    # Mock the environment variable and duckdb.connect
    environ_mock = {"MOTHERDUCK_TOKEN": "fake-token"} if token_available else {}
    
    with patch.dict(os.environ, environ_mock, clear=True), \
         patch('duckdb.connect') as mock_connect:
        
        # Setup a dummy connection to be returned by the mock
        mock_conn = type('MockConnection', (), {
            'execute': lambda self, query, *args: None,
            'close': lambda self: None
        })()
        mock_connect.return_value = mock_conn
        
        # Get the connection
        connection = next(get_db_connection())
        
        # Check how duckdb.connect was called
        if expected_connection:
            mock_connect.assert_called_with(expected_connection)
        else:
            # If no token, it should connect to a local file
            args = mock_connect.call_args[0][0]
            assert "cabinet.duckdb" in args