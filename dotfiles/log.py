import click


def message(msg):
    click.echo(click.style(msg, fg="green"))


def warning(msg):
    click.echo(click.style(msg, fg="red"))


def verbose(msg):
    verbose = click.get_current_context().obj["VERBOSE"]
    if not verbose:
        return

    click.echo(msg)
