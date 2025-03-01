import click

from adopt.backlog.fix import fix_backlog_state
from adopt.cli.backlog.options import category_option
from adopt.cli.options import CONTEXT_SETTINGS, log_option, project_option, team_option, token_option, url_option
from adopt.connect import create_connection, get_work_client, get_work_item_tracking_client
from adopt.logging import configure_logging, convert_logging_level
from adopt.utils import create_team_context, get_backlog_category_from_work_item_type

close_option = click.option('--allow-close', help='Allow to close work items', is_flag=True)


@click.command(name='fix', help='Fix inconsistencies in the backlog', context_settings=CONTEXT_SETTINGS)
@url_option
@token_option
@project_option
@team_option
@category_option
@close_option
@log_option
def cli_fix_backlog(url: str, token: str, project: str, team: str, category: str, allow_close: bool, log_level: str):
    log_level = convert_logging_level(log_level)
    configure_logging(level=log_level, exclude_external_logs=True)

    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type=category)

    fix_backlog_state(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
        update_self=True,  # leave for now, expose if necessary
        allow_to_close=allow_close,
    )
