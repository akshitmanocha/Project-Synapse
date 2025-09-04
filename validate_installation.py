#!/usr/bin/env python3
"""
Final Validation Test - Comprehensive system check
Tests all components without using LLM API calls to avoid quota issues
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports work"""
    print("🔍 Testing imports...")
    try:
        # Core agent imports
        from synapse.agent.agent import (
            AgentState, _tool_registry, build_graph, 
            reasoning_node, tool_exec_node, reflection_node
        )
        print("  ✅ Agent imports: OK")
        
        # Tool imports
        from synapse.tools import tools as sim_tools
        print("  ✅ Tools imports: OK")
        
        # Core system imports  
        from synapse.core.performance_tracker import PerformanceTracker
        print("  ✅ Performance tracker imports: OK")
        
        # Main CLI
        from main import get_predefined_scenarios, run_cli
        print("  ✅ Main CLI imports: OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_tool_registry():
    """Test tool registry completeness"""
    print("\n🔧 Testing tool registry...")
    try:
        from synapse.agent.agent import _tool_registry
        registry = _tool_registry()
        
        expected_count = 30
        actual_count = len(registry)
        
        if actual_count >= expected_count:
            print(f"  ✅ Tool registry: {actual_count} tools registered")
        else:
            print(f"  ⚠️ Tool registry: Only {actual_count} tools, expected {expected_count}")
        
        # Test critical tools exist
        critical_tools = [
            'contact_support_live', 'escalate_to_management', 'issue_voucher',
            'check_traffic', 'get_merchant_status', 'notify_customer',
            'contact_recipient_via_chat', 'suggest_safe_drop_off'
        ]
        
        missing_tools = [tool for tool in critical_tools if tool not in registry]
        if missing_tools:
            print(f"  ❌ Missing critical tools: {missing_tools}")
            return False
        else:
            print("  ✅ All critical tools present")
        
        # Test tools are callable
        test_tool = registry['check_traffic']
        result = test_tool({})
        if isinstance(result, dict) and 'status' in result:
            print("  ✅ Tools are callable")
        else:
            print("  ❌ Tools not working properly")
            return False
            
        return True
    except Exception as e:
        print(f"  ❌ Tool registry error: {e}")
        return False

def test_scenarios():
    """Test scenario definitions"""
    print("\n📋 Testing scenarios...")
    try:
        from main import get_predefined_scenarios
        scenarios = get_predefined_scenarios()
        
        expected_scenarios = [
            '1.0', '2.0', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8', '2.9',
            'traffic', 'merchant', 'weather',
            'approval.1', 'approval.2', 'approval.3', 'approval.4', 'approval.5',
            'human.1', 'human.2', 'human.3', 'human.4', 'human.5'
        ]
        
        missing_scenarios = [s for s in expected_scenarios if s not in scenarios]
        if missing_scenarios:
            print(f"  ❌ Missing scenarios: {missing_scenarios}")
            return False
        
        print(f"  ✅ All {len(scenarios)} scenarios defined")
        return True
    except Exception as e:
        print(f"  ❌ Scenario test error: {e}")
        return False

def test_graph_construction():
    """Test LangGraph can be built"""
    print("\n🔀 Testing graph construction...")
    try:
        from synapse.agent.agent import build_graph
        graph = build_graph()
        
        if graph:
            print("  ✅ LangGraph builds successfully")
            return True
        else:
            print("  ❌ LangGraph build failed")
            return False
    except Exception as e:
        print(f"  ❌ Graph construction error: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("\n⚙️ Testing environment configuration...")
    try:
        # Check .env.template exists
        env_template = project_root / '.env.template'
        if not env_template.exists():
            print("  ❌ .env.template missing")
            return False
        
        # Check .env exists (for user)
        env_file = project_root / '.env'
        if env_file.exists():
            print("  ✅ .env file exists")
        else:
            print("  ⚠️ .env file not found (user needs to copy from template)")
        
        # Test environment variable defaults
        import os
        max_steps = int(os.getenv("MAX_AGENT_STEPS", "15"))
        max_reflections = int(os.getenv("MAX_REFLECTIONS", "3"))
        llm_timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        
        print(f"  ✅ Environment defaults: MAX_AGENT_STEPS={max_steps}, MAX_REFLECTIONS={max_reflections}, LLM_TIMEOUT={llm_timeout}")
        return True
    except Exception as e:
        print(f"  ❌ Environment config error: {e}")
        return False

def test_cli_structure():
    """Test CLI structure"""
    print("\n💻 Testing CLI structure...")
    try:
        # Test main.py exists and is executable
        main_file = project_root / 'main.py'
        if not main_file.exists():
            print("  ❌ main.py missing")
            return False
        
        # Test CLI help (without running to avoid API calls)
        with open(main_file, 'r') as f:
            content = f.read()
            
        required_flags = ['--scenario', '--verbose', '--quiet', '--executive']
        missing_flags = [flag for flag in required_flags if flag not in content]
        
        if missing_flags:
            print(f"  ❌ Missing CLI flags: {missing_flags}")
            return False
        
        print("  ✅ CLI structure complete")
        return True
    except Exception as e:
        print(f"  ❌ CLI structure error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🧪 PROJECT SYNAPSE - FINAL VALIDATION TEST")
    print("=" * 50)
    print("Testing all components without using LLM API...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Tool Registry", test_tool_registry), 
        ("Scenarios", test_scenarios),
        ("Graph Construction", test_graph_construction),
        ("Environment Config", test_environment_config),
        ("CLI Structure", test_cli_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n⚠️ {test_name} test had issues")
    
    print("\n" + "=" * 50)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED! System is ready for use.")
        print("\n📝 Next steps:")
        print("   1. Ensure .env file has GEMINI_API_KEY set") 
        print("   2. Run: python main.py --scenario traffic --quiet")
        print("   3. If API quota available, test with: python main.py 'test problem'")
    else:
        print("❌ Some tests failed. Check errors above.")
        print("\n🔧 Common fixes:")
        print("   - Run: pip install -r requirements.txt")
        print("   - Check .env file configuration") 
        print("   - Verify Python 3.8+ is being used")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)