from turtle import title
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.traceback import Traceback
from api.utils.cli.cli_types import TableInfo, QueryResults


console = Console()


class CLIConsole:

    @staticmethod
    def info(message: str) -> None:
        console.print(f"[blue][ INFO ][/blue] - {message}")

    @staticmethod
    def error(message: str) -> None:
        console.print(f"[red][ ERROR ][/red] - {message}", style="bold red")

    @staticmethod
    def success(message: str) -> None:
        console.print(f"[green][ * ][/green] {message}", style="bold green")
    
    
    

class DBConsole:
    @staticmethod
    def model_name_panels(model_names: list[str]) -> None:
        model_names_str = "\n".join([f"• {model}" for model in model_names])
        console.print(
            Panel(
            f"[white]{model_names_str}[/white]",
            title="Available Models",
            style="bold cyan",
            border_style="bold cyan"
            )
        )
    
    
    @staticmethod
    def show_db_table(table_info: TableInfo) -> None:
        panel_str = (
            f"[bold cyan]Size:[/bold cyan] [white]{table_info.size}[/white]\n"
            f"[bold cyan]Columns:[/bold cyan] [italic white]{
                ', '.join(table_info.columns)}[/italic white]\n"
        )
        if table_info.schema:
            panel_str += f"[bold cyan]Schema:[/bold cyan]\n{table_info.schema}"

        console.print(
            Panel(
                panel_str,
                title=f"api(~app.db\\{table_info.table_name})",
                style="italic cyan"
            )
        )

    @staticmethod
    def show_all_tables(include_schema: bool, tables: list[TableInfo]) -> None:
        if not tables:
            console.print("[yellow]No tables to display.[/yellow]")
            return

        table = Table(
            title="Database Tables",
            title_style="bold cyan",
            show_lines=True
        )

        table.add_column("Table Name", style="bold magenta")
        table.add_column("Size", justify="right")
        table.add_column("Columns")
        table.add_column("SQL Schema")

        for t in tables:
            schema_str = t.schema if t.schema and include_schema else "[dim](n/a)[/dim]"

            if include_schema:
                table.add_row(
                    t.table_name,
                    str(t.size),
                    ", ".join(t.columns),
                    schema_str
                )
            else:
                table.add_row(
                    t.table_name,
                    str(t.size),
                    ", ".join(t.columns)
                )

        console.print(table)

    @staticmethod
    def display_query_results(query_results: QueryResults) -> None:

        if len(query_results.result) <= query_results.page_size:
            header = (
                f"[italic red]Result:[/italic red]",
                f'[bold white]{len(query_results.result)}[/bold white] row(s)'
            )
        else:
            header = (
                f'[italic white]Showing [/italic white]'
                f'[bold yellow]{query_results.page_size}[/italic white]',
                f' [italic white]of[/italic white] '
                f'[bold red]{len(query_results.result)}[/bold red] row(s)'
            )
        result_table = Table(
            title='Query Results', title_style="bold cyan", show_lines=True
        )

        for cols in query_results.columns:
            result_table.add_column(cols)

        for row_data in query_results.result:
            row_data_list = [str(row_data[col])
                             for col in query_results.columns]
            result_table.add_row(*row_data_list)

        console.print(header)
        console.print(result_table)

    @staticmethod
    def display_resulting_sql(stmnt_str) -> None:
        fmt_statement = (
            '[bold white]SQL: [/bold white]'
            f'[italic gray]{stmnt_str}[/italic gray]'
        )
        console.print(
            Panel(
                fmt_statement,
                title="Resulting SQL",
                border_style="dim white",
                title_align="left"
            )
        )


class ConsoleMisc:
    @staticmethod
    def format_exc(exc: Exception) -> None:
        console.print(
            Panel(
                Traceback(show_locals=True, suppress=[__name__]),
                title="[red]Exception Occurred[/red]",
                border_style="red",
            )
        )
