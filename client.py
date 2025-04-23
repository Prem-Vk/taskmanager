import typer
from typing_extensions import Annotated
from decouple import config
import requests

SERVER_URL = config("SERVER_URL", default="http://127.0.0.1:8080/")

app = typer.Typer()

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
            token = response.json().get("access")
            if token:
                typer.echo(f"JWT Token: {token}")
            else:
                typer.echo("Failed to retrieve JWT token.")
        else:
            typer.echo(f"Error: {response.json().get('error', 'Unknown error')}")
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
            typer.echo(f"Error: {response.json().get('error', 'Unknown error')}")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Network error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
