import typer
from typing_extensions import Annotated
from decouple import config
import requests
from rich.console import Console
import shlex
from rich.rule import Rule


console = Console()

SERVER_URL = config("SERVER_URL", default="http://127.0.0.1:8080/")

app = typer.Typer(
    name="task-manager-cli",
    help="A CLI to manage tasks.",
    no_args_is_help=True, # display help if no command is given initially
    add_completion=True, # Disable shell completion
)

@app.command()
def get_jwt_token(
    username: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
):
    try:
        response = requests.post(
            f"{SERVER_URL}api/token/",
            data={
                "username": username,
                "password": password,
            },
        )
        if response.status_code == 200:
            console.print(f"[bold green]Access Token:[/bold green] {response.json().get('access')}")
            console.print(f"[bold green]Refresh Token:[/bold green] {response.json().get('refresh')}")
        else:
            console.print(f"Error:- [bold red]username or password didn't match :[/bold red]")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Network error: {e}")
        raise typer.Exit(1)


@app.command()
def user_signup(
    username: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
    email: str = typer.Option(None, prompt=True),
):
    """
    Signup a new user.
    Thi

    Args:
        username (str): _description_
        password (Annotated[ str, typer.Option, optional): _description_. Defaults to True, confirmation_prompt=True, hide_input=True) ].
        email (str, optional): _description_. Defaults to typer.Option(None, prompt=True).

    Raises:
        typer.Exit: _description_
    """
    try:
        response = requests.post(
            f"{SERVER_URL}api/user-signup/",
            json={
                "username": username,
                "password": password,
                "email": email,
            },
        )
        if response.status_code == 201:
            typer.echo("User created successfully.")
        else:
            console.print(f"Error: {response.json().get('error', 'Unknown error')}")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Network error: {e}")
        raise typer.Exit(1)

@app.command()
def run_api(access_token: Annotated[str, typer.Option("--access-token", "-at", help="JWT access token for authentication.")] = None):
    """
    Run the API server.
    """
    console.print("[bold magenta]Welcome to the task manager CLI![/bold magenta]")
    console.print("Enter commands like 'create my-res --value hello', 'get', 'destroy my-res', or 'exit'.")
    access_token = access_token.strip().replace(" ", "")

    while True:
        try:
            # Handle Ctrl+C or Ctrl+D
            console.print(Rule())
            console.print(Rule("Enter Command", style="bold blue", align="left"))
            console.print("Access token is :", access_token)
            command_input = input("> ").strip()

            if command_input.lower() in ["exit", "quit"]:
                console.print("\n[bold magenta]Exiting CLI. Goodbye![/bold magenta]")
                break

            try:
                # Parsing input through shlex to handle quotes
                command_parts = shlex.split(command_input)
            except ValueError as e:
                 console.print(f"[bold red]Error parsing command:[/bold red] {e}")
                 continue

            try:
                # Typer process command_parts as if they were sys.argv
                app(args=command_parts, prog_name="task-manager-cli")
            except typer.Exit as e:
                # Raised by Typer for successful exits (like after help) or expected failures
                if e.code != 0:
                     pass # Keep loop running
            except SystemExit as e:
                 if e.code != 0:
                     console.print(f"[bold red]System Exit Error (Code: {e.code})[/bold red]")
            except Exception as e:
                console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D
            console.print("\n[bold magenta]Exiting CLI. Goodbye![/bold magenta]")
            break

if __name__ == "__main__":
    app()
