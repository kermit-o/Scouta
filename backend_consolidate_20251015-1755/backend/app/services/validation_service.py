import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import re
from typing import Dict, List, Tuple
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Usar import absoluto
from backend.app.utils.config import Config

logger = logging.getLogger(__name__)

class InputValidationService:
    def __init__(self):
        self.malicious_patterns = [
            r"(?i)(drop\s+table|delete\s+from|insert\s+into|update\s+set|union\s+select)",
            r"(?i)(exec\(|system\(|passthru\(|shell_exec\()",
            r"(?i)(<script|javascript:|onload=|onerror=)",
            r"(?i)(base64_decode|eval\(|assert\()",
            r"(?i)(\.\./|\.\.\\|/etc/passwd|/etc/shadow)",
            r"(?i)(localhost|127\.0\.0\.1|0\.0\.0\.0)"
        ]
        
        self.complexity_thresholds = {
            "low": 500,
            "medium": 2000,
            "high": 5000
        }

    def validate_requirements(self, requirements: str) -> Dict:
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "complexity": "low",
            "estimated_timeline": "1-2 weeks"
        }

        if not requirements or len(requirements.strip()) < 10:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Requirements are too short or empty")
            return validation_result

        if len(requirements) > 10000:
            validation_result["warnings"].append("Requirements are very long, consider simplifying")
            validation_result["complexity"] = "very_high"

        security_issues = self._check_security(requirements)
        if security_issues:
            validation_result["is_valid"] = False
            validation_result["errors"].extend(security_issues)

        complexity = self._estimate_complexity(requirements)
        validation_result["complexity"] = complexity
        validation_result["estimated_timeline"] = self._estimate_timeline(complexity)

        ambiguous_terms = self._check_ambiguity(requirements)
        if ambiguous_terms:
            validation_result["warnings"].extend(ambiguous_terms)

        return validation_result

    def _check_security(self, text: str) -> List[str]:
        issues = []
        for pattern in self.malicious_patterns:
            if re.search(pattern, text):
                issues.append(f"Potential security issue detected: {pattern}")
        return issues

    def _estimate_complexity(self, requirements: str) -> str:
        length = len(requirements)
        if length < self.complexity_thresholds["low"]:
            return "low"
        elif length < self.complexity_thresholds["medium"]:
            return "medium"
        elif length < self.complexity_thresholds["high"]:
            return "high"
        else:
            return "very_high"

    def _estimate_timeline(self, complexity: str) -> str:
        timelines = {
            "low": "1-2 weeks",
            "medium": "2-4 weeks",
            "high": "1-2 months",
            "very_high": "3+ months"
        }
        return timelines.get(complexity, "2-4 weeks")

    def _check_ambiguity(self, text: str) -> List[str]:
        ambiguous_terms = [
            "maybe", "possibly", "perhaps", "should", "could",
            "might", "approximately", "around", "some", "several"
        ]
        found_terms = []
        for term in ambiguous_terms:
            if term.lower() in text.lower():
                found_terms.append(f"Ambiguous term: '{term}'")
        return found_terms

# Global instance
validation_service = InputValidationService()
from backend.app.config.paths import setup_paths; setup_paths()
