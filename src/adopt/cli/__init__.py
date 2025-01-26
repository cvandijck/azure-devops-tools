import click

from adopt.env import PAT_ENV, PROJECT_ENV, TEAM_ENV, URL_ENV

log_type = click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False)

url_option = lambda: click.option('--url', '-u', help='Organization URL', envvar=URL_ENV)
token_option = lambda: click.option('--token', '-t', help='Personal Access Token', envvar=PAT_ENV)
project_option = lambda: click.option('--project', '-p', help='Project Name', envvar=PROJECT_ENV)
team_option = lambda: click.option('--team', '-t', help='Team Name', envvar=TEAM_ENV)
log_option = lambda: click.option('--log-level', '-l', help='Log Level', default='INFO', type=log_type)


@click.group()
def cli_root(): ...
