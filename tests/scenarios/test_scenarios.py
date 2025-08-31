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
    
    def validate_scenario_2_3_reasoning(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that the agent followed correct reasoning for Scenario 2.3 (At-Door Dispute)."""
        steps = result.get('steps', [])
        validation = {
            'collected_evidence_immediately': False,
            'analyzed_evidence_quickly': False,
            'provided_immediate_resolution': False,
            'protected_or_held_driver_accountable': False,
            'logged_merchant_feedback': False,
            'maintained_professional_relations': False,
            'completed_successfully': result.get('done', False)
        }
        
        evidence_collect_step = None
        evidence_analyze_step = None
        resolution_step = None
        driver_action_step = None
        feedback_step = None
        
        # Check tool usage and sequence for at-door dispute
        for i, step in enumerate(steps):
            action = step.get('action', {})
            tool_name = action.get('tool_name', '')
            thought = step.get('thought', '').lower()
            observation = step.get('observation', {})
            
            if tool_name == 'collect_evidence':
                validation['collected_evidence_immediately'] = True
                evidence_collect_step = i
                
            elif tool_name == 'analyze_evidence':
                validation['analyzed_evidence_quickly'] = True
                evidence_analyze_step = i
                
                # Check if analysis was done promptly after evidence collection
                if evidence_collect_step is not None and i == evidence_collect_step + 1:
                    pass  # Good sequencing
                    
            elif tool_name in ['issue_instant_refund', 'issue_partial_refund']:
                validation['provided_immediate_resolution'] = True
                resolution_step = i
                
            elif tool_name == 'exonerate_driver':
                validation['protected_or_held_driver_accountable'] = True
                driver_action_step = i
                
            elif tool_name == 'log_merchant_packaging_feedback':
                validation['logged_merchant_feedback'] = True
                feedback_step = i
                
            elif tool_name == 'notify_customer':
                # Check for professional communication
                if 'professional' in thought or 'courteous' in thought or 'apologize' in thought:
                    validation['maintained_professional_relations'] = True
        
        # Check urgency - evidence collection should be early
        if evidence_collect_step is not None and evidence_collect_step <= 1:
            pass  # Good urgency
            
        # Check proper sequence for at-door dispute
        sequence_check = True
        if evidence_collect_step is not None and evidence_analyze_step is not None:
            if evidence_analyze_step < evidence_collect_step:
                sequence_check = False
                
        # Resolution should come after analysis
        if evidence_analyze_step is not None and resolution_step is not None:
            if resolution_step < evidence_analyze_step:
                sequence_check = False
                
        # Feedback should be near the end
        if feedback_step is not None and feedback_step < 2:
            sequence_check = False  # Too early for feedback
            
        if not sequence_check:
            validation['completed_successfully'] = False
            
        return validation

    def validate_scenario_2_2_reasoning(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that the agent followed correct reasoning for Scenario 2.2 (Item Out of Stock)."""
        steps = result.get('steps', [])
        validation = {
            'checked_merchant_status': False,
            'contacted_merchant': False,
            'proposed_substitute': False,
            'notified_customer': False,
            'handled_unavailability': False,  # Either substitute or refund
            'followed_logical_sequence': False,
            'completed_successfully': result.get('done', False)
        }
        
        merchant_step = None
        contact_step = None
        substitute_step = None
        refund_step = None
        notify_step = None
        
        # Check tool usage and sequence
        for i, step in enumerate(steps):
            action = step.get('action', {})
            tool_name = action.get('tool_name', '')
            thought = step.get('thought', '').lower()
            observation = step.get('observation', {})
            
            if tool_name == 'get_merchant_status':
                validation['checked_merchant_status'] = True
                merchant_step = i
                
                # Check if stock issue was identified
                if isinstance(observation, dict):
                    stock = observation.get('stock', {})
                    if isinstance(stock, dict):
                        # Check if any item is out of stock (False value)
                        has_stock_issue = any(not available for available in stock.values())
                        if has_stock_issue:
                            pass  # Stock issue identified
            
            elif tool_name == 'contact_merchant':
                validation['contacted_merchant'] = True
                contact_step = i
            
            elif tool_name == 'propose_substitute':
                validation['proposed_substitute'] = True
                substitute_step = i
                validation['handled_unavailability'] = True
                
            elif tool_name == 'issue_partial_refund':
                refund_step = i
                validation['handled_unavailability'] = True
                
            elif tool_name == 'notify_customer':
                validation['notified_customer'] = True
                notify_step = i
        
        # Check logical sequence (merchant status -> contact -> substitute/refund -> notify)
        sequence_ok = True
        if merchant_step is not None:
            if contact_step is not None and contact_step < merchant_step:
                sequence_ok = False
            if substitute_step is not None and substitute_step < merchant_step:
                sequence_ok = False
            if refund_step is not None and refund_step < merchant_step:
                sequence_ok = False
        
        if contact_step is not None:
            if substitute_step is not None and substitute_step < contact_step:
                sequence_ok = False
            if refund_step is not None and refund_step < contact_step:
                sequence_ok = False
                
        validation['followed_logical_sequence'] = sequence_ok
        
        return validation

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
    
    def validate_scenario_2_4_reasoning(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that the agent followed correct reasoning for Scenario 2.4 (Recipient Unavailable)."""
        steps = result.get('steps', [])
        validation = {
            'contacted_recipient_first': False,
            'attempted_alternative_delivery': False,
            'considered_safe_drop_off_or_locker': False,
            'handled_perishable_urgency': False,
            'minimized_driver_idle_time': False,
            'followed_logical_escalation_sequence': False,
            'completed_successfully': result.get('done', False)
        }
        
        contact_step = None
        safe_dropoff_step = None
        locker_step = None
        redelivery_step = None
        sender_contact_step = None
        
        # Check tool usage and sequence for recipient unavailable scenario
        for i, step in enumerate(steps):
            action = step.get('action', {})
            tool_name = action.get('tool_name', '')
            thought = step.get('thought', '').lower()
            observation = step.get('observation', {})
            
            if tool_name == 'contact_recipient_via_chat':
                validation['contacted_recipient_first'] = True
                contact_step = i
                
            elif tool_name == 'suggest_safe_drop_off':
                validation['considered_safe_drop_off_or_locker'] = True
                safe_dropoff_step = i
                
            elif tool_name == 'find_nearby_locker':
                validation['considered_safe_drop_off_or_locker'] = True
                locker_step = i
                
            elif tool_name == 'schedule_redelivery':
                validation['attempted_alternative_delivery'] = True
                redelivery_step = i
                
            elif tool_name == 'contact_sender':
                sender_contact_step = i
                
            # Check for urgency awareness about perishables
            if 'perishable' in thought or 'temperature' in thought or 'grocery' in thought or 'urgent' in thought:
                validation['handled_perishable_urgency'] = True
                
            # Check for driver efficiency considerations
            if 'driver' in thought and ('idle' in thought or 'waiting' in thought or 'reassign' in thought or 'efficient' in thought):
                validation['minimized_driver_idle_time'] = True
        
        # Check logical escalation sequence: Contact → Safe Drop-off/Locker → Redelivery → Sender
        sequence_valid = True
        
        # Contact should be first
        if contact_step is not None and contact_step > 0:
            # Contact should be early but not necessarily first
            pass
            
        # Safe drop-off or locker should come after contact attempt
        if contact_step is not None and (safe_dropoff_step is not None or locker_step is not None):
            earliest_alternative = min(x for x in [safe_dropoff_step, locker_step] if x is not None)
            if earliest_alternative <= contact_step:
                sequence_valid = False
                
        # Redelivery should be after other attempts
        if redelivery_step is not None:
            earlier_steps = [x for x in [contact_step, safe_dropoff_step, locker_step] if x is not None]
            if earlier_steps and redelivery_step <= max(earlier_steps):
                sequence_valid = False
                
        # Sender contact should be last resort
        if sender_contact_step is not None:
            earlier_steps = [x for x in [contact_step, safe_dropoff_step, locker_step, redelivery_step] if x is not None]
            if earlier_steps and sender_contact_step <= max(earlier_steps):
                sequence_valid = False
        
        validation['followed_logical_escalation_sequence'] = sequence_valid
        
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
    
    def run_scenario_2_2(self) -> Dict[str, Any]:
        """
        Scenario 2.2: Item Out of Stock
        
        Expected behavior:
        1. Check merchant status to identify stock issues
        2. Contact merchant to confirm stock availability
        3. Propose substitute items to customer
        4. If substitutes declined or unavailable, issue partial refund
        5. Notify customer of resolution
        6. Create comprehensive resolution plan
        """
        print("Running Scenario 2.2: Item Out of Stock...")
        
        problem = "A customer ordered a Margherita pizza, garlic bread, and Coke from 'Mario's Pizzeria'. The restaurant just called to say they are out of garlic bread and their Coke machine is broken. The customer is asking what alternatives are available."
        
        start_time = time.time()
        try:
            result = run_agent(problem)
            execution_time = time.time() - start_time
            
            # Print chain of thought
            self.print_chain_of_thought(result, "Item Out of Stock")
            
            # Validate reasoning
            validation = self.validate_scenario_2_2_reasoning(result)
            
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
                'scenario': 'Item Out of Stock',
                'problem': problem,
                'result': result,
                'validation': validation,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            self.results['scenario_2_2'] = scenario_result
            return scenario_result
            
        except Exception as e:
            error_result = {
                'scenario': 'Item Out of Stock',
                'problem': problem,
                'error': str(e),
                'success_rate': 0.0,
                'execution_time': time.time() - start_time
            }
            self.results['scenario_2_2'] = error_result
            print(f"\nERROR running scenario: {e}")
            return error_result
    
    def run_scenario_2_3(self) -> Dict[str, Any]:
        """
        Scenario 2.3: At-Door Dispute Over Damaged Item
        
        Expected behavior:
        1. Immediately collect evidence from both customer and driver
        2. Rapidly analyze evidence to determine fault while parties present
        3. Provide on-spot resolution (refund if customer not at fault)
        4. Exonerate driver or hold accountable based on evidence
        5. Log merchant packaging feedback to prevent future issues
        6. Maintain professional relationships throughout process
        """
        print("Running Scenario 2.3: At-Door Dispute Over Damaged Item...")
        
        problem = "A driver has just arrived at the customer's door with their order from 'Bella's Bistro'. Upon opening the bag, the customer discovers that the pasta container has leaked and the food is spilled inside the bag. The customer is upset and claiming the driver was careless. The driver insists the bag was already damaged when they picked it up from the restaurant. Both parties are at the door and the situation is tense."
        
        start_time = time.time()
        try:
            result = run_agent(problem)
            execution_time = time.time() - start_time
            
            # Print chain of thought
            self.print_chain_of_thought(result, "At-Door Dispute Over Damaged Item")
            
            # Validate reasoning
            validation = self.validate_scenario_2_3_reasoning(result)
            
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
                'scenario': 'At-Door Dispute Over Damaged Item',
                'problem': problem,
                'result': result,
                'validation': validation,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            self.results['scenario_2_3'] = scenario_result
            return scenario_result
            
        except Exception as e:
            error_result = {
                'scenario': 'At-Door Dispute Over Damaged Item',
                'problem': problem,
                'error': str(e),
                'success_rate': 0.0,
                'execution_time': time.time() - start_time
            }
            self.results['scenario_2_3'] = error_result
            print(f"\nERROR running scenario: {e}")
            return error_result
    
    def run_scenario_2_4(self) -> Dict[str, Any]:
        """Test Scenario 2.4: Recipient Unavailable at Delivery Address"""
        try:
            problem = (
                "The driver has arrived at the delivery destination with an order from 'QuickMart Express', "
                "but the recipient is not available to receive the package. The driver has been waiting "
                "for 5 minutes at the address. The package contains perishable groceries that need "
                "temperature-controlled storage. The recipient's apartment building has no doorman "
                "and no secure lobby area for safe drop-off."
            )
            
            print("\n" + "="*60)
            print("SCENARIO: Recipient Unavailable at Delivery Address")
            print("="*60)
            print(f"\nINPUT PROBLEM:\n  {problem}")
            
            start_time = time.time()
            
            # Run agent
            result = self.run_agent_with_problem(problem)
            
            execution_time = time.time() - start_time
            
            # Display chain of thought
            self.display_chain_of_thought(result)
            
            # Display final plan
            print(f"\nFINAL PLAN:")
            print(f"  {result.get('plan', 'No plan generated')}")
            
            print(f"\nCOMPLETED: {result.get('done', False)}")
            print("="*60)
            
            # Validate reasoning
            validation = self.validate_scenario_2_4_reasoning(result)
            
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
                'scenario': 'Recipient Unavailable at Delivery Address',
                'problem': problem,
                'result': result,
                'validation': validation,
                'success_rate': success_rate,
                'execution_time': execution_time
            }
            
            self.results['scenario_2_4'] = scenario_result
            return scenario_result
            
        except Exception as e:
            error_result = {
                'scenario': 'Recipient Unavailable at Delivery Address',
                'problem': problem,
                'error': str(e),
                'success_rate': 0.0,
                'execution_time': time.time() - start_time
            }
            self.results['scenario_2_4'] = error_result
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
        
        # Run Scenario 2.2
        self.run_scenario_2_2()
        
        # Run Scenario 2.3
        self.run_scenario_2_3()
        
        # Run Scenario 2.4
        self.run_scenario_2_4()
        
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
        elif sys.argv[1] == "--scenario-2.2":
            tester = ScenarioTester()
            tester.run_scenario_2_2()
        elif sys.argv[1] == "--scenario-2.3":
            tester = ScenarioTester()
            tester.run_scenario_2_3()
        elif sys.argv[1] == "--scenario-2.4":
            tester = ScenarioTester()
            tester.run_scenario_2_4()
        else:
            print("Usage:")
            print("  python test_scenarios.py                 # Run all scenarios")
            print("  python test_scenarios.py --interactive   # Interactive Scenario 1")
            print("  python test_scenarios.py --scenario-1    # Just Scenario 1")
            print("  python test_scenarios.py --scenario-2    # Just Scenario 2")
            print("  python test_scenarios.py --scenario-2.2  # Just Scenario 2.2")
            print("  python test_scenarios.py --scenario-2.3  # Just Scenario 2.3")
            print("  python test_scenarios.py --scenario-2.4  # Just Scenario 2.4")
    else:
        # Default: run all scenarios
        tester = ScenarioTester()
        tester.run_all_scenarios()