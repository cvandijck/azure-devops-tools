import pytest

from adopt.backlog.sort import reorder_backlog, reorder_backlog_local, sort_backlog
from adopt.connect import create_connection, get_work_client, get_work_item_tracking_client
from adopt.utils import Backlog, create_team_context, get_backlog, get_backlog_category_from_work_item_type


def test_local_backlog_reverse(url, token, project, team):
    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type='story')

    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
    )

    # reverse the order of user stories
    reversed_backlog = Backlog(list(reversed(backlog.work_items)))
    assert backlog != reversed_backlog

    reorder_backlog_local(backlog=backlog, target_backlog=reversed_backlog)
    assert backlog == reversed_backlog


@pytest.mark.mutate
def test_azure_backlog_reverse(url, token, project, team):
    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type='story')

    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
    )

    # reverse the order of user stories
    reversed_backlog = Backlog(list(reversed(backlog.work_items)))

    assert backlog != reversed_backlog
    reorder_backlog(
        backlog=backlog,
        target_backlog=reversed_backlog,
        work_client=work_client,
        team_context=team_context,
    )

    new_backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
    )
    assert new_backlog == reversed_backlog

    reorder_backlog(
        backlog=reversed_backlog,
        target_backlog=backlog,
        work_client=work_client,
        team_context=team_context,
    )


@pytest.mark.mutate
def test_azure_backlog_sort(url, token, project, team):
    connection = create_connection(organization_url=url, token_password=token)
    wit_client = get_work_item_tracking_client(connection=connection)
    work_client = get_work_client(connection=connection)
    team_context = create_team_context(project=project, team=team)
    category = get_backlog_category_from_work_item_type(work_item_type='story')

    sort_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=category,
    )
