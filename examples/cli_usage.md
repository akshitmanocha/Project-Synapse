# Command-Line Interface Usage Examples

## Basic Usage

### Direct Problem Input
```bash
python main.py "A driver is at the customer's location, but the recipient is not available to receive a valuable package."
```

### Using Predefined Scenarios
```bash
# Use scenario 2.4 (recipient unavailable)
python main.py --scenario 2.4

# Use traffic scenario with verbose output
python main.py --scenario traffic --verbose
```

### Different Output Modes
```bash
# Verbose mode - shows detailed observations and tool parameters
python main.py --verbose "Package damaged, customer disputes fault"

# Quiet mode - only shows final resolution plan
python main.py --quiet "Driver stuck in traffic"

# No banner mode - clean output without banner
python main.py --no-banner "Merchant equipment breakdown"
```

## Utility Commands

### List Available Scenarios
```bash
python main.py --list-scenarios
```

Output:
```
📋 AVAILABLE PREDEFINED SCENARIOS
========================================
🎯 1.0: Restaurant is overloaded and cannot fulfill the order within the expected time frame
🎯 2.0: Package arrived damaged and the customer disputes who is at fault
🎯 2.2: Item is out of stock and needs to be replaced with customer's preferred alternative
🎯 2.3: Driver is at the customer's location but there's a dispute about the order at the door
🎯 2.4: A driver is at the customer's location, but the recipient is not available to receive a valuable package
🎯 traffic: Driver stuck in heavy traffic, 45-minute delay expected for customer order
🎯 merchant: Merchant's kitchen equipment broke down, cannot prepare the order
🎯 weather: Severe weather conditions preventing safe delivery completion
```

### Show Available Tools
```bash
python main.py --debug-tools
```

## Using the Installed Command

After installing with `pip install -e .`, you can use the `synapse-agent` command:

```bash
# All the same options work
synapse-agent "Driver stuck in traffic for 45 minutes"
synapse-agent --scenario 2.4 --verbose
synapse-agent --list-scenarios
```

## Example Output

Running:
```bash
python main.py "A driver is at the customer's location, but the recipient is not available to receive a valuable package."
```

Produces:
```
🚀 ============================================================ 🚀
    SYNAPSE AGENT - Autonomous Logistics Coordination
    Advanced Problem-Solving with Reflection & Adaptation
🚀 ============================================================ 🚀

🎯 Problem: A driver is at the customer's location, but the recipient is not available to receive a valuable package.

🚀 Starting Synapse Agent...
⏰ Time: 2025-09-01 00:07:33

🧠 AGENT CHAIN OF THOUGHT
==================================================

📍 Step 1: 🛠️  ACTION
------------------------------
💭 Thought: I need to contact the recipient first to see if they can receive the package
🔧 Tool: contact_recipient_via_chat
✅ Result: {'contact_successful': False}

📍 Step 2: 🤔 REASONING
------------------------------
💭 Thought: Contact failed - I need an alternative approach for this valuable package
🔧 Tool: reflect

📍 Step 3: 🛠️  ACTION  
------------------------------
💭 Thought: Since this is a valuable package, I should suggest a safe drop-off location
🔧 Tool: suggest_safe_drop_off
✅ Result: {'safe_option_available': True, 'location': 'Building concierge'}

⏰ Execution completed in 2.34 seconds

🎯 FINAL RESOLUTION PLAN
==================================================
📋 Plan: Coordinate with building concierge for secure package storage. Driver will leave valuable package with concierge who will hold it securely until recipient can collect. Send notification to recipient with pickup details and concierge contact information.

📊 Execution Summary:
   • Total steps: 3
   • Completed: ✅ Yes
   • Adaptations: ✅ Yes
   • Last reflection: Contact failed - need alternative delivery approach

✅ Agent successfully resolved the logistics problem!
```

## Help Output

```bash
python main.py --help
```

```
usage: main.py [-h] [--scenario SCENARIO] [--list-scenarios] [--verbose]
               [--quiet] [--no-banner] [--debug-tools]
               [problem]

Synapse Agent - Autonomous Logistics Coordination Platform

positional arguments:
  problem               Logistics problem description to solve

options:
  -h, --help            show this help message and exit
  --scenario SCENARIO, -s SCENARIO
                        Use a predefined scenario (1.0, 2.0, 2.2, 2.3, 2.4,
                        traffic, merchant, weather)
  --list-scenarios, -l  List all predefined scenarios
  --verbose, -v         Show detailed observations and tool parameters
  --quiet, -q           Only show final resolution plan
  --no-banner           Don't show the banner
  --debug-tools         Show available tools and their metadata

Examples:
    main.py "Driver stuck in traffic for 45 minutes"
    main.py --verbose "Package damaged, customer disputes fault"
    main.py --scenario 2.4
    main.py --scenario traffic --verbose
    main.py --list-scenarios
```