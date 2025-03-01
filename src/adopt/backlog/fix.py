import logging

from azure.devops.v7_0.work import TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient

from adopt.utils import (
    BACKLOG_REQUIREMENT_CATEGORY,
    WI_STATE_KEY,
    State,
    get_backlog,
    get_parent_backlog_categories,
    update_work_item_field,
)

LOGGER = logging.getLogger(__name__)


def fix_backlog_state(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
    update_self: bool = True,
    allow_to_close: bool = False,
) -> None:
    parent_backlog_categories = get_parent_backlog_categories(backlog_category=backlog_category)
    for parent_category in reversed(parent_backlog_categories):
        fix_backlog_state(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=parent_category,
            update_self=True,  # has to be true to actually update them
        )

    if update_self:
        backlog = get_backlog(
            wit_client=wit_client,
            work_client=work_client,
            team_context=team_context,
            backlog_category=backlog_category,
        )
        for item in backlog:
            children = item.children
            if not children:
                continue

            child_states = {child.state for child in children}
            if any(state == State.ACTIVE.value for state in child_states):
                new_state = State.ACTIVE.value
            elif all(state == State.NEW.value for state in child_states):
                new_state = State.NEW.value
            elif allow_to_close and all(state == State.CLOSED.value for state in child_states):
                new_state = State.CLOSED.value
            else:
                new_state = None

            if new_state and item.state != new_state:
                LOGGER.info(f'Updating {item.item_type} {item.title} to {new_state}')
                update_work_item_field(
                    work_item=item.azure_work_item,
                    wit_client=wit_client,
                    field=WI_STATE_KEY,
                    value=new_state,
                )

    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )
