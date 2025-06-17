#!/bin/bash
# create_and_run_check.sh
# Create the check script and run it

echo "🏯 CREATING DI CONTAINER CHECK SCRIPT..."

# Create the check script with proper formatting
cat > check_current_state.sh << 'EOF'
#!/bin/bash
# check_current_state.sh
# Check your current DI container usage and guide you through the fix

echo "🏯 YŌSAI INTEL DASHBOARD - DI CONTAINER STATE CHECK"
echo "=================================================="

echo ""
echo "📁 Step 1: Checking your project files..."
echo "----------------------------------------"

# Check if main files exist
if [ -f "app.py" ]; then
    echo "✅ app.py found"
else
    echo "❌ app.py not found"
fi

if [ -f "implementation.py" ]; then
    echo "✅ implementation.py found"
else
    echo "❌ implementation.py not found"
fi

if [ -f "core/service_registry.py" ]; then
    echo "✅ core/service_registry.py found"
else
    echo "❌ core/service_registry.py not found"
fi

if [ -f "core/container.py" ]; then
    echo "✅ core/container.py found"
else
    echo "❌ core/container.py not found"
fi

echo ""
echo "🔍 Step 2: Checking for DI container imports..."
echo "----------------------------------------------"

echo "Files importing get_configured_container_with_yaml:"
grep -r "get_configured_container_with_yaml" . --include="*.py" 2>/dev/null || echo "None found"

echo ""
echo "Files importing from core.service_registry:"
grep -r "from core.service_registry" . --include="*.py" 2>/dev/null || echo "None found"

echo ""
echo "Files importing from core.container:"
grep -r "from core.container" . --include="*.py" 2>/dev/null || echo "None found"

echo ""
echo "🧪 Step 3: Testing current DI container..."
echo "----------------------------------------"

echo "Testing basic import..."
python3 -c "
try:
    from core.container import Container
    print('✅ Basic Container import works')
except ImportError as e:
    print(f'❌ Basic Container import failed: {e}')
" 2>/dev/null

echo "Testing service registry import..."
python3 -c "
try:
    from core.service_registry import get_configured_container    print('✅ Service registry import works')
except ImportError as e:
    print(f'❌ Service registry import failed: {e}')
" 2>/dev/null

echo "Testing container creation..."
python3 -c "
try:
    from core.service_registry import get_configured_container
    container = get_configured_container()
    print('⚠️  Container created but may have circular dependencies')
except Exception as e:
    error_msg = str(e).lower()
    if 'circular' in error_msg:
        print('🔴 CONFIRMED: Circular dependency detected!')
    else:
        print(f'❌ Container creation failed: {e}')
" 2>/dev/null

echo ""
echo "📊 Step 4: Analysis and recommendations..."
echo "----------------------------------------"

# Count files that need updating
FILES_TO_UPDATE=$(grep -l "get_configured_container_with_yaml\|from core.service_registry\|from core.container" *.py 2>/dev/null | wc -l)

echo "Files that need updating: $FILES_TO_UPDATE"

if [ "$FILES_TO_UPDATE" -gt 0 ]; then
    echo ""
    echo "📝 FILES TO UPDATE:"
    grep -l "get_configured_container_with_yaml\|from core.service_registry\|from core.container" *.py 2>/dev/null || echo "None in root directory"
fi

echo ""
echo "🎯 NEXT STEPS:"
echo "-------------"
echo "1. Copy the 4 artifacts I provided:"
echo "   • Fixed DI Container → core/di_container.py"
echo "   • Fixed Service Registry → core/service_registry.py (replace existing)"
echo "   • Comprehensive Tests → tests/test_di_container.py"
echo "   • Verification Script → verify_di_fix.py"
echo ""
echo "2. Update your import statements in:"
if [ -f "implementation.py" ]; then
    echo "   • implementation.py"
fi
if [ -f "app.py" ]; then
    echo "   • app.py"
fi
echo ""
echo "3. Change imports from:"
echo "   from core.service_registry import get_configured_container_with_yaml"
echo "   To:"
echo "   from core.service_registry import get_configured_container"
echo ""
echo "4. Test the fix:"
echo "   python3 verify_di_fix.py"
echo ""

echo "🔧 QUICK FIX COMMANDS:"
echo "--------------------"
echo "# 1. Backup your files first:"
echo "cp core/service_registry.py core/service_registry.py.backup"
echo "cp core/container.py core/container.py.backup"
echo "cp implementation.py implementation.py.backup"
echo ""
echo "# 2. After copying artifacts, test the fix:"
echo "python3 verify_di_fix.py"
echo ""
echo "# 3. Run your dashboard:"
echo "python3 implementation.py"

echo ""
echo "🏆 Your circular dependency issue will be completely fixed!"
echo "=================================================="
EOF

echo "✅ Created check_current_state.sh"

# Make it executable
chmod +x check_current_state.sh

echo "🚀 Running the check script..."
echo ""

# Run the script
./check_current_state.sh
