"""
Executive Mode Display Module for Synapse Agent

Provides rich, real-time performance visualization for executive demonstrations
and high-level monitoring of the Synapse logistics coordination agent.
"""

import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED
from rich.syntax import Syntax
import plotext as plt


class ExecutiveDisplay:
    """
    Rich executive display for real-time performance metrics visualization.
    Provides a dashboard-like interface showing query processing, tool execution,
    and performance analytics in real-time.
    """
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.live = None
        self.active = False
        
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
        self.live = Live(self.layout, refresh_per_second=4, console=self.console)
        self.live.start()
        self._update_display()
    
    def stop(self):
        """Stop the executive display."""
        self.active = False
        if self.live:
            self.live.stop()
    
    def _create_header(self) -> Panel:
        """Create the header panel."""
        header_text = Text()
        header_text.append("🚀 SYNAPSE EXECUTIVE DASHBOARD", style="bold cyan")
        header_text.append(" | ", style="dim")
        header_text.append("Real-Time Performance Monitoring", style="italic")
        header_text.append(" | ", style="dim")
        header_text.append(datetime.now().strftime("%H:%M:%S"), style="green")
        
        return Panel(
            Align.center(header_text),
            box=ROUNDED,
            style="on navy_blue"
        )
    
    def _create_query_info(self) -> Panel:
        """Create query information panel."""
        if not self.current_metrics:
            content = Text("Awaiting query...", style="dim italic")
        else:
            table = Table(show_header=False, box=None, padding=0)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Query ID:", self.current_metrics.get("query_id", "N/A"))
            table.add_row("Scenario:", self.current_metrics.get("scenario_type", "N/A"))
            table.add_row("Elapsed Time:", f"{self.current_metrics.get('elapsed_time', 0):.2f}s")
            table.add_row("Steps Completed:", str(self.current_metrics.get("steps_completed", 0)))
            table.add_row("Complexity Score:", self._get_complexity_bar())
            
            content = table
        
        return Panel(
            content,
            title="[bold]📊 Current Query[/bold]",
            box=ROUNDED,
            style="cyan"
        )
    
    def _create_tool_execution(self) -> Panel:
        """Create tool execution timeline panel."""
        table = Table(show_header=True, box=ROUNDED)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Tool", style="cyan", width=25)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=8)
        
        for tool in list(self.tool_timeline)[-5:]:  # Show last 5 tools
            status_icon = {
                "running": "🔄",
                "success": "✅",
                "failed": "❌",
                "pending": "⏳"
            }.get(tool.get("status", "pending"), "❓")
            
            table.add_row(
                tool.get("time", ""),
                tool.get("name", ""),
                status_icon,
                f"{tool.get('duration', 0):.2f}s" if tool.get("duration") else "-"
            )
        
        return Panel(
            table,
            title="[bold]🔧 Tool Execution Timeline[/bold]",
            box=ROUNDED,
            style="green"
        )
    
    def _create_performance_metrics(self) -> Panel:
        """Create performance metrics panel."""
        metrics_text = Text()
        
        if self.current_metrics:
            # Response time chart
            if self.response_times:
                avg_response = sum(self.response_times) / len(self.response_times)
                metrics_text.append(f"Avg Response: {avg_response:.2f}s\n", style="bold")
            
            # Tool efficiency
            metrics_text.append("\n📈 Efficiency Metrics:\n", style="bold yellow")
            metrics_text.append(f"• Parallel Saves: ", style="dim")
            metrics_text.append(f"{self.current_metrics.get('time_saved', 0):.1f}s\n", style="green")
            
            metrics_text.append(f"• Active Tools: ", style="dim")
            metrics_text.append(f"{self.current_metrics.get('active_tools', 0)}\n", style="cyan")
            
            metrics_text.append(f"• Reflections: ", style="dim")
            reflection_count = self.current_metrics.get('reflection_count', 0)
            style = "red" if reflection_count > 2 else "yellow" if reflection_count > 0 else "green"
            metrics_text.append(f"{reflection_count}\n", style=style)
            
            # Cost tracking
            metrics_text.append("\n💰 Cost Analysis:\n", style="bold yellow")
            metrics_text.append(f"• Est. Cost: ", style="dim")
            metrics_text.append(f"{self.current_metrics.get('estimated_cost', '$0.0000')}\n", style="green")
            
            metrics_text.append(f"• Token Usage: ", style="dim")
            metrics_text.append(f"{self.current_metrics.get('total_tokens', 0):,}\n", style="cyan")
        else:
            metrics_text.append("No active metrics", style="dim italic")
        
        return Panel(
            metrics_text,
            title="[bold]📊 Performance Metrics[/bold]",
            box=ROUNDED,
            style="yellow"
        )
    
    def _create_reflection_panel(self) -> Panel:
        """Create reflection events panel."""
        if not self.reflection_events:
            content = Text("No reflections triggered ✅", style="green italic")
        else:
            table = Table(show_header=False, box=None)
            table.add_column("Event", style="yellow")
            
            for event in self.reflection_events[-3:]:  # Show last 3 reflections
                table.add_row(f"🔄 {event['reason']}")
                table.add_row(f"   {event['original']} → {event['alternative']}", style="dim")
                table.add_row("")
            
            content = table
        
        return Panel(
            content,
            title="[bold]🤔 Reflection System[/bold]",
            box=ROUNDED,
            style="magenta"
        )
    
    def _create_timeline_visualization(self) -> Panel:
        """Create a visual timeline of execution."""
        # Create ASCII timeline visualization
        timeline_text = Text()
        
        if self.tool_timeline:
            timeline_text.append("Execution Flow:\n\n", style="bold")
            
            for i, tool in enumerate(list(self.tool_timeline)[-10:]):
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
                
                timeline_text.append(f"{'═' * 3}► ", style=status_color)
                timeline_text.append(f"{tool.get('name', 'Unknown')[:20]:<20}", style=status_color)
                
                # Duration bar
                duration = tool.get("duration", 0)
                bar_length = min(int(duration * 10), 30)
                timeline_text.append(" " + "█" * bar_length, style=status_color)
                timeline_text.append(f" {duration:.2f}s\n", style="dim")
        else:
            timeline_text.append("No execution history yet", style="dim italic")
        
        return Panel(
            timeline_text,
            title="[bold]⏱️ Execution Timeline[/bold]",
            box=ROUNDED,
            style="blue"
        )
    
    def _create_footer(self) -> Panel:
        """Create footer with summary stats."""
        footer_columns = []
        
        # Success rate
        success_rate = self.current_metrics.get("success_rate", 0)
        footer_columns.append(
            Panel(
                Align.center(Text(f"{success_rate:.1f}%", style="bold green")),
                title="Success Rate",
                box=ROUNDED
            )
        )
        
        # Average time
        avg_time = self.current_metrics.get("avg_resolution_time", 0)
        footer_columns.append(
            Panel(
                Align.center(Text(f"{avg_time:.2f}s", style="bold cyan")),
                title="Avg Resolution",
                box=ROUNDED
            )
        )
        
        # Intelligence score
        intelligence = self.current_metrics.get("intelligence_score", 0)
        footer_columns.append(
            Panel(
                Align.center(Text(f"{intelligence}/10", style="bold magenta")),
                title="Intelligence Score",
                box=ROUNDED
            )
        )
        
        return Panel(
            Columns(footer_columns),
            box=ROUNDED,
            style="on grey11"
        )
    
    def _get_complexity_bar(self) -> Text:
        """Create a visual complexity bar."""
        score = self.current_metrics.get("complexity_score", 0)
        bar = Text()
        
        filled = "█" * score
        empty = "░" * (10 - score)
        
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
            # Fail silently to not interrupt agent execution
            pass
        
        if self.active:
            threading.Timer(0.5, self._update_display).start()
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update current metrics from performance tracker."""
        self.current_metrics.update(metrics)
    
    def add_tool_execution(self, tool_name: str, status: str, duration: Optional[float] = None, parallel: bool = False):
        """Add a tool execution to the timeline."""
        self.tool_timeline.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "name": tool_name,
            "status": status,
            "duration": duration,
            "parallel": parallel
        })
    
    def add_reflection(self, reason: str, original_tool: str, alternative: str):
        """Add a reflection event."""
        self.reflection_events.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "reason": reason[:50],  # Truncate for display
            "original": original_tool,
            "alternative": alternative
        })
    
    def show_final_summary(self, metrics: Dict[str, Any]):
        """Display final execution summary."""
        self.stop()
        
        # Create summary panel
        summary = Table(title="🎯 Execution Summary", box=ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="bold")
        
        summary.add_row("Total Duration", f"{metrics.get('total_duration', 0):.2f} seconds")
        summary.add_row("Steps Executed", str(metrics.get('total_steps', 0)))
        summary.add_row("Tools Used", str(metrics.get('tools_used', 0)))
        summary.add_row("Reflections Triggered", str(metrics.get('reflection_count', 0)))
        summary.add_row("Parallelization Savings", f"{metrics.get('time_saved', 0):.2f} seconds")
        summary.add_row("Estimated Cost", metrics.get('estimated_cost', '$0.0000'))
        summary.add_row("Resolution Status", "✅ Success" if metrics.get('success') else "❌ Failed")
        
        self.console.print("\n")
        self.console.print(summary)
        self.console.print("\n")


# Global display instance
executive_display = ExecutiveDisplay()