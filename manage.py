from flask.cli import FlaskGroup

from frontEnd import app, socket

cli = FlaskGroup(socket)

if __name__ == "__main__":
    cli()