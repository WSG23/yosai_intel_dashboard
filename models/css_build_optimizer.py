# css_quality_assurance.py
"""
Comprehensive CSS Quality Assurance & Performance Testing Suite
for Yōsai Intel Dashboard
"""

import os
import re
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import requests
import cssutils
import logging

# Configure CSS utils logging
cssutils.log.setLevel(logging.ERROR)

@dataclass
class CSSMetric:
    """CSS performance and quality metric"""
    name: str
    value: float
    unit: str
    status: str
    threshold: float
    description: str

@dataclass
class ComponentTest:
    """Component isolation test result"""
    component: str
    passes: List[str]
    failures: List[str]
    warnings: List[str]
    score: float

class CSSQualityAnalyzer:
    """Analyzes CSS for quality, performance, and best practices"""
    
    def __init__(self, css_dir: Path):
        self.css_dir = css_dir
        self.metrics = []
        self.violations = []
        self.components = []
        
    def analyze_bundle_size(self) -> CSSMetric:
        """Analyze CSS bundle size and compression"""
        main_css = self.css_dir / "main.css"
        
        if not main_css.exists():
            return CSSMetric("bundle_size", 0, "KB", "error", 100, "Main CSS file not found")
        
        # Calculate total size including imports
        total_size = 0
        processed_files = set()
        
        def calculate_size(css_file: Path):
            nonlocal total_size, processed_files
            
            if css_file in processed_files:
                return
            processed_files.add(css_file)
            
            if css_file.exists():
                content = css_file.read_text()
                total_size += len(content.encode('utf-8'))
                
                # Find @import statements
                imports = re.findall(r"@import\s+['\"]([^'\"]+)['\"]", content)
                for import_path in imports:
                    import_file = css_file.parent / import_path
                    if import_file.exists():
                        calculate_size(import_file)
        
        calculate_size(main_css)
        size_kb = total_size / 1024
        
        # Determine status
        if size_kb <= 50:
            status = "excellent"
        elif size_kb <= 100:
            status = "good"
        elif size_kb <= 200:
            status = "warning"
        else:
            status = "critical"
        
        return CSSMetric(
            "bundle_size", 
            round(size_kb, 2), 
            "KB", 
            status, 
            100, 
            f"Total CSS bundle size including all imports"
        )
    
    def analyze_design_token_usage(self) -> CSSMetric:
        """Analyze design token usage vs hardcoded values"""
        hardcoded_patterns = [
            r'color:\s*#[0-9a-fA-F]{6}',
            r'background:\s*#[0-9a-fA-F]{6}',
            r'border-color:\s*#[0-9a-fA-F]{6}',
            r'padding:\s*\d+px',
            r'margin:\s*\d+px',
            r'border-radius:\s*\d+px',
            r'font-size:\s*\d+px'
        ]
        
        total_values = 0
        hardcoded_values = 0
        
        for css_file in self.css_dir.rglob("*.css"):
            if css_file.name.startswith('_') or css_file.name == 'main.css':
                continue
                
            content = css_file.read_text()
            
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content)
                hardcoded_values += len(matches)
            
            # Count var() usage
            var_usage = len(re.findall(r'var\(--[^)]+\)', content))
            total_values += var_usage + hardcoded_values
        
        if total_values > 0:
            token_usage_percent = ((total_values - hardcoded_values) / total_values) * 100
        else:
            token_usage_percent = 100
        
        if token_usage_percent >= 95:
            status = "excellent"
        elif token_usage_percent >= 85:
            status = "good"
        elif token_usage_percent >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return CSSMetric(
            "design_token_usage",
            round(token_usage_percent, 1),
            "%",
            status,
            90,
            f"Percentage of values using design tokens vs hardcoded values"
        )
    
    def analyze_selector_specificity(self) -> CSSMetric:
        """Analyze CSS selector specificity for maintainability"""
        high_specificity_selectors = []
        total_selectors = 0
        
        for css_file in self.css_dir.rglob("*.css"):
            content = css_file.read_text()
            
            # Parse CSS
            try:
                sheet = cssutils.parseString(content)
                for rule in sheet:
                    if rule.type == rule.STYLE_RULE:
                        total_selectors += 1
                        selector_text = rule.selectorText
                        
                        # Calculate specificity (simplified)
                        id_count = selector_text.count('#')
                        class_count = selector_text.count('.')
                        element_count = len(re.findall(r'\b[a-z]+\b', selector_text.lower()))
                        
                        specificity = (id_count * 100) + (class_count * 10) + element_count
                        
                        if specificity > 30:  # High specificity threshold
                            high_specificity_selectors.append((selector_text, specificity))
            except:
                continue
        
        if total_selectors > 0:
            high_specificity_percent = (len(high_specificity_selectors) / total_selectors) * 100
        else:
            high_specificity_percent = 0
        
        if high_specificity_percent <= 5:
            status = "excellent"
        elif high_specificity_percent <= 10:
            status = "good"
        elif high_specificity_percent <= 20:
            status = "warning"
        else:
            status = "critical"
        
        return CSSMetric(
            "selector_specificity",
            round(100 - high_specificity_percent, 1),
            "%",
            status,
            90,
            f"Percentage of selectors with healthy specificity (< 30)"
        )
    
    def analyze_component_isolation(self) -> List[ComponentTest]:
        """Test component isolation and independence"""
        component_tests = []
        components_dir = self.css_dir / "03-components"
        
        if not components_dir.exists():
            return component_tests
        
        for component_file in components_dir.glob("_*.css"):
            component_name = component_file.stem[1:]  # Remove underscore
            passes = []
            failures = []
            warnings = []
            
            content = component_file.read_text()
            
            # Test 1: No hardcoded values
            hardcoded_patterns = [
                r'color:\s*#[0-9a-fA-F]{6}',
                r'padding:\s*\d+px',
                r'margin:\s*\d+px'
            ]
            
            has_hardcoded = False
            for pattern in hardcoded_patterns:
                if re.search(pattern, content):
                    has_hardcoded = True
                    break
            
            if not has_hardcoded:
                passes.append("No hardcoded values found")
            else:
                failures.append("Contains hardcoded values")
            
            # Test 2: Proper BEM naming
            selectors = re.findall(r'\.([a-zA-Z0-9_-]+)', content)
            bem_compliant = 0
            total_selectors = len(selectors)
            
            for selector in selectors:
                if (selector.startswith(component_name) or 
                    '--' in selector or '__' in selector):
                    bem_compliant += 1
            
            if total_selectors > 0:
                bem_percent = (bem_compliant / total_selectors) * 100
                if bem_percent >= 90:
                    passes.append("BEM naming convention followed")
                elif bem_percent >= 70:
                    warnings.append("Some selectors don't follow BEM")
                else:
                    failures.append("Poor BEM naming convention compliance")
            
            # Test 3: No cross-component dependencies
            cross_deps = []
            other_components = [f.stem[1:] for f in components_dir.glob("_*.css") if f != component_file]
            
            for other_comp in other_components:
                if re.search(rf'\.{other_comp}(?:\s|{{)', content):
                    cross_deps.append(other_comp)
            
            if not cross_deps:
                passes.append("No cross-component dependencies")
            else:
                failures.append(f"Dependencies on: {', '.join(cross_deps)}")
            
            # Test 4: Mobile-first responsive design
            media_queries = re.findall(r'@media[^{]+', content)
            mobile_first = True
            
            for query in media_queries:
                if 'max-width' in query:
                    mobile_first = False
                    break
            
            if media_queries:
                if mobile_first:
                    passes.append("Mobile-first responsive design")
                else:
                    warnings.append("Not fully mobile-first (uses max-width)")
            
            # Calculate score
            total_tests = len(passes) + len(failures) + len(warnings)
            if total_tests > 0:
                score = (len(passes) + (len(warnings) * 0.5)) / total_tests * 100
            else:
                score = 0
            
            component_tests.append(ComponentTest(
                component=component_name,
                passes=passes,
                failures=failures,
                warnings=warnings,
                score=round(score, 1)
            ))
        
        return component_tests
    
    def check_accessibility_compliance(self) -> CSSMetric:
        """Check CSS for accessibility compliance"""
        accessibility_score = 100
        violations = []
        
        for css_file in self.css_dir.rglob("*.css"):
            content = css_file.read_text()
            
            # Check for focus styles
            if not re.search(r':focus', content) and 'button' in content.lower():
                violations.append(f"{css_file.name}: Missing focus styles")
                accessibility_score -= 10
            
            # Check for proper contrast (simplified check)
            if re.search(r'color:\s*#(?:808080|888888|999999)', content):
                violations.append(f"{css_file.name}: Potentially low contrast colors")
                accessibility_score -= 5
            
            # Check for reduced motion support
            if '@media' in content and 'prefers-reduced-motion' not in content:
                violations.append(f"{css_file.name}: No reduced motion support")
                accessibility_score -= 5
        
        accessibility_score = max(0, accessibility_score)
        
        if accessibility_score >= 95:
            status = "excellent"
        elif accessibility_score >= 85:
            status = "good"
        elif accessibility_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return CSSMetric(
            "accessibility_compliance",
            accessibility_score,
            "%",
            status,
            90,
            f"CSS accessibility compliance score"
        )
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete CSS quality analysis"""
        print("🔍 Running comprehensive CSS quality analysis...")
        
        # Run all metric analyses
        metrics = [
            self.analyze_bundle_size(),
            self.analyze_design_token_usage(),
            self.analyze_selector_specificity(),
            self.check_accessibility_compliance()
        ]
        
        # Run component tests
        component_tests = self.analyze_component_isolation()
        
        # Calculate overall score
        metric_scores = [m.value for m in metrics if m.status != "error"]
        overall_score = sum(metric_scores) / len(metric_scores) if metric_scores else 0
        
        return {
            "overall_score": round(overall_score, 1),
            "metrics": metrics,
            "component_tests": component_tests,
            "timestamp": time.time()
        }

class CSSPerformanceTester:
    """Tests CSS performance and optimization"""
    
    def __init__(self, css_dir: Path, app_url: str = "http://localhost:8050"):
        self.css_dir = css_dir
        self.app_url = app_url
    
    def test_critical_css_path(self) -> Dict[str, Any]:
        """Test critical CSS loading performance"""
        try:
            import selenium
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            start_time = time.time()
            driver.get(self.app_url)
            
            # Wait for CSS to load
            driver.implicitly_wait(5)
            
            # Measure time to first contentful paint (simplified)
            load_time = time.time() - start_time
            
            # Check if critical CSS is inline or loaded quickly
            stylesheets = driver.find_elements("css selector", "link[rel='stylesheet']")
            css_load_time = load_time
            
            driver.quit()
            
            return {
                "page_load_time": round(load_time, 2),
                "css_load_time": round(css_load_time, 2),
                "external_stylesheets": len(stylesheets),
                "status": "good" if load_time < 2.0 else "warning" if load_time < 4.0 else "critical"
            }
            
        except ImportError:
            return {"error": "Selenium not installed for performance testing"}
        except Exception as e:
            return {"error": f"Performance test failed: {str(e)}"}
    
    def analyze_unused_css(self) -> Dict[str, Any]:
        """Analyze unused CSS selectors"""
        try:
            # This would require actual DOM analysis
            # For now, provide a simplified analysis
            
            all_selectors = set()
            for css_file in self.css_dir.rglob("*.css"):
                content = css_file.read_text()
                selectors = re.findall(r'\.([a-zA-Z0-9_-]+)', content)
                all_selectors.update(selectors)
            
            # Simplified unused CSS detection
            # In a real scenario, you'd compare against actual HTML usage
            potentially_unused = [s for s in all_selectors if s.startswith('unused-')]
            
            usage_percent = ((len(all_selectors) - len(potentially_unused)) / len(all_selectors)) * 100 if all_selectors else 100
            
            return {
                "total_selectors": len(all_selectors),
                "potentially_unused": len(potentially_unused),
                "usage_percent": round(usage_percent, 1),
                "status": "good" if usage_percent >= 85 else "warning" if usage_percent >= 70 else "critical"
            }
            
        except Exception as e:
            return {"error": f"Unused CSS analysis failed: {str(e)}"}

class CSSComponentTester:
    """Tests individual CSS components in isolation"""
    
    def __init__(self, css_dir: Path):
        self.css_dir = css_dir
        self.test_results = {}
    
    def generate_component_test_page(self, component_name: str) -> str:
        """Generate HTML test page for a specific component"""
        
        component_file = self.css_dir / "03-components" / f"_{component_name}.css"
        if not component_file.exists():
            return ""
        
        # Extract component classes from CSS
        content = component_file.read_text()
        classes = re.findall(r'\.([a-zA-Z0-9_-]+)', content)
        base_class = component_name
        variant_classes = [c for c in classes if c.startswith(f"{component_name}--")]
        size_classes = [c for c in classes if any(size in c for size in ['sm', 'md', 'lg', 'xl'])]
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name.title()} Component Test</title>
    <link rel="stylesheet" href="../css/main.css">
    <style>
        body {{
            padding: 2rem;
            background: var(--surface-app);
            color: var(--text-primary);
            font-family: var(--font-family-system);
        }}
        .test-section {{
            margin-bottom: 3rem;
            padding: 2rem;
            background: var(--surface-primary);
            border-radius: var(--radius-lg);
            border: 1px solid var(--color-gray-700);
        }}
        .test-title {{
            font-size: var(--text-xl);
            font-weight: var(--font-weight-bold);
            margin-bottom: 1rem;
            color: var(--color-accent);
        }}
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .component-example {{
            padding: 1rem;
            background: var(--surface-secondary);
            border-radius: var(--radius-md);
            border: 1px solid var(--color-gray-600);
        }}
        .example-label {{
            font-size: var(--text-sm);
            color: var(--text-tertiary);
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <h1>{component_name.title()} Component Test Page</h1>
    <p>Testing component isolation and variants</p>
    
    <div class="test-section">
        <h2 class="test-title">Base Component</h2>
        <div class="component-example">
            <div class="example-label">Base {component_name}</div>
            <div class="{base_class}">Base {component_name} example</div>
        </div>
    </div>
    
    {"".join([f'''
    <div class="test-section">
        <h2 class="test-title">Variant: {variant}</h2>
        <div class="component-example">
            <div class="example-label">{variant}</div>
            <div class="{base_class} {variant}">{variant} example</div>
        </div>
    </div>
    ''' for variant in variant_classes[:5]])}
    
    {"".join([f'''
    <div class="test-section">
        <h2 class="test-title">Size: {size}</h2>
        <div class="component-example">
            <div class="example-label">{size}</div>
            <div class="{base_class} {size}">{size} example</div>
        </div>
    </div>
    ''' for size in size_classes[:4]])}
    
    <div class="test-section">
        <h2 class="test-title">Combined Variants</h2>
        <div class="component-grid">
            {" ".join([f'''
            <div class="component-example">
                <div class="example-label">{base_class} {variant} {size_classes[0] if size_classes else ""}</div>
                <div class="{base_class} {variant} {size_classes[0] if size_classes else ""}">{variant} + size</div>
            </div>
            ''' for variant in variant_classes[:3]])}
        </div>
    </div>
    
    <div class="test-section">
        <h2 class="test-title">Responsive Test</h2>
        <p>Resize the window to test responsive behavior</p>
        <div class="component-example">
            <div class="{base_class} {variant_classes[0] if variant_classes else ''}">Responsive component test</div>
        </div>
    </div>
    
    <div class="test-section">
        <h2 class="test-title">Accessibility Test</h2>
        <div class="component-example">
            <div class="example-label">Tab through these elements to test focus states</div>
            <button class="{base_class}">Focusable {component_name}</button>
            <a href="#" class="{base_class}">Link {component_name}</a>
        </div>
    </div>
</body>
</html>"""
        
        return html_template
    
    def create_all_component_tests(self) -> Dict[str, str]:
        """Create test pages for all components"""
        test_pages = {}
        components_dir = self.css_dir / "03-components"
        
        if not components_dir.exists():
            return test_pages
        
        # Create test directory
        test_dir = self.css_dir.parent / "test-components"
        test_dir.mkdir(exist_ok=True)
        
        for component_file in components_dir.glob("_*.css"):
            component_name = component_file.stem[1:]  # Remove underscore
            html_content = self.generate_component_test_page(component_name)
            
            if html_content:
                test_file = test_dir / f"{component_name}-test.html"
                test_file.write_text(html_content)
                test_pages[component_name] = str(test_file)
                print(f"✅ Created test page: {test_file}")
        
        # Create index page
        index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Test Suite</title>
    <link rel="stylesheet" href="../css/main.css">
</head>
<body style="padding: 2rem; background: var(--surface-app); color: var(--text-primary);">
    <h1>Yōsai Intel Component Test Suite</h1>
    <p>Click on any component to test its isolation and variants:</p>
    <ul>
        {"".join([f'<li><a href="{name}-test.html">{name.title()} Component</a></li>' for name in test_pages.keys()])}
    </ul>
</body>
</html>"""
        
        index_file = test_dir / "index.html"
        index_file.write_text(index_content)
        print(f"✅ Created test suite index: {index_file}")
        
        return test_pages

def generate_css_report(css_dir: Path, output_file: Path = None) -> Dict[str, Any]:
    """Generate comprehensive CSS quality report"""
    
    print("📊 Generating comprehensive CSS quality report...")
    
    # Initialize analyzers
    quality_analyzer = CSSQualityAnalyzer(css_dir)
    performance_tester = CSSPerformanceTester(css_dir)
    component_tester = CSSComponentTester(css_dir)
    
    # Run analyses
    quality_results = quality_analyzer.run_full_analysis()
    performance_results = performance_tester.test_critical_css_path()
    unused_css_results = performance_tester.analyze_unused_css()
    
    # Generate component tests
    component_test_pages = component_tester.create_all_component_tests()
    
    # Compile report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": quality_results["overall_score"],
        "quality_metrics": [
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "status": m.status,
                "threshold": m.threshold,
                "description": m.description
            } for m in quality_results["metrics"]
        ],
        "component_tests": [
            {
                "component": ct.component,
                "score": ct.score,
                "passes": ct.passes,
                "failures": ct.failures,
                "warnings": ct.warnings
            } for ct in quality_results["component_tests"]
        ],
        "performance": {
            "critical_css": performance_results,
            "unused_css": unused_css_results
        },
        "test_pages": component_test_pages,
        "recommendations": generate_recommendations(quality_results, performance_results)
    }
    
    # Save report
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📋 Report saved to: {output_file}")
    
    return report

def generate_recommendations(quality_results: Dict, performance_results: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    # Check bundle size
    bundle_metric = next((m for m in quality_results["metrics"] if m.name == "bundle_size"), None)
    if bundle_metric and bundle_metric.value > 100:
        recommendations.append("Consider splitting CSS into critical and non-critical parts for better loading performance")
    
    # Check design token usage
    token_metric = next((m for m in quality_results["metrics"] if m.name == "design_token_usage"), None)
    if token_metric and token_metric.value < 85:
        recommendations.append("Replace hardcoded values with design tokens for better consistency and maintainability")
    
    # Check component scores
    component_tests = quality_results.get("component_tests", [])
    low_scoring_components = [ct["component"] for ct in component_tests if ct["score"] < 70]
    if low_scoring_components:
        recommendations.append(f"Improve component isolation for: {', '.join(low_scoring_components)}")
    
    # Check performance
    if "css_load_time" in performance_results and performance_results["css_load_time"] > 1.0:
        recommendations.append("Optimize CSS loading by implementing critical CSS inlining")
    
    if not recommendations:
        recommendations.append("Great job! Your CSS architecture meets all quality standards.")
    
    return recommendations

def print_report_summary(report: Dict[str, Any]):
    """Print a formatted summary of the CSS quality report"""
    
    print("\n" + "=" * 60)
    print("🎯 CSS QUALITY REPORT SUMMARY")
    print("=" * 60)
    
    print(f"\n📊 OVERALL SCORE: {report['overall_score']:.1f}/100")
    
    # Status indicator
    score = report['overall_score']
    if score >= 90:
        print("🟢 EXCELLENT - World-class CSS architecture!")
    elif score >= 80:
        print("🟡 GOOD - Minor improvements needed")
    elif score >= 70:
        print("🟠 WARNING - Several issues to address")
    else:
        print("🔴 CRITICAL - Major refactoring needed")
    
    print(f"\n📅 Generated: {report['timestamp']}")
    
    print(f"\n📏 QUALITY METRICS:")
    for metric in report['quality_metrics']:
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "warning": "🟠",
            "critical": "🔴",
            "error": "❌"
        }.get(metric['status'], "⚪")
        
        print(f"  {status_emoji} {metric['name'].replace('_', ' ').title()}: {metric['value']}{metric['unit']}")
    
    print(f"\n🧩 COMPONENT TESTS:")
    for component in report['component_tests']:
        score = component['score']
        if score >= 90:
            emoji = "🟢"
        elif score >= 75:
            emoji = "🟡"
        else:
            emoji = "🔴"
        print(f"  {emoji} {component['component'].title()}: {score:.1f}%")
    
    print(f"\n⚡ PERFORMANCE:")
    perf = report['performance']
    if 'critical_css' in perf and 'page_load_time' in perf['critical_css']:
        load_time = perf['critical_css']['page_load_time']
        print(f"  📄 Page Load Time: {load_time}s")
    
    if 'unused_css' in perf and 'usage_percent' in perf['unused_css']:
        usage = perf['unused_css']['usage_percent']
        print(f"  🎯 CSS Usage: {usage}%")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n🧪 TEST PAGES:")
    for component, path in report['test_pages'].items():
        print(f"  📝 {component.title()}: {path}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    # Get CSS directory from command line or use default
    if len(sys.argv) > 1:
        css_dir = Path(sys.argv[1])
    else:
        css_dir = Path("assets/css")
    
    if not css_dir.exists():
        print(f"❌ CSS directory not found: {css_dir}")
        print("Usage: python css_quality_assurance.py [css_directory]")
        sys.exit(1)
    
    # Generate report
    report_file = css_dir.parent / "css-quality-report.json"
    report = generate_css_report(css_dir, report_file)
    
    # Print summary
    print_report_summary(report)
    
    print(f"\n📋 Full report available at: {report_file}")
    print("🧪 Component test pages created in: test-components/")
    print("\n🚀 Next steps:")
    print("1. Review recommendations and address critical issues")
    print("2. Test components using generated test pages")
    print("3. Run performance tests on live application")
    print("4. Set up automated quality monitoring")

# =================================================================== 
# CSS Build and Optimization Script
# ===================================================================

# css_build_optimizer.py
"""
CSS Build and Optimization Pipeline
Handles minification, purging, and optimization
"""

import re
import gzip
import subprocess
from pathlib import Path
from typing import Set, List

class CSSOptimizer:
    """Optimizes CSS for production deployment"""
    
    def __init__(self, css_dir: Path, output_dir: Path):
        self.css_dir = css_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def minify_css(self, input_file: Path, output_file: Path):
        """Minify CSS file"""
        content = input_file.read_text()
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        content = re.sub(r':\s*', ':', content)
        content = re.sub(r';\s*', ';', content)
        
        # Remove unnecessary semicolons
        content = re.sub(r';}', '}', content)
        
        output_file.write_text(content.strip())
        
        # Calculate compression
        original_size = len(input_file.read_text())
        minified_size = len(content)
        compression_ratio = (1 - minified_size / original_size) * 100
        
        print(f"✅ Minified {input_file.name}: {compression_ratio:.1f}% smaller")
    
    def create_critical_css(self, used_selectors: Set[str]):
        """Extract critical CSS for above-the-fold content"""
        critical_css = []
        
        # Include foundation CSS
        foundation_dir = self.css_dir / "01-foundation"
        if foundation_dir.exists():
            for foundation_file in foundation_dir.glob("*.css"):
                critical_css.append(foundation_file.read_text())
        
        # Include critical components
        critical_components = ["buttons", "alerts", "navigation"]
        components_dir = self.css_dir / "03-components"
        
        for component in critical_components:
            component_file = components_dir / f"_{component}.css"
            if component_file.exists():
                content = component_file.read_text()
                # Filter to only used selectors
                filtered_content = self.filter_css_by_selectors(content, used_selectors)
                critical_css.append(filtered_content)
        
        # Write critical CSS
        critical_file = self.output_dir / "critical.css"
        critical_file.write_text("\n".join(critical_css))
        
        # Minify critical CSS
        critical_min_file = self.output_dir / "critical.min.css"
        self.minify_css(critical_file, critical_min_file)
        
        return critical_min_file
    
    def filter_css_by_selectors(self, css_content: str, used_selectors: Set[str]) -> str:
        """Filter CSS to only include used selectors"""
        # This is a simplified implementation
        # In production, use a proper CSS parser
        used_rules = []
        
        rules = re.split(r'}', css_content)
        for rule in rules:
            if '{' in rule:
                selector_part, declaration_part = rule.split('{', 1)
                selectors = [s.strip() for s in selector_part.split(',')]
                
                # Check if any selector is used
                if any(self.selector_matches(sel, used_selectors) for sel in selectors):
                    used_rules.append(rule + '}')
        
        return '\n'.join(used_rules)
    
    def selector_matches(self, selector: str, used_selectors: Set[str]) -> bool:
        """Check if a CSS selector matches any used selector"""
        # Extract class names from selector
        classes = re.findall(r'\.([a-zA-Z0-9_-]+)', selector)
        return any(cls in used_selectors for cls in classes)
    
    def build_production_css(self):
        """Build optimized CSS for production"""
        print("🏗️ Building production CSS...")
        
        # Create main production CSS
        main_css = self.css_dir / "main.css"
        if main_css.exists():
            prod_main = self.output_dir / "main.min.css"
            self.minify_css(main_css, prod_main)
            
            # Create gzipped version
            with open(prod_main, 'rb') as f_in:
                with gzip.open(f"{prod_main}.gz", 'wb') as f_out:
                    f_out.write(f_in.read())
            
            print(f"✅ Production CSS created: {prod_main}")
            print(f"✅ Gzipped version: {prod_main}.gz")
        
        # Build critical CSS (would need actual usage data)
        critical_selectors = {"btn", "navbar", "alert", "panel"}  # Example
        critical_file = self.create_critical_css(critical_selectors)
        print(f"✅ Critical CSS created: {critical_file}")

if __name__ == "__main__":
    css_dir = Path("assets/css")
    output_dir = Path("assets/css/dist")
    
    optimizer = CSSOptimizer(css_dir, output_dir)
    optimizer.build_production_css()