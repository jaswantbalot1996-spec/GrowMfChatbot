#!/usr/bin/env python3
"""
Phase 4 GitHub Actions Deployment Verification Script

Validates:
- GitHub Actions workflow syntax
- Required secrets configured
- Workflow triggers set correctly
- Initial test run
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class Phase4Verifier:
    """Verify Phase 4 GitHub Actions deployment."""
    
    def __init__(self):
        """Initialize verifier."""
        self.repo_path = Path.cwd()
        self.workflow_path = self.repo_path / ".github" / "workflows" / "phase-4-daily-scrape.yml"
        self.results = []
        self.status = "✅ PASS"
    
    def run(self):
        """Run all verification checks."""
        print("🚀 Phase 4 GitHub Actions Deployment Verification")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # Check 1: Workflow file exists
        self._check_workflow_exists()
        
        # Check 2: Workflow is valid YAML
        self._check_workflow_yaml()
        
        # Check 3: Required secrets
        self._check_required_secrets()
        
        # Check 4: Workflow triggers
        self._check_workflow_triggers()
        
        # Check 5: Required Python modules
        self._check_python_modules()
        
        # Check 6: API server running
        self._check_api_server()
        
        # Check 7: Redis connectivity
        self._check_redis()
        
        # Print summary
        self._print_summary()
    
    def _log_check(self, name: str, passed: bool, details: str = ""):
        """Log a check result."""
        icon = "✅" if passed else "❌"
        self.results.append((name, passed, details))
        print(f"{icon} {name}")
        if details:
            print(f"   {details}")
        if not passed:
            self.status = "❌ FAIL"
    
    def _check_workflow_exists(self):
        """Check if workflow file exists."""
        exists = self.workflow_path.exists()
        self._log_check(
            "Workflow file exists",
            exists,
            str(self.workflow_path) if exists else "File not found"
        )
    
    def _check_workflow_yaml(self):
        """Check if workflow YAML is valid."""
        try:
            import yaml
            with open(self.workflow_path, 'r') as f:
                yaml.safe_load(f)
            self._log_check("Workflow YAML valid", True)
        except ImportError:
            self._log_check("Workflow YAML check", False, "PyYAML not installed")
        except Exception as e:
            self._log_check("Workflow YAML valid", False, str(e))
    
    def _check_required_secrets(self):
        """Check if required GitHub secrets are configured."""
        required_secrets = [
            "CHROMA_DB_URL",
            "CHROMA_API_KEY",
            "GROK_API_KEY",
            "GOOGLE_TRANSLATE_API_KEY",
            "POSTGRES_URL",
            "REDIS_URL",
            "SLACK_WEBHOOK",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY"
        ]
        
        # Check locally in .env first
        env_file = self.repo_path / ".env"
        env_vars = {}
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        env_vars[key] = val
        
        missing = []
        for secret in required_secrets:
            if secret not in env_vars and not os.getenv(secret):
                missing.append(secret)
        
        passed = len(missing) == 0
        details = f"{len(required_secrets)} secrets configured"
        if missing:
            details += f" ({len(missing)} missing: {', '.join(missing[:3])}...)"
        
        self._log_check("Required secrets configured", passed, details)
    
    def _check_workflow_triggers(self):
        """Check if workflow has correct triggers."""
        try:
            import yaml
            with open(self.workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            triggers = workflow.get('on', {})
            has_schedule = 'schedule' in triggers
            has_dispatch = 'workflow_dispatch' in triggers
            
            passed = has_schedule and has_dispatch
            details = f"Schedule: {has_schedule}, Dispatch: {has_dispatch}"
            
            self._log_check("Workflow triggers configured", passed, details)
        except Exception as e:
            self._log_check("Workflow triggers check", False, str(e))
    
    def _check_python_modules(self):
        """Check if required Python modules are installed."""
        required_modules = [
            'redis',
            'requests',
            'streamlit',
            'flask',
            'google-cloud-translate',
            'pyyaml'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module.replace('-', '_'))
            except ImportError:
                missing.append(module)
        
        passed = len(missing) == 0
        details = f"{len(required_modules)} modules available"
        if missing:
            details += f" ({len(missing)} missing: {', '.join(missing[:2])}...)"
        
        self._log_check("Required Python modules", passed, details)
    
    def _check_api_server(self):
        """Check if Phase 4 API server is running."""
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=5)
            passed = response.status_code == 200
            
            self._log_check(
                "Phase 4 API server",
                passed,
                "Running on http://localhost:8000" if passed else "Not responding"
            )
        except Exception as e:
            self._log_check(
                "Phase 4 API server",
                False,
                "Start with: python phase_4_extended_coverage/api_server_phase4.py 8000"
            )
    
    def _check_redis(self):
        """Check Redis connectivity."""
        try:
            import redis
            r = redis.Redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                socket_connect_timeout=5
            )
            r.ping()
            self._log_check("Redis connectivity", True, "Connected")
        except Exception as e:
            self._log_check(
                "Redis connectivity",
                False,
                "Ensure Redis is running (fallback cache will be used)"
            )
    
    def _print_summary(self):
        """Print verification summary."""
        print()
        print("=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for _, passed, _ in self.results if passed)
        total_count = len(self.results)
        
        print(f"Status: {self.status}")
        print(f"Passed: {passed_count}/{total_count}")
        print()
        
        if passed_count == total_count:
            print("✅ All checks passed! Ready to deploy Phase 4.")
            print()
            print("Next steps:")
            print("1. Commit Phase 4 code: git add phase_4_extended_coverage/")
            print("2. Push to GitHub: git push origin main")
            print("3. Navigate to Actions tab → Phase 4 Daily Extended Coverage Scrape")
            print("4. Verify secrets in repository settings")
            print("5. Run workflow_dispatch to test manual trigger")
            print()
            print("Workflow will run daily at 9:00 AM IST automatically.")
        else:
            print("⚠️  Some checks failed. Please address the issues above.")
            print()
            print("Failed checks:")
            for name, passed, details in self.results:
                if not passed:
                    print(f"  • {name}")
                    if details:
                        print(f"    - {details}")


def main():
    """Run verification."""
    verifier = Phase4Verifier()
    verifier.run()
    
    # Exit with appropriate code
    sys.exit(0 if "PASS" in verifier.status else 1)


if __name__ == "__main__":
    main()
