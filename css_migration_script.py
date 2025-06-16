# css_migration_script.py
"""
Automated CSS Migration Script for Yōsai Intel Dashboard
Converts existing dashboard.css to modular architecture
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class CSSMigrator:
    """Handles the migration from monolithic to modular CSS"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.css_dir = self.project_root / "assets" / "css"
        self.old_css = self.project_root / "assets" / "dashboard.css"
        
        # CSS Category mappings
        self.component_patterns = {
            "buttons": [r"\.btn", r"\..*-button", r"\.complete-button", r"\.resolve-button"],
            "chips": [r"\.chip", r"\.detection-chip"],
            "cards": [r"\.card", r"\.ticket-card", r"\.signal-card"],
            "alerts": [r"\.alert", r"\.notification"],
            "panels": [r"\.panel", r"\..*-panel"],
            "forms": [r"\.form", r"\.input", r"\.select"],
            "navigation": [r"\.nav", r"\.navbar"]
        }
        
        self.layout_patterns = [
            r"\.main-content", r"\.dashboard", r"\.container", 
            r"\.row", r"\.col", r"\.grid", r"\.flex"
        ]
        
        self.utility_patterns = [
            r"\.text-", r"\.font-", r"\.bg-", r"\.p-", r"\.m-", 
            r"\.w-", r"\.h-", r"\.display-", r"\.position-"
        ]
    
    def create_directory_structure(self):
        """Create the modular CSS directory structure"""
        directories = [
            "01-foundation",
            "02-layout", 
            "03-components",
            "04-panels",
            "05-pages",
            "06-themes",
            "07-utilities"
        ]
        
        for directory in directories:
            dir_path = self.css_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
    
    def backup_current_css(self):
        """Backup existing CSS file"""
        if self.old_css.exists():
            backup_path = self.old_css.with_suffix('.css.backup')
            shutil.copy2(self.old_css, backup_path)
            print(f"✅ Backed up existing CSS to: {backup_path}")
    
    def extract_css_rules(self, css_content: str) -> Dict[str, List[str]]:
        """Extract CSS rules and categorize them"""
        rules = {
            "foundation": [],
            "layout": [],
            "components": {},
            "panels": [],
            "utilities": [],
            "uncategorized": []
        }
        
        # Split CSS into individual rules
        css_rules = re.findall(r'([^{}]+)\s*\{[^{}]*\}', css_content, re.DOTALL)
        
        for rule in css_rules:
            selector = rule.strip()
            categorized = False
            
            # Check for foundation (variables, resets)
            if selector.startswith(':root') or selector.startswith('*'):
                rules["foundation"].append(rule)
                categorized = True
            
            # Check for layout patterns
            elif any(re.search(pattern, selector) for pattern in self.layout_patterns):
                rules["layout"].append(rule)
                categorized = True
            
            # Check for utility patterns
            elif any(re.search(pattern, selector) for pattern in self.utility_patterns):
                rules["utilities"].append(rule)
                categorized = True
            
            # Check for component patterns
            else:
                for component, patterns in self.component_patterns.items():
                    if any(re.search(pattern, selector) for pattern in patterns):
                        if component not in rules["components"]:
                            rules["components"][component] = []
                        rules["components"][component].append(rule)
                        categorized = True
                        break
            
            # Check for panel patterns
            if not categorized and 'panel' in selector.lower():
                rules["panels"].append(rule)
                categorized = True
            
            if not categorized:
                rules["uncategorized"].append(rule)
        
        return rules
    
    def create_foundation_files(self):
        """Create foundation CSS files with design tokens"""
        
        # Variables file content
        variables_content = '''/* =================================================================== */
/* 01-foundation/_variables.css - Design Token System */
/* =================================================================== */

:root {
  /* Extracted from existing dashboard.css */
  --color-primary: #1B2A47;
  --color-accent: #2196F3;
  --color-accent-hover: #42A5F5;
  --color-success: #2DBE6C;
  --color-warning: #FFB020;
  --color-critical: #E02020;
  --color-background: #0F1419;
  --color-surface: #1A2332;
  --color-border: #2D3748;
  --color-text-primary: #F7FAFC;
  --color-text-secondary: #E2E8F0;
  --color-text-tertiary: #A0AEC0;
  
  /* Spacing system (8pt grid) */
  --space-0: 0;
  --space-1: 0.25rem;    /* 4px */
  --space-2: 0.5rem;     /* 8px */
  --space-3: 0.75rem;    /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-5: 1.25rem;    /* 20px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  
  /* Border radius */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-full: 9999px;
  
  /* Typography */
  --font-family-system: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  
  /* Font weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Transitions */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  
  /* Shadows */
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
'''
        
        # Write variables file
        variables_path = self.css_dir / "01-foundation" / "_variables.css"
        variables_path.write_text(variables_content)
        print(f"✅ Created variables file: {variables_path}")
        
        # Reset file content
        reset_content = '''/* =================================================================== */
/* 01-foundation/_reset.css - Modern CSS Reset */
/* =================================================================== */

*, *::before, *::after {
  box-sizing: border-box;
}

* {
  margin: 0;
}

html, body {
  height: 100%;
}

body {
  line-height: 1.5;
  font-family: var(--font-family-system);
  color: var(--color-text-primary);
  background-color: var(--color-background);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
}
'''
        
        reset_path = self.css_dir / "01-foundation" / "_reset.css"
        reset_path.write_text(reset_content)
        print(f"✅ Created reset file: {reset_path}")
    
    def create_main_css(self):
        """Create the main CSS file that imports all modules"""
        
        main_content = '''/* =================================================================== */
/* assets/css/main.css - Master Import File */
/* =================================================================== */

/* Foundation Layer */
@import './01-foundation/_variables.css';
@import './01-foundation/_reset.css';
@import './01-foundation/_typography.css';
@import './01-foundation/_accessibility.css';

/* Layout System */
@import './02-layout/_grid.css';
@import './02-layout/_containers.css';
@import './02-layout/_spacing.css';

/* Component Library */
@import './03-components/_buttons.css';
@import './03-components/_cards.css';
@import './03-components/_chips.css';
@import './03-components/_alerts.css';
@import './03-components/_forms.css';
@import './03-components/_navigation.css';

/* Dashboard Panels */
@import './04-panels/_panel-base.css';
@import './04-panels/_map-panel.css';
@import './04-panels/_alert-panel.css';
@import './04-panels/_signal-panel.css';
@import './04-panels/_bottom-panel.css';
@import './04-panels/_navbar.css';

/* Page-Specific Styles */
@import './05-pages/_dashboard.css';
@import './05-pages/_analytics.css';

/* Theme System */
@import './06-themes/_dark-theme.css';

/* Utility Classes */
@import './07-utilities/_display.css';
@import './07-utilities/_flexbox.css';
@import './07-utilities/_colors.css';
@import './07-utilities/_spacing.css';
@import './07-utilities/_text.css';
'''
        
        main_path = self.css_dir / "main.css"
        main_path.write_text(main_content)
        print(f"✅ Created main CSS file: {main_path}")
    
    def convert_existing_css(self):
        """Convert existing dashboard.css to new structure"""
        if not self.old_css.exists():
            print(f"❌ Could not find existing CSS file: {self.old_css}")
            return
        
        # Read existing CSS
        css_content = self.old_css.read_text()
        print(f"📖 Reading existing CSS: {len(css_content)} characters")
        
        # Extract and categorize rules
        rules = self.extract_css_rules(css_content)
        
        # Create component files
        for component, component_rules in rules["components"].items():
            if component_rules:
                component_path = self.css_dir / "03-components" / f"_{component}.css"
                component_content = f"""/* =================================================================== */
/* 03-components/_{component}.css - {component.title()} Component System */
/* =================================================================== */

{chr(10).join(component_rules)}
"""
                component_path.write_text(component_content)
                print(f"✅ Created component file: {component_path}")
        
        # Create layout file
        if rules["layout"]:
            layout_path = self.css_dir / "02-layout" / "_dashboard-layout.css"
            layout_content = f"""/* =================================================================== */
/* 02-layout/_dashboard-layout.css - Dashboard Layout System */
/* =================================================================== */

{chr(10).join(rules["layout"])}
"""
            layout_path.write_text(layout_content)
            print(f"✅ Created layout file: {layout_path}")
        
        # Create utilities file
        if rules["utilities"]:
            utilities_path = self.css_dir / "07-utilities" / "_extracted.css"
            utilities_content = f"""/* =================================================================== */
/* 07-utilities/_extracted.css - Extracted Utility Classes */
/* =================================================================== */

{chr(10).join(rules["utilities"])}
"""
            utilities_path.write_text(utilities_content)
            print(f"✅ Created utilities file: {utilities_path}")
        
        # Report uncategorized rules
        if rules["uncategorized"]:
            print(f"⚠️  Found {len(rules['uncategorized'])} uncategorized rules")
            uncategorized_path = self.css_dir / "_uncategorized.css"
            uncategorized_content = f"""/* =================================================================== */
/* _uncategorized.css - Rules that need manual categorization */
/* =================================================================== */

{chr(10).join(rules["uncategorized"])}
"""
            uncategorized_path.write_text(uncategorized_content)
            print(f"📝 Created uncategorized file for manual review: {uncategorized_path}")
    
    def update_app_py(self):
        """Update app.py to use new CSS system"""
        app_file = self.project_root / "app.py"
        
        if not app_file.exists():
            print(f"❌ Could not find app.py file: {app_file}")
            return
        
        # Read current app.py
        app_content = app_file.read_text()
        
        # Replace CSS import
        updated_content = re.sub(
            r'external_stylesheets=\[dbc\.themes\.BOOTSTRAP\]',
            'external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/css/main.css"]',
            app_content
        )
        
        # If no change was made, add the CSS import
        if updated_content == app_content:
            updated_content = re.sub(
                r'app = dash\.Dash\(',
                'app = dash.Dash(',
                app_content
            )
            updated_content = re.sub(
                r'external_stylesheets=\[[^\]]*\]',
                'external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/css/main.css"]',
                updated_content
            )
        
        # Write updated app.py
        app_file.write_text(updated_content)
        print(f"✅ Updated app.py to use new CSS system")
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting CSS Migration Process...")
        print("=" * 50)
        
        # Step 1: Create directory structure
        self.create_directory_structure()
        
        # Step 2: Backup existing CSS
        self.backup_current_css()
        
        # Step 3: Create foundation files
        self.create_foundation_files()
        
        # Step 4: Convert existing CSS
        self.convert_existing_css()
        
        # Step 5: Create main CSS file
        self.create_main_css()
        
        # Step 6: Update app.py
        self.update_app_py()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Review generated CSS files")
        print("2. Manually categorize any uncategorized rules")
        print("3. Update HTML classes to use new component system")
        print("4. Test the application")
        print("5. Remove old dashboard.css when confident")

# validation_script.py
"""
CSS Validation and Testing Script
"""

def validate_css_structure(css_dir: Path) -> Dict[str, bool]:
    """Validate that all required CSS files exist"""
    required_files = [
        "01-foundation/_variables.css",
        "01-foundation/_reset.css", 
        "02-layout/_grid.css",
        "03-components/_buttons.css",
        "03-components/_chips.css",
        "04-panels/_panel-base.css",
        "main.css"
    ]
    
    results = {}
    for file_path in required_files:
        full_path = css_dir / file_path
        results[file_path] = full_path.exists()
    
    return results

def check_css_variables_usage(css_dir: Path) -> List[str]:
    """Check for hardcoded values that should use CSS variables"""
    violations = []
    
    # Common patterns that should use variables
    patterns = [
        (r'color:\s*#[0-9a-fA-F]{6}', 'Use CSS color variables'),
        (r'padding:\s*\d+px', 'Use spacing variables'),
        (r'margin:\s*\d+px', 'Use spacing variables'),
        (r'border-radius:\s*\d+px', 'Use radius variables'),
        (r'font-size:\s*\d+px', 'Use text size variables')
    ]
    
    for css_file in css_dir.rglob("*.css"):
        content = css_file.read_text()
        for pattern, message in patterns:
            matches = re.findall(pattern, content)
            if matches:
                violations.append(f"{css_file.name}: {message} - Found: {matches}")
    
    return violations

def generate_component_documentation(css_dir: Path):
    """Generate documentation for all components"""
    docs_content = """# Yōsai Intel CSS Component Documentation

## Component Library

"""
    
    components_dir = css_dir / "03-components"
    if components_dir.exists():
        for component_file in components_dir.glob("_*.css"):
            component_name = component_file.stem[1:]  # Remove underscore
            docs_content += f"""
### {component_name.title()} Component

**File:** `{component_file.relative_to(css_dir)}`

**Usage:**
```html
<!-- Basic usage -->
<div class="{component_name}">{component_name.title()} Content</div>

<!-- With modifiers -->
<div class="{component_name} {component_name}--variant">{component_name.title()} Variant</div>
```

**Available Variants:**
- `{component_name}--primary`
- `{component_name}--secondary`
- `{component_name}--small`
- `{component_name}--large`

---
"""
    
    docs_file = css_dir / "COMPONENT_DOCS.md"
    docs_file.write_text(docs_content)
    print(f"✅ Generated component documentation: {docs_file}")

if __name__ == "__main__":
    import sys
    
    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Initialize migrator
    migrator = CSSMigrator(project_root)
    
    # Run migration
    migrator.run_migration()
    
    # Validate results
    print("\n🔍 Validating migration results...")
    validation_results = validate_css_structure(migrator.css_dir)
    
    all_valid = True
    for file_path, exists in validation_results.items():
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_valid = False
    
    if all_valid:
        print("\n🎉 All required files created successfully!")
    else:
        print("\n⚠️  Some required files are missing. Please check the output above.")
    
    # Check for CSS violations
    violations = check_css_variables_usage(migrator.css_dir)
    if violations:
        print(f"\n⚠️  Found {len(violations)} CSS violations:")
        for violation in violations[:5]:  # Show first 5
            print(f"   {violation}")
        if len(violations) > 5:
            print(f"   ... and {len(violations) - 5} more")
    else:
        print("\n✅ No CSS violations found!")
    
    # Generate documentation
    generate_component_documentation(migrator.css_dir)
    
    print(f"\n📚 Migration complete! CSS files created in: {migrator.css_dir}")
    print("Run your application to test the new CSS system.")

# =================================================================== 
# Updated app.py configuration
# ===================================================================

# app.py - Updated with new CSS system
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input

# Import your existing components
from components import navbar, incident_alerts_panel, map_panel, bottom_panel, weak_signal_panel

# Initialize the Dash app with new CSS system
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "/assets/css/main.css"  # New modular CSS system
    ],
    suppress_callback_exceptions=True,
    use_pages=True,
    # Add meta tags for better mobile experience
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "theme-color", "content": "#1B2A47"}
    ]
)

server = app.server

# Main dashboard page layout with new CSS classes
def dashboard_layout():
    return html.Div([
        # Navbar
        html.Div(navbar.layout, className='dashboard__navbar'),
        
        # Main content grid
        html.Div([
            html.Div(
                incident_alerts_panel.layout, 
                className='dashboard__left-panel panel'
            ),
            html.Div(
                map_panel.layout, 
                className='dashboard__map-panel map-panel'
            ),
            html.Div(
                weak_signal_panel.layout, 
                className='dashboard__right-panel panel'
            ),
        ], className='dashboard__content'),
        
        # Bottom panel
        html.Div(bottom_panel.layout, className='dashboard__bottom-panel')
    ], className='dashboard')

# Register the main dashboard as the index page
dash.register_page(
    "dashboard", 
    path="/", 
    title="Yōsai Intel Dashboard",
    layout=dashboard_layout
)

# App layout with page container
app.layout = html.Div([
    dcc.Location(id='url'),
    dash.page_container
], id='app-container')

if __name__ == '__main__':
    app.run_server(debug=True)