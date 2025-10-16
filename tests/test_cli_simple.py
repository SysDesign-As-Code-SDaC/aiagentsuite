"""
Simple CLI tests for AI Agent Suite.
"""

import pytest
import subprocess
import sys
from pathlib import Path
import tempfile


class TestCLISimple:
    """Simple CLI functionality tests."""
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "AI Agent Suite CLI" in result.stdout
    
    def test_cli_init_help(self):
        """Test CLI init help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "init", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Initialize" in result.stdout
    
    def test_cli_constitution_help(self):
        """Test CLI constitution help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "constitution", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "constitution" in result.stdout
    
    def test_cli_protocols_help(self):
        """Test CLI protocols help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "protocols", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "protocols" in result.stdout
    
    def test_cli_memory_help(self):
        """Test CLI memory help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "memory", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "memory" in result.stdout
    
    def test_cli_log_decision_help(self):
        """Test CLI log-decision help command."""
        result = subprocess.run([
            sys.executable, "-m", "aiagentsuite.cli.main", "log-decision", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "decision" in result.stdout
