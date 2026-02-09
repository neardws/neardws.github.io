"""Report generation commands."""
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from src.db.connection import get_connection, db_exists
from src.config import RATES_FILE, load_rates, calculate_cost


console = Console()


def _format_tokens(count: int) -> str:
    """Format token count with K/M suffix."""
    if count is None:
        return "0"
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count/1_000:.1f}K"
    return str(count)


def _get_date_range(range_type: str) -> tuple[str, str, str]:
    """Get date filter SQL, start date, and title based on range type."""
    today = datetime.now().date()
    
    if range_type == "daily":
        return (
            "date(u.recorded_at) = date('now')",
            str(today),
            f"Daily Report - {today.strftime('%Y-%m-%d')}"
        )
    elif range_type == "weekly":
        week_start = today - timedelta(days=today.weekday())
        return (
            f"date(u.recorded_at) >= date('{week_start}')",
            str(week_start),
            f"Weekly Report - Week {today.strftime('%Y-W%W')} ({week_start} to {today})"
        )
    elif range_type == "monthly":
        month_start = today.replace(day=1)
        return (
            f"date(u.recorded_at) >= date('{month_start}')",
            str(month_start),
            f"Monthly Report - {today.strftime('%Y-%m')}"
        )
    else:
        return ("1=1", "all", "All Time Report")


def generate_daily_report(output_csv: bool = False) -> Optional[str]:
    """Generate daily usage report."""
    if not db_exists():
        console.print("[red]Database not initialized. Run 'tt init' first.[/red]")
        return None
    
    rates = load_rates()
    date_filter, _, title = _get_date_range("daily")
    
    with get_connection() as conn:
        query = f"""
            SELECT 
                date(u.recorded_at) as date,
                s.display_name as source,
                m.display_name as model,
                m.model_id,
                COUNT(*) as requests,
                SUM(u.input_tokens) as input_tokens,
                SUM(u.output_tokens) as output_tokens,
                SUM(u.cache_read_tokens) as cache_read,
                SUM(u.total_tokens) as total_tokens,
                SUM(u.cost_total) as recorded_cost
            FROM usage u
            JOIN models m ON u.model_id = m.id
            JOIN sources s ON u.source_id = s.id
            WHERE {date_filter}
            GROUP BY date(u.recorded_at), s.id, m.id
            ORDER BY date DESC, source, model
        """
        rows = conn.execute(query).fetchall()
    
    if not rows:
        console.print(f"[yellow]No usage data found for today[/yellow]")
        return None
    
    if output_csv:
        return _generate_csv(rows, rates)
    
    _render_report_table(rows, title, rates)
    return None


def generate_weekly_report(output_csv: bool = False) -> Optional[str]:
    """Generate weekly usage report with day-by-day breakdown."""
    if not db_exists():
        console.print("[red]Database not initialized. Run 'tt init' first.[/red]")
        return None
    
    rates = load_rates()
    date_filter, start_date, title = _get_date_range("weekly")
    
    with get_connection() as conn:
        query = f"""
            SELECT 
                date(u.recorded_at) as date,
                s.display_name as source,
                m.display_name as model,
                m.model_id,
                COUNT(*) as requests,
                SUM(u.input_tokens) as input_tokens,
                SUM(u.output_tokens) as output_tokens,
                SUM(u.cache_read_tokens) as cache_read,
                SUM(u.total_tokens) as total_tokens,
                SUM(u.cost_total) as recorded_cost
            FROM usage u
            JOIN models m ON u.model_id = m.id
            JOIN sources s ON u.source_id = s.id
            WHERE {date_filter}
            GROUP BY date(u.recorded_at), s.id, m.id
            ORDER BY date DESC, source, model
        """
        rows = conn.execute(query).fetchall()
        
        summary_query = f"""
            SELECT 
                date(u.recorded_at) as date,
                COUNT(*) as requests,
                SUM(u.input_tokens) as input_tokens,
                SUM(u.output_tokens) as output_tokens,
                SUM(u.cache_read_tokens) as cache_read,
                SUM(u.total_tokens) as total_tokens,
                SUM(u.cost_total) as recorded_cost
            FROM usage u
            WHERE {date_filter}
            GROUP BY date(u.recorded_at)
            ORDER BY date DESC
        """
        summary_rows = conn.execute(summary_query).fetchall()
    
    if not rows:
        console.print(f"[yellow]No usage data found for this week[/yellow]")
        return None
    
    if output_csv:
        return _generate_csv(rows, rates)
    
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
    
    table = Table(title="Daily Summary")
    table.add_column("Date", style="cyan")
    table.add_column("Requests", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache Read", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost", justify="right", style="green")
    
    total_requests = 0
    total_input = 0
    total_output = 0
    total_cache = 0
    total_tokens = 0
    total_cost = 0.0
    
    for row in summary_rows:
        cost = _calculate_row_cost(row, rates, is_summary=True)
        table.add_row(
            row["date"],
            str(row["requests"]),
            _format_tokens(row["input_tokens"] or 0),
            _format_tokens(row["output_tokens"] or 0),
            _format_tokens(row["cache_read"] or 0),
            _format_tokens(row["total_tokens"] or 0),
            f"${cost:.4f}"
        )
        total_requests += row["requests"]
        total_input += row["input_tokens"] or 0
        total_output += row["output_tokens"] or 0
        total_cache += row["cache_read"] or 0
        total_tokens += row["total_tokens"] or 0
        total_cost += cost
    
    table.add_section()
    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{total_requests}[/bold]",
        f"[bold]{_format_tokens(total_input)}[/bold]",
        f"[bold]{_format_tokens(total_output)}[/bold]",
        f"[bold]{_format_tokens(total_cache)}[/bold]",
        f"[bold]{_format_tokens(total_tokens)}[/bold]",
        f"[bold green]${total_cost:.4f}[/bold green]"
    )
    
    console.print(table)
    
    _render_report_table(rows, "Detailed Breakdown", rates)
    return None


def _calculate_row_cost(row, rates: dict, is_summary: bool = False) -> float:
    """Calculate cost for a row using rates config."""
    try:
        recorded_cost = row["recorded_cost"]
        if recorded_cost and recorded_cost > 0:
            return recorded_cost
    except (KeyError, IndexError):
        pass
    
    try:
        model_id = row["model_id"] if not is_summary else ""
    except (KeyError, IndexError):
        model_id = ""
    
    return calculate_cost(
        model_id or "",
        row["input_tokens"] or 0,
        row["output_tokens"] or 0,
        row["cache_read"] or 0,
        0,
        rates
    )


def _render_report_table(rows: list, title: str, rates: dict) -> None:
    """Render usage data as a rich table."""
    table = Table(title=title)
    table.add_column("Date", style="cyan")
    table.add_column("Source", style="blue")
    table.add_column("Model", style="magenta")
    table.add_column("Requests", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache Read", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost", justify="right", style="green")
    
    total_requests = 0
    total_input = 0
    total_output = 0
    total_cache = 0
    total_tokens = 0
    total_cost = 0.0
    
    for row in rows:
        cost = _calculate_row_cost(row, rates)
        table.add_row(
            row["date"],
            row["source"] or "Unknown",
            row["model"] or "Unknown",
            str(row["requests"]),
            _format_tokens(row["input_tokens"] or 0),
            _format_tokens(row["output_tokens"] or 0),
            _format_tokens(row["cache_read"] or 0),
            _format_tokens(row["total_tokens"] or 0),
            f"${cost:.4f}"
        )
        total_requests += row["requests"]
        total_input += row["input_tokens"] or 0
        total_output += row["output_tokens"] or 0
        total_cache += row["cache_read"] or 0
        total_tokens += row["total_tokens"] or 0
        total_cost += cost
    
    table.add_section()
    table.add_row(
        "[bold]Total[/bold]",
        "",
        "",
        f"[bold]{total_requests}[/bold]",
        f"[bold]{_format_tokens(total_input)}[/bold]",
        f"[bold]{_format_tokens(total_output)}[/bold]",
        f"[bold]{_format_tokens(total_cache)}[/bold]",
        f"[bold]{_format_tokens(total_tokens)}[/bold]",
        f"[bold green]${total_cost:.4f}[/bold green]"
    )
    
    console.print(table)


def _generate_csv(rows: list, rates: dict) -> str:
    """Generate CSV output from rows."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "date", "source", "model", "requests",
        "input_tokens", "output_tokens", "cache_read_tokens",
        "total_tokens", "cost_usd"
    ])
    
    for row in rows:
        cost = _calculate_row_cost(row, rates)
        writer.writerow([
            row["date"],
            row["source"] or "Unknown",
            row["model"] or "Unknown",
            row["requests"],
            row["input_tokens"] or 0,
            row["output_tokens"] or 0,
            row["cache_read"] or 0,
            row["total_tokens"] or 0,
            f"{cost:.6f}"
        ])
    
    return output.getvalue()
