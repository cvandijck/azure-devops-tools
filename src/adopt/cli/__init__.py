import click

from adopt.config import ADO_ORG_URL_VAR, ADO_PAT_VAR, ADO_PROJECT_VAR, ADO_TEAM_VAR

log_type = click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False)

url_option = lambda: click.option('--url', '-u', help='Organization URL', envvar=ADO_ORG_URL_VAR)
token_option = lambda: click.option('--token', '-t', help='Personal Access Token', envvar=ADO_PAT_VAR)
project_option = lambda: click.option('--project', '-p', help='Project Name', envvar=ADO_PROJECT_VAR)
team_option = lambda: click.option('--team', '-t', help='Team Name', envvar=ADO_TEAM_VAR)
log_option = lambda: click.option('--log-level', '-l', help='Log Level', default='INFO', type=log_type)


@click.group()
def cli_root(): ...
