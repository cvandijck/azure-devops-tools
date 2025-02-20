import click

from adopt.backlog.sort import DEFAULT_SORT_KEY, VALID_SORT_KEY_STR, sort_backlog
from adopt.cli import log_option, project_option, team_option, token_option, url_option
from adopt.connect import create_connection, get_work_client, get_work_item_tracking_client
from adopt.formatting import format_backlog_as_table
from adopt.logging import configure_logging, convert_logging_level
from adopt.utils import create_team_context, get_backlog, get_backlog_category_from_work_item_type


@click.group(name='backlog', help='Tools to work with the backlog')
def cli_backlog(): ...


category_type = click.Choice(['Story', 'Feature', 'Epic'], case_sensitive=False)
category_option = lambda: click.option('--category', '-c', help='Backlog Category', default='Story', type=category_type)


@cli_backlog.command(name='sort', help='Sort the backlog')
@url_option()
@token_option()
@project_option()
@team_option()
@log_option()
@category_option()
@click.option('--sort_key', '-s', help=f'Sort key [{VALID_SORT_KEY_STR}]', default=DEFAULT_SORT_KEY)
def cli_sort_backlog(url: str, token: str, project: str, team: str, category: str, sort_key: str, log_level: str):
    log_level = convert_logging_level(log_level)
    configure_logging(level=log_level, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    sort_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
        sort_key=sort_key,
    )


@cli_backlog.command(name='print', help='Print the backlog')
@url_option()
@token_option()
@project_option()
@team_option()
@log_option()
@category_option()
def cli_print_backlog(url: str, token: str, project: str, team: str, category: str, log_level: str):
    log_level = convert_logging_level(log_level)
    configure_logging(level=log_level, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
    )

    table = format_backlog_as_table(backlog)
    print(table)
