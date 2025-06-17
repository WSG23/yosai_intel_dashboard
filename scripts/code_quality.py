# tools/code_quality.py
"""
Code quality and standards enforcement system
Implements Apple's code quality standards and best practices
"""
import ast
import os
import subprocess
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging

class QualityLevel(Enum):
    """Code quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

class IssueType(Enum):
    """Types of code quality issues"""
    STYLE = "style"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

@dataclass
class QualityIssue:
    """Individual code quality issue"""
    file_path: str
    line_number: int
    issue_type: IssueType
    severity: str
    message: str
    rule: str
    suggestion: Optional[str] = None

@dataclass
class QualityReport:
    """Comprehensive quality report"""
    overall_score: float
    quality_level: QualityLevel
    total_files: int
    total_lines: int
    issues_by_type: Dict[IssueType, int]
    issues_by_severity: Dict[str, int]
    detailed_issues: List[QualityIssue]
    metrics: Dict[str, Any]
    recommendations: List[str]

class CodeQualityAnalyzer:
    """Comprehensive code quality analysis system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds (Apple-grade standards)
        self.thresholds = {
            'max_function_length': 30,
            'max_class_length': 200,
            'max_file_length': 500,
            'max_complexity': 8,
            'min_test_coverage': 80,
            'max_duplicate_lines': 5,
            'min_documentation_coverage': 70
        }
    
    def analyze_project(self) -> QualityReport:
        """Perform comprehensive project analysis"""
        
        self.logger.info("Starting comprehensive code quality analysis...")
        
        # Collect all Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        issues = []
        metrics = {
            'total_files': len(python_files),
            'total_lines': 0,
            'functions_analyzed': 0,
            'classes_analyzed': 0,
            'complexity_scores': [],
            'function_lengths': [],
            'class_lengths': []
        }
        
        # Analyze each file
        for file_path in python_files:
            file_issues, file_metrics = self._analyze_file(file_path)
            issues.extend(file_issues)
            
            metrics['total_lines'] += file_metrics.get('lines', 0)
            metrics['functions_analyzed'] += file_metrics.get('functions', 0)
            metrics['classes_analyzed'] += file_metrics.get('classes', 0)
            metrics['complexity_scores'].extend(file_metrics.get('complexity_scores', []))
            metrics['function_lengths'].extend(file_metrics.get('function_lengths', []))
            metrics['class_lengths'].extend(file_metrics.get('class_lengths', []))
        
        # Run external quality tools
        external_issues = self._run_external_tools()
        issues.extend(external_issues)
        
        # Calculate overall score and generate report
        return self._generate_report(issues, metrics)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped in analysis"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'env',
            '.pytest_cache',
            'node_modules',
            'migrations',
            'test_',
            'conftest.py'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze individual Python file"""
        
        issues = []
        metrics = {
            'lines': 0,
            'functions': 0,
            'classes': 0,
            'complexity_scores': [],
            'function_lengths': [],
            'class_lengths': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                metrics['lines'] = len(lines)
            
            # Parse AST for deeper analysis
            tree = ast.parse(content)
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                    func_issues, func_length = self._analyze_function(node, file_path)
                    issues.extend(func_issues)
                    metrics['function_lengths'].append(func_length)
                    
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                    class_issues, class_length = self._analyze_class(node, file_path)
                    issues.extend(class_issues)
                    metrics['class_lengths'].append(class_length)
            
            # File-level checks
            file_issues = self._analyze_file_structure(file_path, lines)
            issues.extend(file_issues)
            
        except Exception as e:
            self.logger.warning(f"Error analyzing {file_path}: {e}")
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type=IssueType.MAINTAINABILITY,
                severity="error",
                message=f"Failed to parse file: {e}",
                rule="parse_error"
            ))
        
        return issues, metrics
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> Tuple[List[QualityIssue], int]:
        """Analyze function for quality issues"""
        
        issues = []
        
        # Calculate function length
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            func_length = node.end_lineno - node.lineno + 1
        else:
            func_length = 1
        
        # Check function length
        if func_length > self.thresholds['max_function_length']:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.MAINTAINABILITY,
                severity="warning",
                message=f"Function '{node.name}' is too long ({func_length} lines)",
                rule="max_function_length",
                suggestion=f"Consider breaking into smaller functions (max: {self.thresholds['max_function_length']} lines)"
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.DOCUMENTATION,
                severity="info",
                message=f"Function '{node.name}' missing docstring",
                rule="missing_docstring",
                suggestion="Add descriptive docstring explaining function purpose and parameters"
            ))
        
        # Check function complexity (simplified cyclomatic complexity)
        complexity = self._calculate_complexity(node)
        if complexity > self.thresholds['max_complexity']:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.COMPLEXITY,
                severity="warning",
                message=f"Function '{node.name}' has high complexity ({complexity})",
                rule="max_complexity",
                suggestion="Consider simplifying logic or breaking into smaller functions"
            ))
        
        # Check for too many parameters
        if len(node.args.args) > 5:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.MAINTAINABILITY,
                severity="info",
                message=f"Function '{node.name}' has many parameters ({len(node.args.args)})",
                rule="too_many_parameters",
                suggestion="Consider using a configuration object or dataclass"
            ))
        
        return issues, func_length
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> Tuple[List[QualityIssue], int]:
        """Analyze class for quality issues"""
        
        issues = []
        
        # Calculate class length
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            class_length = node.end_lineno - node.lineno + 1
        else:
            class_length = 1
        
        # Check class length
        if class_length > self.thresholds['max_class_length']:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.MAINTAINABILITY,
                severity="warning",
                message=f"Class '{node.name}' is too long ({class_length} lines)",
                rule="max_class_length",
                suggestion=f"Consider breaking into smaller classes (max: {self.thresholds['max_class_length']} lines)"
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.DOCUMENTATION,
                severity="info",
                message=f"Class '{node.name}' missing docstring",
                rule="missing_docstring",
                suggestion="Add descriptive docstring explaining class purpose"
            ))
        
        # Count methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 15:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                issue_type=IssueType.MAINTAINABILITY,
                severity="warning",
                message=f"Class '{node.name}' has many methods ({len(methods)})",
                rule="too_many_methods",
                suggestion="Consider if class has too many responsibilities"
            ))
        
        return issues, class_length
    
    def _analyze_file_structure(self, file_path: Path, lines: List[str]) -> List[QualityIssue]:
        """Analyze file structure and organization"""
        
        issues = []
        
        # Check file length
        if len(lines) > self.thresholds['max_file_length']:
            issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type=IssueType.MAINTAINABILITY,
                severity="warning",
                message=f"File is too long ({len(lines)} lines)",
                rule="max_file_length",
                suggestion=f"Consider splitting into multiple files (max: {self.thresholds['max_file_length']} lines)"
            ))
        
        # Check for proper imports organization
        import_section_ended = False
        for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
            line = line.strip()
            
            if line.startswith('import ') or line.startswith('from '):
                if import_section_ended:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type=IssueType.STYLE,
                        severity="info",
                        message="Import statement after non-import code",
                        rule="import_organization",
                        suggestion="Place all imports at the top of the file"
                    ))
            elif line and not line.startswith('#') and not line.startswith('"""'):
                import_section_ended = True
        
        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(QualityIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type=IssueType.STYLE,
                    severity="info",
                    message="Trailing whitespace",
                    rule="trailing_whitespace",
                    suggestion="Remove trailing whitespace"
                ))
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(QualityIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type=IssueType.STYLE,
                    severity="info",
                    message=f"Line too long ({len(line)} characters)",
                    rule="line_length",
                    suggestion="Break long lines (max: 120 characters)"
                ))
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate simplified cyclomatic complexity"""
        
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        
        return complexity
    
    def _run_external_tools(self) -> List[QualityIssue]:
        """Run external code quality tools"""
        
        issues = []
        
        # Run flake8
        try:
            result = subprocess.run(
                ['flake8', '--format=json', '.'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                flake8_issues = self._parse_flake8_output(result.stdout)
                issues.extend(flake8_issues)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("Flake8 not available or timed out")
        
        # Run mypy
        try:
            result = subprocess.run(
                ['mypy', '.', '--json-report', '/tmp/mypy-report'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            mypy_issues = self._parse_mypy_output(result.stdout)
            issues.extend(mypy_issues)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("MyPy not available or timed out")
        
        return issues
    
    def _parse_flake8_output(self, output: str) -> List[QualityIssue]:
        """Parse flake8 JSON output"""
        issues = []
        
        try:
            # Flake8 doesn't output JSON by default, this is simplified
            lines = output.strip().split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 4:
                        file_path = parts[0]
                        line_num = int(parts[1]) if parts[1].isdigit() else 1
                        message = ':'.join(parts[3:]).strip()
                        
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=line_num,
                            issue_type=IssueType.STYLE,
                            severity="info",
                            message=message,
                            rule="flake8"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Error parsing flake8 output: {e}")
        
        return issues
    
    def _parse_mypy_output(self, output: str) -> List[QualityIssue]:
        """Parse mypy output"""
        issues = []
        
        try:
            lines = output.strip().split('\n')
            for line in lines:
                if ': error:' in line or ': warning:' in line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        file_path = parts[0]
                        line_num = int(parts[1]) if parts[1].isdigit() else 1
                        severity = "error" if "error" in line else "warning"
                        message = ':'.join(parts[2:]).strip()
                        
                        issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=line_num,
                            issue_type=IssueType.MAINTAINABILITY,
                            severity=severity,
                            message=message,
                            rule="mypy"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Error parsing mypy output: {e}")
        
        return issues
    
    def _generate_report(self, issues: List[QualityIssue], metrics: Dict[str, Any]) -> QualityReport:
        """Generate comprehensive quality report"""
        
        # Count issues by type and severity
        issues_by_type = {}
        issues_by_severity = {}
        
        for issue_type in IssueType:
            issues_by_type[issue_type] = len([i for i in issues if i.issue_type == issue_type])
        
        for severity in ['error', 'warning', 'info']:
            issues_by_severity[severity] = len([i for i in issues if i.severity == severity])
        
        # Calculate overall score (0-100)
        score = self._calculate_quality_score(issues, metrics)
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.NEEDS_IMPROVEMENT
        else:
            quality_level = QualityLevel.POOR
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics, quality_level)
        
        return QualityReport(
            overall_score=score,
            quality_level=quality_level,
            total_files=metrics['total_files'],
            total_lines=metrics['total_lines'],
            issues_by_type=issues_by_type,
            issues_by_severity=issues_by_severity,
            detailed_issues=issues,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def _calculate_quality_score(self, issues: List[QualityIssue], metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        
        base_score = 100.0
        
        # Deduct points for issues
        error_weight = 10
        warning_weight = 5
        info_weight = 1
        
        for issue in issues:
            if issue.severity == 'error':
                base_score -= error_weight
            elif issue.severity == 'warning':
                base_score -= warning_weight
            else:
                base_score -= info_weight
        
        # Bonus for good practices
        if metrics['total_files'] > 0:
            # Bonus for good average function length
            if metrics['function_lengths']:
                avg_func_length = sum(metrics['function_lengths']) / len(metrics['function_lengths'])
                if avg_func_length <= self.thresholds['max_function_length'] * 0.7:
                    base_score += 5
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(
        self, 
        issues: List[QualityIssue], 
        metrics: Dict[str, Any], 
        quality_level: QualityLevel
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # High-priority recommendations based on issues
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        
        if error_count > 0:
            recommendations.append(f"🚨 Fix {error_count} critical errors immediately")
        
        if warning_count > 5:
            recommendations.append(f"⚠️ Address {warning_count} warnings to improve code quality")
        
        # Specific recommendations based on issue types
        complexity_issues = [i for i in issues if i.issue_type == IssueType.COMPLEXITY]
        if len(complexity_issues) > 3:
            recommendations.append("🔄 Refactor complex functions to improve maintainability")
        
        doc_issues = [i for i in issues if i.issue_type == IssueType.DOCUMENTATION]
        if len(doc_issues) > 5:
            recommendations.append("📚 Add missing documentation and docstrings")
        
        style_issues = [i for i in issues if i.issue_type == IssueType.STYLE]
        if len(style_issues) > 10:
            recommendations.append("💅 Run code formatter (black) to fix style issues")
        
        # General recommendations based on quality level
        if quality_level == QualityLevel.POOR:
            recommendations.extend([
                "🏗️ Consider major refactoring to improve code structure",
                "🧪 Implement comprehensive testing strategy",
                "📖 Establish coding standards and guidelines"
            ])
        elif quality_level == QualityLevel.NEEDS_IMPROVEMENT:
            recommendations.extend([
                "🔧 Focus on reducing technical debt",
                "📊 Implement code metrics monitoring",
                "👥 Consider code review process improvements"
            ])
        elif quality_level == QualityLevel.GOOD:
            recommendations.extend([
                "✨ Fine-tune performance optimizations",
                "🔍 Add more comprehensive testing",
                "📈 Monitor and maintain current quality level"
            ])
        else:  # EXCELLENT
            recommendations.extend([
                "🎯 Excellent code quality! Keep up the good work",
                "🚀 Consider sharing best practices with other teams",
                "🔬 Explore advanced optimization opportunities"
            ])
        
        return recommendations
    
    def export_report(self, report: QualityReport, format: str = 'json') -> str:
        """Export quality report in various formats"""
        
        if format == 'json':
            import json
            
            # Convert dataclasses to dicts
            report_dict = {
                'overall_score': report.overall_score,
                'quality_level': report.quality_level.value,
                'total_files': report.total_files,
                'total_lines': report.total_lines,
                'issues_by_type': {k.value: v for k, v in report.issues_by_type.items()},
                'issues_by_severity': report.issues_by_severity,
                'detailed_issues': [
                    {
                        'file_path': issue.file_path,
                        'line_number': issue.line_number,
                        'issue_type': issue.issue_type.value,
                        'severity': issue.severity,
                        'message': issue.message,
                        'rule': issue.rule,
                        'suggestion': issue.suggestion
                    }
                    for issue in report.detailed_issues
                ],
                'metrics': report.metrics,
                'recommendations': report.recommendations
            }
            
            return json.dumps(report_dict, indent=2)
        
        elif format == 'markdown':
            return self._generate_markdown_report(report)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _generate_markdown_report(self, report: QualityReport) -> str:
        """Generate markdown quality report"""
        
        md = f"""# Code Quality Report

## Overview
- **Overall Score**: {report.overall_score:.1f}/100
- **Quality Level**: {report.quality_level.value.title()}
- **Total Files**: {report.total_files}
- **Total Lines**: {report.total_lines}

## Issues Summary

### By Severity
"""
        
        for severity, count in report.issues_by_severity.items():
            md += f"- **{severity.title()}**: {count}\n"
        
        md += "\n### By Type\n"
        for issue_type, count in report.issues_by_type.items():
            if count > 0:
                md += f"- **{issue_type.value.title()}**: {count}\n"
        
        md += "\n## Recommendations\n"
        for rec in report.recommendations:
            md += f"- {rec}\n"
        
        md += (
            f"\n## Metrics\n"
            f"- **Functions Analyzed**: {report.metrics.get('functions_analyzed', 0)}\n"
            f"- **Classes Analyzed**: {report.metrics.get('classes_analyzed', 0)}\n"
        )
        
        if report.metrics.get('function_lengths'):
            avg_func_length = sum(report.metrics['function_lengths']) / len(report.metrics['function_lengths'])
            md += f"- **Average Function Length**: {avg_func_length:.1f} lines\n"
        
        return md

# Command line interface
def main():
    """Command line interface for code quality analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze code quality')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown', help='Output format')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = CodeQualityAnalyzer(args.project_root)
    report = analyzer.analyze_project()
    
    # Export report
    output = analyzer.export_report(report, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Quality report exported to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()