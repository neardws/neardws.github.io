"""Token Tracker CLI."""
import click
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.config import DB_PATH, RATES_FILE, load_rates, calculate_cost, save_rates, DEFAULT_RATES
from src.db.connection import init_db, db_exists, get_connection
from src.ingestors.openclaw import OpenClawIngestor
from src.ingestors.droid import DroidIngestor
from src.ingestors.cliproxyapi import CLIProxyAPIIngestor

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Token Tracker - Track LLM token usage across coding agents."""
    pass


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Force re-initialization")
def init(force: bool):
    """Initialize the token tracker database."""
    if db_exists() and not force:
        console.print(f"[yellow]Database already exists at {DB_PATH}[/yellow]")
        console.print("Use --force to re-initialize")
        return
    
    console.print(f"[blue]Initializing database at {DB_PATH}...[/blue]")
    init_db()
    console.print("[green]Database initialized successfully![/green]")
    
    # Show seed data
    with get_connection() as conn:
        providers = conn.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
        sources = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        models = conn.execute("SELECT COUNT(*) FROM models").fetchone()[0]
    
    console.print(f"  Providers: {providers}")
    console.print(f"  Sources: {sources}")
    console.print(f"  Models: {models}")


@cli.command()
@click.argument("source", required=False)
@click.option("--since", "-s", help="Ingest data since date (YYYY-MM-DD)")
def ingest(source: str, since: str):
    """Ingest token usage data from sources.
    
    SOURCE can be 'openclaw' or 'droid'. If not specified, ingests from all sources.
    """
    if not db_exists():
        console.print("[red]Database not initialized. Run 'tt init' first.[/red]")
        return
    
    since_dt = None
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid date format: {since}. Use YYYY-MM-DD.[/red]")
            return
    
    ingestors = []
    if source is None or source == "openclaw":
        ingestors.append(("OpenClaw", OpenClawIngestor()))
    if source is None or source == "droid":
        ingestors.append(("Droid", DroidIngestor()))
    if source is None or source == "cliproxyapi":
        ingestors.append(("CLIProxyAPI", CLIProxyAPIIngestor()))
    
    if not ingestors:
        console.print(f"[red]Unknown source: {source}[/red]")
        return
    
    total = 0
    console.print("[blue]Ingesting data...[/blue]")
    
    for name, ingestor in ingestors:
        count = ingestor.ingest(since_dt)
        total += count
        if count > 0:
            console.print(f"  [green]{name}: {count} new records[/green]")
        else:
            console.print(f"  [dim]{name}: no new records[/dim]")
    
    console.print(f"\n[green]Total: {total} records ingested[/green]")


@cli.command()
@click.option("--range", "-r", "date_range", default="today", help="Date range (today, 7d, 30d, all)")
def usage(date_range: str):
    """Show token usage summary."""
    if not db_exists():
        console.print("[red]Database not initialized. Run 'tt init' first.[/red]")
        return
    
    rates = load_rates()
    
    # Build date filter
    if date_range == "today":
        date_filter = "date(u.recorded_at) = date('now')"
        title = "Today's Usage"
    elif date_range == "7d":
        date_filter = "u.recorded_at >= datetime('now', '-7 days')"
        title = "Last 7 Days Usage"
    elif date_range == "30d":
        date_filter = "u.recorded_at >= datetime('now', '-30 days')"
        title = "Last 30 Days Usage"
    else:
        date_filter = "1=1"
        title = "All Time Usage"
    
    with get_connection() as conn:
        # Get usage by model
        query = f"""
            SELECT 
                m.display_name as model,
                m.model_id,
                COUNT(*) as requests,
                SUM(u.input_tokens) as input_tokens,
                SUM(u.output_tokens) as output_tokens,
                SUM(u.cache_read_tokens) as cache_read,
                SUM(u.cache_write_tokens) as cache_write,
                SUM(u.total_tokens) as total_tokens,
                SUM(u.cost_total) as recorded_cost
            FROM usage u
            JOIN models m ON u.model_id = m.id
            WHERE {date_filter}
            GROUP BY m.id
            ORDER BY total_tokens DESC
        """
        
        rows = conn.execute(query).fetchall()
        
        if not rows:
            console.print(f"[yellow]No usage data found for {date_range}[/yellow]")
            return
        
        # Create table
        table = Table(title=title)
        table.add_column("Model", style="cyan")
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
            recorded_cost = row["recorded_cost"] or 0
            if recorded_cost > 0:
                cost = recorded_cost
            else:
                cost = calculate_cost(
                    row["model_id"],
                    row["input_tokens"] or 0,
                    row["output_tokens"] or 0,
                    row["cache_read"] or 0,
                    row["cache_write"] or 0,
                    rates
                )
            
            table.add_row(
                row["model"] or "Unknown",
                str(row["requests"]),
                _format_tokens(row["input_tokens"]),
                _format_tokens(row["output_tokens"]),
                _format_tokens(row["cache_read"]),
                _format_tokens(row["total_tokens"]),
                f"${cost:.4f}"
            )
            total_requests += row["requests"]
            total_input += row["input_tokens"] or 0
            total_output += row["output_tokens"] or 0
            total_cache += row["cache_read"] or 0
            total_tokens += row["total_tokens"] or 0
            total_cost += cost
        
        # Add total row
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
        
        if RATES_FILE.exists():
            console.print(f"\n[dim]Using rates from {RATES_FILE}[/dim]")
        else:
            console.print(f"\n[dim]Using default rates (create {RATES_FILE} to customize)[/dim]")


@cli.command()
def status():
    """Show database status and statistics."""
    if not db_exists():
        console.print(f"[red]Database not found at {DB_PATH}[/red]")
        console.print("Run 'tt init' to initialize.")
        return
    
    console.print(f"[blue]Database: {DB_PATH}[/blue]")
    console.print(f"Size: {DB_PATH.stat().st_size / 1024:.1f} KB\n")
    
    with get_connection() as conn:
        # Count records
        usage_count = conn.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
        session_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        
        # Latest record
        latest = conn.execute(
            "SELECT recorded_at FROM usage ORDER BY recorded_at DESC LIMIT 1"
        ).fetchone()
        
        # Ingest state
        states = conn.execute(
            "SELECT source, file_path, last_position, updated_at FROM ingest_state ORDER BY updated_at DESC LIMIT 5"
        ).fetchall()
    
    console.print(f"Usage records: {usage_count}")
    console.print(f"Sessions: {session_count}")
    
    if latest:
        console.print(f"Latest record: {latest[0]}")
    
    if states:
        console.print("\n[blue]Recent Ingest State:[/blue]")
        for state in states:
            console.print(f"  {state['source']}: {Path(state['file_path']).name} @ {state['last_position']} bytes")
    
    if RATES_FILE.exists():
        console.print(f"\n[green]Rates config: {RATES_FILE}[/green]")
    else:
        console.print(f"\n[dim]Rates config: not found (using defaults)[/dim]")


@cli.group()
def report():
    """Generate usage reports."""
    pass


@report.command("daily")
@click.option("--csv", "output_csv", is_flag=True, help="Output as CSV")
def report_daily(output_csv: bool):
    """Generate daily usage report."""
    from src.cli.report import generate_daily_report
    result = generate_daily_report(output_csv)
    if result:
        console.print(result)


@report.command("weekly")
@click.option("--csv", "output_csv", is_flag=True, help="Output as CSV")
def report_weekly(output_csv: bool):
    """Generate weekly usage report with day-by-day breakdown."""
    from src.cli.report import generate_weekly_report
    result = generate_weekly_report(output_csv)
    if result:
        console.print(result)


@cli.group()
def rates():
    """Manage rate configuration."""
    pass


@rates.command("show")
def rates_show():
    """Show current rate configuration."""
    current_rates = load_rates()
    
    table = Table(title="Token Rates (per 1M tokens)")
    table.add_column("Model", style="cyan")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache Read", justify="right")
    table.add_column("Cache Write", justify="right")
    
    for model_id, model_rates in current_rates.get("models", {}).items():
        table.add_row(
            model_id,
            f"${model_rates.get('input_per_1m', 0):.2f}",
            f"${model_rates.get('output_per_1m', 0):.2f}",
            f"${model_rates.get('cache_read_per_1m', 0):.2f}",
            f"${model_rates.get('cache_write_per_1m', 0):.2f}"
        )
    
    default_rates = current_rates.get("default", {})
    table.add_section()
    table.add_row(
        "[dim]default[/dim]",
        f"[dim]${default_rates.get('input_per_1m', 0):.2f}[/dim]",
        f"[dim]${default_rates.get('output_per_1m', 0):.2f}[/dim]",
        f"[dim]${default_rates.get('cache_read_per_1m', 0):.2f}[/dim]",
        f"[dim]${default_rates.get('cache_write_per_1m', 0):.2f}[/dim]"
    )
    
    console.print(table)
    
    if RATES_FILE.exists():
        console.print(f"\n[dim]Config file: {RATES_FILE}[/dim]")
    else:
        console.print(f"\n[dim]Using built-in defaults. Run 'tt rates init' to create config file.[/dim]")


@rates.command("init")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing config")
def rates_init(force: bool):
    """Initialize rate configuration file with defaults."""
    if RATES_FILE.exists() and not force:
        console.print(f"[yellow]Config file already exists at {RATES_FILE}[/yellow]")
        console.print("Use --force to overwrite")
        return
    
    save_rates(DEFAULT_RATES)
    console.print(f"[green]Created rate config at {RATES_FILE}[/green]")
    console.print("Edit this file to customize rates for your models.")


def _format_tokens(count: int) -> str:
    """Format token count with K/M suffix."""
    if count is None:
        return "0"
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count/1_000:.1f}K"
    return str(count)


if __name__ == "__main__":
    cli()
