import os
import re

import typer

from typing import Annotated

from loguru import logger

app = typer.Typer(pretty_exceptions_show_locals=False)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Kalsel seeder")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


class Generator:
    def __init__(self, name: str) -> None:
        self.name = name

    def model_gen(self) -> None:
        if os.path.exists(f"src/models/{self.name.lower()}.py"):
            logger.warning(
                f"Model file {self.name.lower()}.py already exists. Skipping..."
            )
            return
        with open("src/models/__template_mongo_model", "r") as file:
            file_contents = file.read()

            updated_contents = file_contents.replace(
                "template", self.name.lower()
            ).replace("Template", self.name.title())
        with open(f"src/models/{self.name.lower()}.py", "w") as file:
            file.write(updated_contents)

    def route_gen(self) -> None:
        if os.path.exists(f"src/routes/api/{self.name.lower()}.py"):
            logger.warning(
                f"Route file {self.name.lower()}.py already exists. Skipping..."
            )
            return
        with open("src/routes/api/__template_mongo_route", "r") as file:
            file_contents = file.read()

            updated_contents = file_contents.replace(
                "template", self.name.lower()
            ).replace("Template", self.name.title())
        with open(f"src/routes/api/{self.name.lower()}.py", "w") as file:
            file.write(updated_contents)

        with open("src/routes/base.py", "r") as file:
            base_contents = file.readlines()
            for i, line in enumerate(base_contents):
                if re.search(r"from src.routes.api", line):
                    temp = re.split(
                        r",[^\w]{0,}",
                        re.sub(r"(from src.routes.api import(\s){1,})|(\n)", "", line),
                    )
                    temp.append(f"{self.name.lower()}")

                    base_contents[i] = f"from src.routes.api import {', '.join(temp)}" + "\n"
            base_contents.append(
                "\n" +f"router.include_router({self.name.lower()}.app, prefix='/{self.name.lower()}', tags=['{self.name.title()}'])"
            )

        with open("src/routes/base.py", "w") as file:
            file.writelines(base_contents)

    def clear(self) -> None:
        if os.path.exists(f"src/models/{self.name.lower()}.py"):
            os.remove(f"src/models/{self.name.lower()}.py")
        if os.path.exists(f"src/routes/api/{self.name.lower()}.py"):
            os.remove(f"src/routes/api/{self.name.lower()}.py")

        with open("src/routes/base.py", "r") as file:
            base_contents = file.readlines()
            for i, line in enumerate(base_contents):
                if re.search(r"from src.routes.api ", line):
                    temp = re.split(
                        r",[^\w]{0,}",
                        re.sub(r"(from src.routes.api import(\s){1,})|(\n)", "", line),
                    )
                    if self.name.lower() in temp:
                        temp.remove(self.name.lower())
                    base_contents[i]= f"from src.routes.api import {', '.join(temp)}" + "\n"
                if line == f"router.include_router({self.name.lower()}.app, prefix='/{self.name.lower()}', tags=['{self.name.title()}'])":
                    base_contents.remove(line)
        with open("src/routes/base.py", "w") as file:
            file.writelines(base_contents)


@app.command()
def base(name: Annotated[str, typer.Option()]) -> None:
    logger.info(f"Generating base file for {name}...")
    gen = Generator(name)
    gen.model_gen()
    gen.route_gen()


@app.command()
def clear(name: Annotated[str, typer.Option()]) -> None:
    gen = Generator(name)
    gen.clear()
