import logging
from rich.console import Console
from rich.logging import RichHandler


class ApiLogger:
    """A rich-formatted logger for API operations.

    This logger provides enhanced console output with rich formatting,
    including icons and colors for different log levels. It uses the
    Rich library to provide better visual feedback for API operations.

    Args:
        name: The name of the logger, typically the module or class name.

    Attributes:
        console: The Rich console instance used for direct printing.
    """

    def __init__(self, name: str):
        """Initialize the ApiLogger with a rich handler.

        Args:
            name: The name of the logger to create.
        """
        console = Console()
        handler = RichHandler(
            markup=True,
            console=console,
            rich_tracebacks=True,
            show_level=True,
            show_path=False,
        )
        root = logging.getLogger(name)
        root.setLevel(logging.NOTSET)
        root.handlers = [handler]
        self._logger = root
        self.console = console
        self.verbose = 1

    def set_verbose(self, verbose: int):
        """Set the verbose mode of the logger.

        Args:
            verbose: Whether to log verbose information.
        """

        self.verbose = verbose

    def info(self, message: str):
        """Log an informational message with an info icon.

        Args:
            message: The message to log.
        """
        if self.verbose >= 1:
            self.console.print(f"[bold blue]ℹ[/bold blue] {message}")

    def success(self, message: str):
        """Log a success message with a checkmark icon.

        Args:
            message: The message to log.
        """
        if self.verbose >= 2:
            self.console.print(f"[green]✓[/green] {message}")

    def error(self, message: str):
        """Log an error message with an error icon.

        Args:
            message: The message to log.
        """
        self._logger.log(logging.ERROR, f"[red]✗[/red] {message}")

    def warning(self, message: str):
        """Log a warning message with a warning icon.

        Args:
            message: The message to log.
        """
        self._logger.log(logging.WARNING, f"[yellow]![/yellow] {message}")

    def debug(self, message: str):
        """Log a debug message with a subtle icon.

        Args:
            message: The message to log.
        """
        self._logger.log(logging.DEBUG, f"[dim]…[/dim] {message}")
