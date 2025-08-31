#!/usr/bin/env python3
"""
Test scenarios for the Synapse agent system.

This module contains test scenarios to validate the agent's reasoning capabilities
and ensure it follows the ANALYZE -> STRATEGIZE -> EXECUTE -> ADAPT framework.
"""

import json
import time
from typing import Dict, Any, List
from src.agent import run_agent


class ScenarioTester:
    """Test harness for agent scenarios."""
    
    def __init__(self):
        self.results = {}
    
    def print_chain_of_thought(self, result: Dict[str, Any], scenario_name: str):
        """Print the agent's chain of thought in a clear, readable format."""
        print(f"\n{'=' * 60}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'=' * 60}")
        
        print(f"\nINPUT PROBLEM:")
        print(f"  {result.get('input', 'N/A')}")
        
        steps = result.get('steps', [])
        print(f"\nCHAIN OF THOUGHT ({len(steps)} steps):")
        print("-" * 50)
        
        for i, step in enumerate(steps, 1):
            thought = step.get('thought', 'No thought recorded')
            action = step.get('action', {})
            observation = step.get('observation', 'No observation')
            
            print(f"\nSTEP {i}:")
            print(f"  THOUGHT: {thought[:200]}{'...' if len(thought) > 200 else ''}")
            
            if action:
                tool_name = action.get('tool_name', 'Unknown')
                parameters = action.get('parameters', {})
                print(f"  ACTION: {tool_name}({parameters})")
            
            if observation and observation != 'No observation':
                if isinstance(observation, dict):
                    status = observation.get('status', 'unknown')
                    tool_name = observation.get('tool_name', 'unknown')
                    print(f"  RESULT: {tool_name} -> {status}")
                    
                    # Show key results based on tool type
                    if tool_name == 'get_merchant_status':
                        prep_time = observation.get('prep_time_mins', 'N/A')
                        is_open = observation.get('open', 'N/A')
                        print(f"    Prep Time: {prep_time} mins, Open: {is_open}")
                    elif tool_name == 'check_traffic':
                        delay = observation.get('delay_mins', 'N/A')
                        incident = observation.get('incident_level', 'N/A')
                        print(f"    Delay: {delay} mins, Incident: {incident}")
                    elif tool_name == 'notify_customer':
                        delivered = observation.get('delivered', 'N/A')
                        message_id = observation.get('message_id', 'N/A')
                        print(f"    Delivered: {delivered}, Message ID: {message_id}")
                else:
                    print(f"  RESULT: {observation}")
        
        print(f"\nFINAL PLAN:")
        final_plan = result.get('plan', 'No final plan')
        print(f"  {final_plan}")
        
        print(f"\nCOMPLETED: {result.get('done', False)}")
        print("=" * 60)
    
    def validate_scenario_2_reasoning(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that the agent followed correct reasoning for Scenario 2 (Damaged Packaging Dispute)."""
        steps = result.get('steps', [])
        validation = {
            'collected_evidence': False,
            'analyzed_evidence': False,
            'followed_sequential_workflow': False,
            'made_data_driven_decision': False,
            'took_appropriate_action': False,
            'notified_stakeholders': False,
            'completed_successfully': result.get('done', False)
        }
        
        evidence_id = None
        collect_step = None
        analyze_step = None
        action_step = None
        
        # Check tool usage and sequence
        for i, step in enumerate(steps):
            action = step.get('action', {})
            tool_name = action.get('tool_name', '')
            thought = step.get('thought', '').lower()
            observation = step.get('observation', {})
            
            if tool_name == 'collect_evidence':
                validation['collected_evidence'] = True
                collect_step = i
                if isinstance(observation, dict):
                    evidence_id = observation.get('evidence_id')
            
            elif tool_name == 'analyze_evidence':
                validation['analyzed_evidence'] = True
                analyze_step = i
                
                # Check if analysis led to decision
                if isinstance(observation, dict):
                    fault = observation.get('result', {}).get('fault')
                    confidence = observation.get('result', {}).get('confidence', 0)
                    if fault and confidence > 0.5:
                        validation['made_data_driven_decision'] = True
            
            elif tool_name in ['issue_instant_refund', 'exonerate_driver']:
                validation['took_appropriate_action'] = True
                action_step = i
            
            elif tool_name == 'notify_customer':
                validation['notified_stakeholders'] = True
        
        # Check sequential workflow (collect -> analyze -> action)
        if collect_step is not None and analyze_step is not None:
            if collect_step < analyze_step:
                if action_step is None or analyze_step < action_step:
                    validation['followed_sequential_workflow'] = True
        
        return validation

    def validate_scenario_1_reasoning(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that the agent followed correct reasoning for Scenario 1."""
        steps = result.get('steps', [])
        validation = {
            'used_get_merchant_status': False,
            'identified_long_delay': False,
            'notified_customer': False,
            'considered_rerouting': False,
            'followed_logical_sequence': False,
            'completed_successfully': result.get('done', False)
        }
        
        # Check tool usage
        for step in steps:
            action = step.get('action', {})
            tool_name = action.get('tool_name', '')
            thought = step.get('thought', '').lower()
            observation = step.get('observation', {})
            
            if tool_name == 'get_merchant_status':
                validation['used_get_merchant_status'] = True
                
                # Check if agent identified delay
                if isinstance(observation, dict):
                    prep_time = observation.get('prep_time_mins', 0)
                    if prep_time >= 30:  # Consider 30+ minutes as long delay
                        validation['identified_long_delay'] = True
            
            elif tool_name == 'notify_customer':
                validation['notified_customer'] = True
            
            elif tool_name == 're_route_driver' or 'reroute' in thought or 'alternative' in thought:
                validation['considered_rerouting'] = True
        
        # Check logical sequence (merchant status should come before customer notification)
        merchant_step = None
        customer_step = None
        
        for i, step in enumerate(steps):
            action = step.get('action', {})
            if action.get('tool_name') == 'get_merchant_status' and merchant_step is None:
                merchant_step = i
            elif action.get('tool_name') == 'notify_customer' and customer_step is None:
                customer_step = i
        
        if merchant_step is not None and customer_step is not None:
            validation['followed_logical_sequence'] = merchant_step < customer_step
        elif merchant_step is not None:  # Used merchant status even if didn't notify customer
            validation['followed_logical_sequence'] = True
        
        return validation
    
    def run_scenario_1(self) -> Dict[str, Any]:
        """
        Scenario 1: Overloaded Restaurant
        
        Expected behavior:
        1. Use get_merchant_status to check restaurant capacity
        2. Identify that 40+ minute delay is too long
        3. Notify customer about the delay
        4. Consider rerouting or finding alternatives
        5. Create comprehensive resolution plan
        """
        print("Running Scenario 1: Overloaded Restaurant...")
        
        problem = "An order is placed at 'Restaurant X', but the kitchen is overloaded."
        
        start_time = time.time()
        try:
            result = run_agent(problem)
            execution_time = time.time() - start_time
            
            # Print chain of thought
            self.print_chain_of_thought(result, "Overloaded Restaurant")
            
            # Validate reasoning
            validation = self.validate_scenario_1_reasoning(result)
            
            print(f"\nVALIDATION RESULTS:")
            print("-" * 30)
            for criteria, passed in validation.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {criteria}: {status}")
            
            success_rate = sum(validation.values()) / len(validation)
            print(f"\nOVERALL SUCCESS RATE: {success_rate:.1%}")
            print(f"EXECUTION TIME: {execution_time:.2f} seconds")
            
            # Store results
            scenario_result = {
                'scenario': 'Overloaded Restaurant',
                'problem': problem,
                'result': result,
                'validation': validation,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            self.results['scenario_1'] = scenario_result
            return scenario_result
            
        except Exception as e:
            error_result = {
                'scenario': 'Overloaded Restaurant',
                'problem': problem,
                'error': str(e),
                'success_rate': 0.0,
                'execution_time': time.time() - start_time
            }
            self.results['scenario_1'] = error_result
            print(f"\nERROR running scenario: {e}")
            return error_result
    
    def run_scenario_2(self) -> Dict[str, Any]:
        """
        Scenario 2: Damaged Packaging Dispute
        
        Expected behavior:
        1. Collect evidence from customer and driver
        2. Analyze evidence to determine fault
        3. Based on analysis, take appropriate action:
           - If merchant fault: issue refund + exonerate driver
           - If driver fault: compensate customer, no exoneration
           - If unclear: issue partial refund for customer satisfaction
        4. Notify relevant parties of resolution
        5. Create comprehensive resolution plan
        """
        print("Running Scenario 2: Damaged Packaging Dispute...")
        
        problem = "A customer reports that their order from 'Pasta Palace' arrived with damaged packaging and some food items were spilled. The customer is requesting a full refund and claims the driver was careless. The driver denies fault and says the packaging was already damaged when picked up from the restaurant."
        
        start_time = time.time()
        try:
            result = run_agent(problem)
            execution_time = time.time() - start_time
            
            # Print chain of thought
            self.print_chain_of_thought(result, "Damaged Packaging Dispute")
            
            # Validate reasoning
            validation = self.validate_scenario_2_reasoning(result)
            
            print(f"\nVALIDATION RESULTS:")
            print("-" * 30)
            for criteria, passed in validation.items():
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {criteria}: {status}")
            
            success_rate = sum(validation.values()) / len(validation)
            print(f"\nOVERALL SUCCESS RATE: {success_rate:.1%}")
            print(f"EXECUTION TIME: {execution_time:.2f} seconds")
            
            # Store results
            scenario_result = {
                'scenario': 'Damaged Packaging Dispute',
                'problem': problem,
                'result': result,
                'validation': validation,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            self.results['scenario_2'] = scenario_result
            return scenario_result
            
        except Exception as e:
            error_result = {
                'scenario': 'Damaged Packaging Dispute',
                'problem': problem,
                'error': str(e),
                'success_rate': 0.0,
                'execution_time': time.time() - start_time
            }
            self.results['scenario_2'] = error_result
            print(f"\nERROR running scenario: {e}")
            return error_result
    
    def run_all_scenarios(self):
        """Run all available scenarios."""
        print("Starting Synapse Agent Scenario Testing")
        print("=" * 50)
        
        # Run Scenario 1
        self.run_scenario_1()
        
        # Run Scenario 2  
        self.run_scenario_2()
        
        # Summary
        print(f"\n{'=' * 50}")
        print("TESTING SUMMARY")
        print("=" * 50)
        
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results.values() if r.get('success_rate', 0) > 0.7)
        
        print(f"Total Scenarios: {total_scenarios}")
        print(f"Successful Scenarios: {successful_scenarios}")
        print(f"Overall Success Rate: {successful_scenarios/total_scenarios:.1%}" if total_scenarios > 0 else "No scenarios completed")
        
        # Detailed results
        for scenario_id, result in self.results.items():
            scenario_name = result.get('scenario', scenario_id)
            success_rate = result.get('success_rate', 0)
            status = "✓ PASS" if success_rate > 0.7 else "✗ FAIL"
            print(f"  {scenario_name}: {success_rate:.1%} {status}")


def test_scenario_1_interactive():
    """Interactive test for Scenario 1 with detailed output."""
    tester = ScenarioTester()
    result = tester.run_scenario_1()
    
    # Ask for follow-up analysis
    print(f"\n{'=' * 60}")
    print("INTERACTIVE ANALYSIS")
    print("=" * 60)
    
    validation = result.get('validation', {})
    
    if not validation.get('used_get_merchant_status'):
        print("❌ ISSUE: Agent didn't check merchant status first")
        print("   RECOMMENDATION: Ensure system prompt emphasizes checking restaurant capacity early")
    
    if not validation.get('identified_long_delay'):
        print("❌ ISSUE: Agent didn't identify the delay as problematic")
        print("   RECOMMENDATION: Set clear thresholds for acceptable delays in system prompt")
    
    if not validation.get('notified_customer'):
        print("❌ ISSUE: Agent didn't proactively notify customer")
        print("   RECOMMENDATION: Emphasize customer communication in system prompt")
    
    if not validation.get('considered_rerouting'):
        print("❌ ISSUE: Agent didn't consider alternative solutions")
        print("   RECOMMENDATION: Add guidance for exploring alternatives when delays are long")
    
    if validation.get('success_rate', 0) > 0.8:
        print("✅ EXCELLENT: Agent demonstrated strong reasoning capabilities!")
    elif validation.get('success_rate', 0) > 0.6:
        print("⚠️  GOOD: Agent performed well with minor areas for improvement")
    else:
        print("❌ NEEDS WORK: Agent reasoning needs significant improvement")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            test_scenario_1_interactive()
        elif sys.argv[1] == "--scenario-1":
            tester = ScenarioTester()
            tester.run_scenario_1()
        elif sys.argv[1] == "--scenario-2":
            tester = ScenarioTester()
            tester.run_scenario_2()
        else:
            print("Usage:")
            print("  python test_scenarios.py                # Run all scenarios")
            print("  python test_scenarios.py --interactive  # Interactive Scenario 1")
            print("  python test_scenarios.py --scenario-1   # Just Scenario 1")
            print("  python test_scenarios.py --scenario-2   # Just Scenario 2")
    else:
        # Default: run all scenarios
        tester = ScenarioTester()
        tester.run_all_scenarios()