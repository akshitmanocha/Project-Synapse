#!/usr/bin/env python3
"""
Synapse Agent - Command Line Interface

A sophisticated autonomous AI agent for last-mile logistics coordination.
Features advanced decision-making capabilities, multi-stakeholder orchestration,
and intelligent error recovery through reflection and adaptation.

Usage:
    python main.py "Problem description here"
    python main.py --help
    python main.py --verbose "Problem description"
    python main.py --scenario 2.4
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from synapse import run_agent
    from synapse.agent import AgentState
    from synapse.tools import debug_tools
    from synapse.core.performance_tracker import PerformanceTracker
    from synapse.core.executive_display import ExecutiveDisplay
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure you're in the project root directory and have installed the package:")
    print("pip install -e .")
    sys.exit(1)


def print_banner():
    """Print the Synapse Agent banner."""
    print("🚀 " + "=" * 60 + " 🚀")
    print("    SYNAPSE AGENT - Autonomous Logistics Coordination")
    print("    Advanced Problem-Solving with Reflection & Adaptation")
    print("🚀 " + "=" * 60 + " 🚀")
    print()


def print_chain_of_thought(steps: List[Dict[str, Any]], verbose: bool = False):
    """
    Display the agent's chain of thought in a structured, readable format with clear headings.
    
    Args:
        steps: List of agent reasoning and action steps
        verbose: Whether to show detailed observations
    """
    if not steps:
        print("\n" + "=" * 70)
        print("🧠 AGENT CHAIN OF THOUGHT")
        print("=" * 70)
        print("⚠️  No reasoning steps were recorded.")
        return
    
    print("\n" + "=" * 70)
    print("🧠 AGENT CHAIN OF THOUGHT")
    print("=" * 70)
    
    for i, step in enumerate(steps, 1):
        is_reflection = step.get("action", {}).get("tool_name") == "reflect"
        step_type = "REFLECTION & REASONING" if is_reflection else "ACTION & EXECUTION"
        step_icon = "🤔" if is_reflection else "🛠️"
        
        # Step header with clear visual separation
        print(f"\n┌─ STEP {i}: {step_icon} {step_type} " + "─" * (50 - len(f"STEP {i}: {step_type}")))
        print("│")
        
        # THOUGHT section with clear heading
        if "thought" in step and step["thought"]:
            print("│ 💭 THOUGHT:")
            thought_lines = step["thought"].split('\n')
            for line in thought_lines:
                if line.strip():
                    print(f"│    {line.strip()}")
            print("│")
        
        # ACTION section with clear heading
        if "action" in step and step["action"]:
            action = step["action"]
            tool_name = action.get("tool_name", "unknown")
            parameters = action.get("parameters", {})
            
            if tool_name != "reflect":  # Don't show action details for reflection steps
                print("│ 🔧 ACTION:")
                print(f"│    Tool Used: {tool_name}")
                if parameters and verbose:
                    print(f"│    Parameters: {parameters}")
                elif parameters:
                    # Show key parameters in non-verbose mode
                    key_params = {k: v for k, v in parameters.items() if k in ["customer_id", "driver_id", "order_id", "recipient_id"]}
                    if key_params:
                        print(f"│    Key Parameters: {key_params}")
                print("│")
        
        # OBSERVATION section with clear heading
        if "observation" in step and step["observation"]:
            obs = step["observation"]
            
            print("│ 👁️  OBSERVATION:")
            
            if verbose:
                # Full observation in verbose mode
                obs_str = str(obs)
                obs_lines = obs_str.split('\n')
                for line in obs_lines:
                    if line.strip():
                        print(f"│    {line.strip()}")
            else:
                # Formatted key results in normal mode
                if isinstance(obs, dict):
                    # Success/failure indicators
                    success_fields = ["success", "delivered", "contact_successful", "scheduled", 
                                    "available", "refund_issued", "completed"]
                    status_fields = ["status", "result", "fault", "confidence", "reason"]
                    
                    success_results = {k: "✅ Yes" if v else "❌ No" for k, v in obs.items() 
                                     if k in success_fields and v is not None}
                    status_results = {k: v for k, v in obs.items() 
                                    if k in status_fields and v is not None}
                    
                    if success_results:
                        for key, value in success_results.items():
                            print(f"│    {key.replace('_', ' ').title()}: {value}")
                    
                    if status_results:
                        for key, value in status_results.items():
                            print(f"│    {key.replace('_', ' ').title()}: {value}")
                    
                    # Show other relevant information
                    other_fields = {k: v for k, v in obs.items() 
                                  if k not in success_fields + status_fields and v is not None}
                    if other_fields:
                        for key, value in other_fields.items():
                            if len(str(value)) > 50:
                                print(f"│    {key.replace('_', ' ').title()}: {str(value)[:47]}...")
                            else:
                                print(f"│    {key.replace('_', ' ').title()}: {value}")
                else:
                    # Handle non-dict observations
                    obs_str = str(obs)
                    if len(obs_str) > 60:
                        print(f"│    {obs_str[:57]}...")
                    else:
                        print(f"│    {obs_str}")
        
        # Close the step box
        print("└" + "─" * 69)


def print_final_plan(result: Dict[str, Any]):
    """Display the final resolution plan with enhanced formatting."""
    print("\n" + "=" * 70)
    print("🎯 FINAL RESOLUTION PLAN")
    print("=" * 70)
    
    # Main plan section with clear heading
    print("\n📋 FINAL PLAN:")
    print("┌" + "─" * 68 + "┐")
    
    if "plan" in result and result["plan"]:
        # Format the plan with proper line wrapping
        plan_text = result["plan"]
        plan_lines = plan_text.split('\n')
        
        for line in plan_lines:
            if line.strip():
                # Wrap long lines for better readability
                words = line.strip().split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 64:
                        current_line += word + " "
                    else:
                        if current_line:
                            print(f"│ {current_line.ljust(66)} │")
                        current_line = word + " "
                if current_line:
                    print(f"│ {current_line.strip().ljust(66)} │")
            else:
                print(f"│{' ' * 68}│")
    else:
        print(f"│ ⚠️  No final plan was generated.{' ' * 34} │")
    
    print("└" + "─" * 68 + "┘")
    
    # Execution summary with clear headings
    print("\n📊 EXECUTION SUMMARY:")
    print("┌" + "─" * 68 + "┐")
    
    total_steps = len(result.get('steps', []))
    completed = result.get('done', False)
    needs_adaptation = result.get("needs_adaptation", False)
    
    # Steps information
    print(f"│ Total Steps Executed: {total_steps:<48} │")
    print(f"│ Status: {'✅ Successfully Completed' if completed else '⚠️  Partially Completed':<56} │")
    
    # Reflection and adaptation information
    if needs_adaptation:
        print(f"│ Adaptations Made: ✅ Yes{' ' * 44} │")
        if result.get("reflection_reason"):
            reason = result.get("reflection_reason")
            if len(reason) > 45:
                reason = reason[:42] + "..."
            print(f"│ Last Reflection: {reason:<48} │")
    else:
        print(f"│ Adaptations Made: ❌ None needed{' ' * 35} │")
    
    # Tool usage summary if available
    if total_steps > 0:
        reflection_steps = sum(1 for step in result.get('steps', []) 
                             if step.get('action', {}).get('tool_name') == 'reflect')
        action_steps = total_steps - reflection_steps
        
        print(f"│ Action Steps: {action_steps:<52} │")
        print(f"│ Reflection Steps: {reflection_steps:<48} │")
    
    print("└" + "─" * 68 + "┘")


def _quick_api_check() -> bool:
    """Quick API availability check before running the agent."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            print("   Please add your API key to the .env file")
            return False
        
        # Very quick test call
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key=api_key,
            timeout=5  # Short timeout for quick check
        )
        
        test_message = HumanMessage(content="OK")
        response = llm.invoke([test_message])
        
        return bool(response and response.content)
        
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str or "resourceexhausted" in error_str.lower():
            print("❌ Google Gemini API quota exceeded (50 requests/day limit)")
            print("   • Wait 24 hours for quota reset")
            print("   • Get new API key from https://ai.google.dev/")
            print("   • Run: python check_api_quota.py for detailed check")
        elif "api_key" in error_str.lower() or "invalid" in error_str.lower():
            print("❌ Invalid API key - check your GEMINI_API_KEY in .env")
        else:
            print(f"❌ API Error: {str(e)[:100]}...")
        return False

def get_predefined_scenarios() -> Dict[str, str]:
    """Get predefined test scenarios."""
    return {
        "1.0": "Restaurant is overloaded and cannot fulfill the order within the expected time frame",
        "2.0": "Package arrived damaged and the customer disputes who is at fault",
        "2.2": "Item is out of stock and needs to be replaced with customer's preferred alternative",
        "2.3": "Driver is at the customer's location but there's a dispute about the order at the door",
        "2.4": "A driver is at the customer's location, but the recipient is not available to receive a valuable package",
        "2.5": "Driver cannot locate delivery address due to incorrect or incomplete information like missing unit number",
        "2.6": "Passenger's trip is impacted by sudden severe traffic event like major accident or road closure",
        "2.7": "Passenger reports losing a personal item in the vehicle after trip completion",
        "2.8": "Driver encounters unsafe road conditions including protest, road hazard, or severe weather requiring immediate rerouting",
        "2.9": "Driver has accepted a booking but is not moving or responding to contact attempts for over 10 minutes",
        "traffic": "Driver stuck in heavy traffic, 45-minute delay expected for customer order",
        "merchant": "Merchant's kitchen equipment broke down, cannot prepare the order",
        "weather": "Severe weather conditions preventing safe delivery completion",
        
        # New approval-requiring scenarios
        "approval.1": "Customer extremely upset about cold food delivery, demanding $50 voucher compensation",
        "approval.2": "VIP customer's $2000 jewelry order delayed due to driver accident, needs immediate management escalation",
        "approval.3": "Driver's vehicle damaged while avoiding road hazard during delivery, requesting expense reimbursement",
        "approval.4": "System outage caused 3-hour merchant downtime, merchant requesting platform credit compensation",
        "approval.5": "Multiple delivery failures due to address issues, customer demands premium redelivery with waived fees",
        
        # High-stakes scenarios requiring human intervention
        "human.1": "Driver reports customer threatened physical violence over late delivery, safety concern escalation needed",
        "human.2": "Customer claims driver stole $500 cash tip, potential legal liability and fraud investigation required",
        "human.3": "Delivery vehicle involved in minor accident with $10,000 damages, insurance and legal coordination needed",
        "human.4": "Food poisoning complaint goes viral on social media with 50K shares, crisis management required",
        "human.5": "Government inspector found health violations during delivery pickup, regulatory compliance issue"
    }


def run_cli():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Synapse Agent - Autonomous Logistics Coordination Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s "Driver stuck in traffic for 45 minutes"
    %(prog)s --verbose "Package damaged, customer disputes fault"
    %(prog)s --scenario 2.4
    %(prog)s --scenario traffic --verbose
    %(prog)s --list-scenarios
        """
    )
    
    # Main argument groups
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "problem",
        nargs="?",
        help="Logistics problem description to solve"
    )
    input_group.add_argument(
        "--scenario", "-s",
        type=str,
        help="Use a predefined scenario (1.0, 2.0-2.9, traffic, approval.1-5, human.1-5)"
    )
    input_group.add_argument(
        "--list-scenarios", "-l",
        action="store_true",
        help="List all predefined scenarios"
    )
    
    # Display options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed observations and tool parameters"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show final resolution plan"
    )
    parser.add_argument(
        "--executive", "-e",
        action="store_true",
        help="Executive mode: Show real-time performance metrics and visualizations"
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Don't show the banner"
    )
    parser.add_argument(
        "--debug-tools",
        action="store_true",
        help="Show available tools and their metadata"
    )
    
    args = parser.parse_args()
    
    # Handle list scenarios
    if args.list_scenarios:
        scenarios = get_predefined_scenarios()
        print("📋 AVAILABLE PREDEFINED SCENARIOS")
        print("=" * 40)
        for key, description in scenarios.items():
            print(f"🎯 {key}: {description}")
        return
    
    # Handle debug tools
    if args.debug_tools:
        print("🛠️  AVAILABLE TOOLS")
        print("=" * 30)
        debug_tools()
        return
    
    # Show banner unless quiet or no-banner
    if not args.quiet and not args.no_banner:
        print_banner()
    
    # Determine the problem to solve
    if args.scenario:
        scenarios = get_predefined_scenarios()
        if args.scenario not in scenarios:
            print(f"❌ Unknown scenario: {args.scenario}")
            print(f"Available scenarios: {', '.join(scenarios.keys())}")
            sys.exit(1)
        problem = scenarios[args.scenario]
        if not args.quiet:
            print(f"🎯 Using scenario '{args.scenario}': {problem}")
            print()
    else:
        problem = args.problem
        if not args.quiet:
            print(f"🎯 Problem: {problem}")
            print()
    
    # Validate that we have a problem to solve (unless using utility flags)
    if not problem or not problem.strip():
        if not args.list_scenarios and not args.debug_tools:
            print("❌ Error: Please provide a problem description or use --scenario.")
            print("Use --help for usage information or --list-scenarios to see available scenarios.")
            sys.exit(1)
        return  # Exit early for utility commands
    
    try:
        # Record start time
        start_time = datetime.now()
        
        # Initialize executive display if needed
        display = None
        if args.executive:
            display = ExecutiveDisplay()
            display.start()
        
        if not args.quiet:
            print("🚀 Starting Synapse Agent...")
            print(f"⏰ Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        # Determine scenario type for tracking
        scenario_type = args.scenario if args.scenario else "custom"
        
        # Quick API availability check before running
        if not _quick_api_check():
            if args.executive and display:
                display.stop()
            return
            
        # Run the agent with performance tracking if in executive mode
        result = run_agent(problem, scenario_type=scenario_type, enable_performance_tracking=args.executive, executive_display=display)
        
        # Record end time
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Stop executive display and show final metrics
        if args.executive and display:
            display.stop()
            
            # Get final performance metrics
            tracker = PerformanceTracker()
            if tracker.query_history:
                last_query = tracker.query_history[-1]
                
                # Show executive summary
                print("\n" + "=" * 70)
                print("📊 EXECUTIVE PERFORMANCE SUMMARY")
                print("=" * 70)
                
                print(f"\n📈 Query Metrics:")
                print(f"  • Total Duration: {duration.total_seconds():.2f} seconds")
                # Get actual data from result if tracker data is missing
                total_steps = last_query.total_steps if last_query.total_steps > 0 else len(result.get("steps", []))
                tool_count = len(last_query.tool_executions) if last_query.tool_executions else len([s for s in result.get("steps", []) if s.get("action")])
                reflection_count = last_query.reflection_steps if hasattr(last_query, 'reflection_steps') else len([s for s in result.get("steps", []) if s.get("action", {}).get("tool_name") == "reflect"])
                
                print(f"  • Steps Executed: {total_steps}")
                print(f"  • Tools Used: {tool_count}")
                print(f"  • Reflections: {reflection_count}")
                
                print(f"\n⚡ Efficiency Analysis:")
                print(f"  • Parallel Executions: {last_query.parallel_executions}")
                print(f"  • Time Saved: {last_query.time_saved_by_parallelization:.2f}s")
                print(f"  • Complexity Score: {last_query.get_complexity_score()}/10")
                print(f"  • First-Try Success: {'Yes ✅' if last_query.first_try_success else 'No (Reflection Used)'}")
                
                print(f"\n💰 Cost Analysis:")
                print(f"  • Total Tokens: {last_query.total_input_tokens + last_query.total_output_tokens:,}")
                print(f"  • Estimated Cost: ${last_query.estimated_cost:.4f}")
                print(f"  • LLM Calls: {last_query.llm_calls}")
                print(f"  • Avg Response Time: {last_query.avg_llm_response_time:.2f}s")
                
                # Tool performance breakdown
                if last_query.tool_executions:
                    print(f"\n🔧 Tool Execution Breakdown:")
                    for tool in last_query.tool_executions[:5]:  # Show top 5
                        status_icon = "✅" if tool.status == "success" else "❌"
                        print(f"  {status_icon} {tool.tool_name}: {tool.duration:.2f}s")
                
                # Export metrics if requested
                metrics_file = f"metrics_{last_query.query_id}.json"
                tracker.export_metrics(metrics_file)
                print(f"\n📁 Detailed metrics exported to: {metrics_file}")
        
        elif not args.quiet:
            print(f"\n⏰ Execution completed in {duration.total_seconds():.2f} seconds")
            print()
        
        # Display results based on verbosity (skip in executive mode as it has its own display)
        if not args.quiet and not args.executive:
            print_chain_of_thought(result.get("steps", []), verbose=args.verbose)
        
        print_final_plan(result)
        
        # Success indicator
        if result.get("done", False):
            print("\n✅ Agent successfully resolved the logistics problem!")
        else:
            print("\n⚠️  Agent completed processing but may require additional steps.")
        
    except KeyboardInterrupt:
        if display:
            display.stop()
        print("\n\n⏸️  Execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        if display:
            display.stop()
        print(f"\n❌ Error during execution: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
