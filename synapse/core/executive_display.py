"""
Executive Mode Display Module for Synapse Agent (Windows Compatible)

Provides rich, real-time performance visualization for executive demonstrations
and high-level monitoring of the Synapse logistics coordination agent.
"""

import time
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import threading

# Detect platform for proper rendering
IS_WINDOWS = sys.platform == "win32"

# Configure proper encoding for Windows
if IS_WINDOWS:
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, SIMPLE, SQUARE
from rich.syntax import Syntax


class ExecutiveDisplay:
    """
    Rich executive display for real-time performance metrics visualization.
    Provides a dashboard-like interface showing query processing, tool execution,
    and performance analytics in real-time.
    """
    
    def __init__(self):
        # Initialize console with proper encoding
        self.console = Console(force_terminal=True if IS_WINDOWS else None)
        self.layout = Layout()
        self.live = None
        self.active = False
        
        # Use simpler box styles for Windows compatibility
        self.box_style = SIMPLE if IS_WINDOWS else ROUNDED
        
        # Performance tracking
        self.current_metrics = {}
        self.tool_timeline = deque(maxlen=20)
        self.response_times = deque(maxlen=50)
        self.reflection_events = []
        
        # Progress tracking
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        )
        
        # Initialize layout structure
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup the dashboard layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=4)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        self.layout["left"].split_column(
            Layout(name="query_info", size=8),
            Layout(name="tool_execution", size=12),
            Layout(name="timeline")
        )
        
        self.layout["right"].split_column(
            Layout(name="metrics", size=15),
            Layout(name="reflection")
        )
    
    def start(self):
        """Start the executive display."""
        self.active = True
        self.live = Live(self.layout, refresh_per_second=4, console=self.console)  # Increased refresh rate
        self.live.start()
        self._update_display()
    
    def stop(self):
        """Stop the executive display."""
        self.active = False
        if self.live:
            self.live.stop()
    
    def _get_icon(self, icon_name: str) -> str:
        """Get platform-appropriate icon or fallback."""
        icons = {
            "rocket": "[*]" if IS_WINDOWS else "🚀",
            "chart": "[i]" if IS_WINDOWS else "📊",
            "tool": "[T]" if IS_WINDOWS else "🔧",
            "check": "[v]" if IS_WINDOWS else "✅",
            "cross": "[x]" if IS_WINDOWS else "❌",
            "running": "[~]" if IS_WINDOWS else "🔄",
            "pending": "[.]" if IS_WINDOWS else "⏳",
            "question": "[?]" if IS_WINDOWS else "❓",
            "money": "[$]" if IS_WINDOWS else "💰",
            "chart_up": "[^]" if IS_WINDOWS else "📈",
            "think": "[o]" if IS_WINDOWS else "🤔",
            "clock": "[c]" if IS_WINDOWS else "⏱️",
            "target": "[>]" if IS_WINDOWS else "🎯"
        }
        return icons.get(icon_name, icon_name)
    
    def _create_header(self) -> Panel:
        """Create the header panel."""
        header_text = Text()
        header_text.append(f"{self._get_icon('rocket')} SYNAPSE EXECUTIVE DASHBOARD", style="bold cyan")
        header_text.append(" | ", style="dim")
        header_text.append("Real-Time Performance Monitoring", style="italic")
        header_text.append(" | ", style="dim")
        header_text.append(datetime.now().strftime("%H:%M:%S"), style="green")
        
        return Panel(
            Align.center(header_text),
            box=self.box_style,
            style="on navy_blue" if not IS_WINDOWS else "cyan"
        )
    
    def _create_query_info(self) -> Panel:
        """Create query information panel."""
        # Get live data from performance tracker
        from synapse.core.performance_tracker import PerformanceTracker
        tracker = PerformanceTracker()
        
        if tracker.current_query:
            table = Table(show_header=False, box=None, padding=0)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Query ID:", tracker.current_query.query_id)
            table.add_row("Scenario:", tracker.current_query.scenario_type)
            
            # Calculate elapsed time
            import time
            elapsed = time.time() - tracker.current_query.start_time
            table.add_row("Elapsed Time:", f"{elapsed:.2f}s")
            
            table.add_row("Steps Completed:", str(tracker.current_query.total_steps))
            table.add_row("Complexity Score:", self._get_complexity_bar_from_tracker(tracker))
            
            content = table
        elif self.current_metrics:
            table = Table(show_header=False, box=None, padding=0)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Query ID:", self.current_metrics.get("query_id", "N/A"))
            table.add_row("Scenario:", self.current_metrics.get("scenario_type", "N/A"))
            table.add_row("Elapsed Time:", f"{self.current_metrics.get('elapsed_time', 0):.2f}s")
            table.add_row("Steps Completed:", str(self.current_metrics.get("steps_completed", 0)))
            table.add_row("Complexity Score:", self._get_complexity_bar())
            
            content = table
        else:
            content = Text(f"{self._get_icon('running')} Initializing agent...", style="dim italic")
        
        return Panel(
            content,
            title=f"[bold]{self._get_icon('chart')} Current Query[/bold]",
            box=self.box_style,
            style="cyan"
        )
    
    def _create_tool_execution(self) -> Panel:
        """Create tool execution timeline panel."""
        table = Table(show_header=True, box=self.box_style)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Tool", style="cyan", width=25)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=8)
        
        if self.tool_timeline:
            for tool in list(self.tool_timeline)[-5:]:  # Show last 5 tools
                status_icon = {
                    "running": self._get_icon("running"),
                    "success": self._get_icon("check"),
                    "failed": self._get_icon("cross"),
                    "pending": self._get_icon("pending")
                }.get(tool.get("status", "pending"), self._get_icon("question"))
                
                table.add_row(
                    tool.get("time", ""),
                    tool.get("name", ""),
                    status_icon,
                    f"{tool.get('duration', 0):.2f}s" if tool.get("duration") else "-"
                )
        else:
            table.add_row("", "No tools executed yet", "", "")
        
        return Panel(
            table,
            title=f"[bold]{self._get_icon('tool')} Tool Execution Timeline[/bold]",
            box=self.box_style,
            style="green"
        )
    
    def _create_performance_metrics(self) -> Panel:
        """Create performance metrics panel."""
        metrics_text = Text()
        
        # Get live data from performance tracker
        from synapse.core.performance_tracker import PerformanceTracker
        tracker = PerformanceTracker()
        
        if tracker.current_query:
            # Response time from actual LLM calls
            if tracker.current_query.avg_llm_response_time > 0:
                metrics_text.append(f"Avg Response: {tracker.current_query.avg_llm_response_time:.2f}s\n", style="bold")
            
            # Tool efficiency
            metrics_text.append(f"\n{self._get_icon('chart_up')} Efficiency Metrics:\n", style="bold yellow")
            metrics_text.append(f"• Parallel Saves: ", style="dim")
            metrics_text.append(f"{tracker.current_query.time_saved_by_parallelization:.1f}s\n", style="green")
            
            metrics_text.append(f"• Active Tools: ", style="dim")
            metrics_text.append(f"{len(tracker.active_tools)}\n", style="cyan")
            
            metrics_text.append(f"• Reflections: ", style="dim")
            reflection_count = tracker.current_query.reflection_steps
            style = "red" if reflection_count > 2 else "yellow" if reflection_count > 0 else "green"
            metrics_text.append(f"{reflection_count}\n", style=style)
            
            # Cost tracking - REAL VALUES FROM TRACKER
            metrics_text.append(f"\n{self._get_icon('money')} Cost Analysis:\n", style="bold yellow")
            metrics_text.append(f"• Est. Cost: ", style="dim")
            metrics_text.append(f"${tracker.current_query.estimated_cost:.4f}\n", style="green")
            
            metrics_text.append(f"• Token Usage: ", style="dim")
            total_tokens = tracker.current_query.total_input_tokens + tracker.current_query.total_output_tokens
            metrics_text.append(f"{total_tokens:,}\n", style="cyan")
        elif self.tool_timeline:
            # Fallback to dashboard internal state during execution
            metrics_text.append(f"\n{self._get_icon('chart_up')} Live Execution:\n", style="bold yellow")
            
            # Count successful vs failed tools
            successful_tools = len([t for t in self.tool_timeline if t.get("status") == "success"])
            failed_tools = len([t for t in self.tool_timeline if t.get("status") == "failed"])
            running_tools = len([t for t in self.tool_timeline if t.get("status") == "running"])
            
            metrics_text.append(f"• Tools Executed: ", style="dim")
            metrics_text.append(f"{len(self.tool_timeline)}\n", style="cyan")
            
            metrics_text.append(f"• Success Rate: ", style="dim")
            if len(self.tool_timeline) > 0:
                success_rate = (successful_tools / len(self.tool_timeline)) * 100
                metrics_text.append(f"{success_rate:.1f}%\n", style="green")
            else:
                metrics_text.append("0%\n", style="dim")
            
            metrics_text.append(f"• Running: ", style="dim")
            metrics_text.append(f"{running_tools}\n", style="yellow")
            
            metrics_text.append(f"• Reflections: ", style="dim")
            reflection_count = len(self.reflection_events)
            style = "red" if reflection_count > 2 else "yellow" if reflection_count > 0 else "green"
            metrics_text.append(f"{reflection_count}\n", style=style)
        else:
            metrics_text.append(f"{self._get_icon('running')} Initializing metrics...", style="dim italic")
        
        return Panel(
            metrics_text,
            title=f"[bold]{self._get_icon('chart')} Performance Metrics[/bold]",
            box=self.box_style,
            style="yellow"
        )
    
    def _create_reflection_panel(self) -> Panel:
        """Create reflection events panel."""
        if not self.reflection_events:
            content = Text(f"No reflections triggered {self._get_icon('check')}", style="green italic")
        else:
            table = Table(show_header=False, box=None)
            table.add_column("Event", style="yellow")
            
            for event in self.reflection_events[-3:]:  # Show last 3 reflections
                table.add_row(f"{self._get_icon('running')} {event['reason']}")
                arrow = "->" if IS_WINDOWS else "→"
                table.add_row(f"   {event['original']} {arrow} {event['alternative']}", style="dim")
                table.add_row("")
            
            content = table
        
        return Panel(
            content,
            title=f"[bold]{self._get_icon('think')} Reflection System[/bold]",
            box=self.box_style,
            style="magenta"
        )
    
    def _create_timeline_visualization(self) -> Panel:
        """Create a visual timeline of execution."""
        # Create ASCII timeline visualization
        timeline_text = Text()
        
        if self.tool_timeline:
            timeline_text.append("Execution Flow:\n\n", style="bold")
            
            # Group timeline entries by unique tool executions (latest status wins)
            unique_tools = {}
            for tool in self.tool_timeline:
                key = f"{tool.get('name', 'Unknown')}_{tool.get('time', '')}"
                unique_tools[key] = tool
            
            for i, (key, tool) in enumerate(list(unique_tools.items())[-10:]):
                # Create visual representation
                if tool.get("parallel"):
                    timeline_text.append("║ ", style="cyan")
                else:
                    timeline_text.append("│ ", style="dim")
                
                # Tool name and status
                status_color = {
                    "success": "green",
                    "failed": "red",
                    "running": "yellow"
                }.get(tool.get("status", "pending"), "dim")
                
                arrow = ">" if IS_WINDOWS else "►"
                timeline_text.append(f"==={arrow} ", style=status_color)
                timeline_text.append(f"{tool.get('name', 'Unknown')[:18]:<18}", style=status_color)
                
                # Duration bar (only show if completed)
                duration = tool.get("duration", 0)
                if duration and duration > 0:
                    bar_length = min(int(duration * 20), 20)  # Scale for visibility
                    bar_char = "#" if IS_WINDOWS else "█"
                    timeline_text.append(" " + bar_char * max(1, bar_length), style=status_color)
                    timeline_text.append(f" {duration:.2f}s", style="dim")
                else:
                    timeline_text.append(" [running...]", style="dim")
                timeline_text.append("\n")
        else:
            timeline_text.append("Waiting for tool execution...", style="dim italic")
        
        return Panel(
            timeline_text,
            title=f"[bold]{self._get_icon('clock')} Execution Timeline[/bold]",
            box=self.box_style,
            style="blue"
        )
    
    def _create_footer(self) -> Panel:
        """Create footer with summary stats."""
        footer_columns = []
        
        # Get live data from performance tracker
        from synapse.core.performance_tracker import PerformanceTracker
        tracker = PerformanceTracker()
        
        # Calculate success rate from tool executions
        if tracker.current_query and tracker.current_query.tool_executions:
            successful_tools = len([t for t in tracker.current_query.tool_executions if t.status == "success"])
            total_tools = len([t for t in tracker.current_query.tool_executions if t.status in ["success", "failed"]])
            success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 0
        elif self.tool_timeline:
            successful_tools = len([t for t in self.tool_timeline if t.get("status") == "success"])
            total_tools = len([t for t in self.tool_timeline if t.get("status") in ["success", "failed"]])
            success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 0
        else:
            success_rate = 0
            
        footer_columns.append(
            Panel(
                Align.center(Text(f"{success_rate:.1f}%", style="bold green")),
                title="Success Rate",
                box=self.box_style
            )
        )
        
        # Calculate average resolution time from completed tools
        if tracker.current_query and tracker.current_query.tool_executions:
            completed_tools = [t for t in tracker.current_query.tool_executions if t.duration and t.duration > 0]
            avg_time = sum(t.duration for t in completed_tools) / len(completed_tools) if completed_tools else 0
        elif self.tool_timeline:
            completed_tools = [t for t in self.tool_timeline if t.get("duration") and t.get("duration") > 0]
            avg_time = sum(t["duration"] for t in completed_tools) / len(completed_tools) if completed_tools else 0
        else:
            avg_time = 0
            
        footer_columns.append(
            Panel(
                Align.center(Text(f"{avg_time:.2f}s", style="bold cyan")),
                title="Avg Resolution",
                box=self.box_style
            )
        )
        
        # Calculate intelligence score based on complexity and success
        if tracker.current_query:
            steps = tracker.current_query.total_steps
            reflections = tracker.current_query.reflection_steps
        else:
            steps = self.current_metrics.get("steps_completed", 0)
            reflections = self.current_metrics.get("reflection_count", 0)
        intelligence = min(10, max(1, steps + (10 - reflections * 2)))
        
        footer_columns.append(
            Panel(
                Align.center(Text(f"{intelligence}/10", style="bold magenta")),
                title="Intelligence Score",
                box=self.box_style
            )
        )
        
        return Panel(
            Columns(footer_columns),
            box=self.box_style,
            style="on grey11" if not IS_WINDOWS else "dim"
        )
    
    def _get_complexity_bar(self) -> Text:
        """Create a visual complexity bar."""
        score = self.current_metrics.get("complexity_score", 0)
        bar = Text()
        
        # Use ASCII characters for Windows
        filled_char = "#" if IS_WINDOWS else "█"
        empty_char = "-" if IS_WINDOWS else "░"
        
        filled = filled_char * score
        empty = empty_char * (10 - score)
        
        if score <= 3:
            bar.append(filled, style="green")
        elif score <= 6:
            bar.append(filled, style="yellow")
        else:
            bar.append(filled, style="red")
        
        bar.append(empty, style="dim")
        bar.append(f" ({score}/10)", style="dim")
        
        return bar
    
    def _get_complexity_bar_from_tracker(self, tracker) -> Text:
        """Create a visual complexity bar from tracker data."""
        if tracker.current_query:
            score = min(10, max(1, tracker.current_query.total_steps + tracker.current_query.reflection_steps))
        else:
            score = 1
            
        bar = Text()
        
        # Use ASCII characters for Windows
        filled_char = "#" if IS_WINDOWS else "█"
        empty_char = "-" if IS_WINDOWS else "░"
        
        filled = filled_char * score
        empty = empty_char * (10 - score)
        
        if score <= 3:
            bar.append(filled, style="green")
        elif score <= 6:
            bar.append(filled, style="yellow")
        else:
            bar.append(filled, style="red")
        
        bar.append(empty, style="dim")
        bar.append(f" ({score}/10)", style="dim")
        
        return bar
    
    def _update_display(self):
        """Update all display panels."""
        if not self.active:
            return
        
        try:
            self.layout["header"].update(self._create_header())
            self.layout["query_info"].update(self._create_query_info())
            self.layout["tool_execution"].update(self._create_tool_execution())
            self.layout["metrics"].update(self._create_performance_metrics())
            self.layout["reflection"].update(self._create_reflection_panel())
            self.layout["timeline"].update(self._create_timeline_visualization())
            self.layout["footer"].update(self._create_footer())
        except Exception as e:
            # Log display update errors for debugging
            import os
            if os.getenv("DEBUG", "false").lower() == "true":
                import traceback
                print(f"Display update error: {e}", file=sys.stderr)
                traceback.print_exc()
            pass
        
        if self.active:
            threading.Timer(0.25, self._update_display).start()  # Faster updates
    
    def _update_display_immediate(self):
        """Force immediate display update without timer."""
        if not self.active:
            return
        
        try:
            self.layout["header"].update(self._create_header())
            self.layout["query_info"].update(self._create_query_info())
            self.layout["tool_execution"].update(self._create_tool_execution())
            self.layout["metrics"].update(self._create_performance_metrics())
            self.layout["reflection"].update(self._create_reflection_panel())
            self.layout["timeline"].update(self._create_timeline_visualization())
            self.layout["footer"].update(self._create_footer())
        except Exception as e:
            # Log display update errors for debugging
            import os
            if os.getenv("DEBUG", "false").lower() == "true":
                import traceback
                print(f"Display update error: {e}", file=sys.stderr)
                traceback.print_exc()
            pass
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update current metrics from performance tracker."""
        self.current_metrics.update(metrics)
        # Force immediate display update when metrics change
        if self.live and self.active:
            self._update_display_immediate()
    
    def add_tool_execution(self, tool_name: str, status: str, duration: Optional[float] = None, parallel: bool = False):
        """Add a tool execution to the timeline."""
        self.tool_timeline.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "name": tool_name,
            "status": status,
            "duration": duration,
            "parallel": parallel
        })
        # Force immediate display update
        if self.live and self.active:
            self._update_display_immediate()
    
    def add_reflection(self, reason: str, original_tool: str, alternative: str):
        """Add a reflection event."""
        self.reflection_events.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": reason[:50],  # Truncate for display
            "original": original_tool,
            "alternative": alternative
        })
        # Force immediate display update
        if self.live and self.active:
            self._update_display_immediate()
    
    def show_final_summary(self, metrics: Dict[str, Any]):
        """Display final execution summary."""
        self.stop()
        
        # Create summary panel
        summary = Table(title=f"{self._get_icon('target')} Execution Summary", box=self.box_style, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="bold")
        
        summary.add_row("Total Duration", f"{metrics.get('total_duration', 0):.2f} seconds")
        summary.add_row("Steps Executed", str(metrics.get('total_steps', 0)))
        summary.add_row("Tools Used", str(metrics.get('tools_used', 0)))
        summary.add_row("Reflections Triggered", str(metrics.get('reflection_count', 0)))
        summary.add_row("Parallelization Savings", f"{metrics.get('time_saved', 0):.2f} seconds")
        summary.add_row("Estimated Cost", metrics.get('estimated_cost', '$0.0000'))
        success_icon = self._get_icon('check') if metrics.get('success') else self._get_icon('cross')
        summary.add_row("Resolution Status", f"{success_icon} Success" if metrics.get('success') else f"{success_icon} Failed")
        
        self.console.print("\n")
        self.console.print(summary)
        self.console.print("\n")


# Global display instance
executive_display = ExecutiveDisplay()