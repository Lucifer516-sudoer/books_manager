from typer import Typer

app = Typer(
    name="BookManager",
    pretty_exceptions_show_locals=True,
)


if __name__ == "__main__":
    app()
