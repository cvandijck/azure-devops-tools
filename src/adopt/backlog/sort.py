import logging
from dataclasses import dataclass
from typing import Optional

from azure.devops.v7_0.work import ReorderOperation, TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient

from adopt.utils import BACKLOG_REQUIREMENT_CATEGORY, AbstractWorkItem, Backlog, get_backlog

LOGGER = logging.getLogger(__name__)


@dataclass
class Swap:
    item: AbstractWorkItem
    next_item: Optional[AbstractWorkItem]
    previous_item: Optional[AbstractWorkItem]

    def __str__(self) -> str:
        prev_item, next_item = self.previous_item, self.next_item
        after_text = f'after "{prev_item.title}"' if prev_item else 'at the beginning'
        before_text = f'before "{next_item.title}"' if next_item else 'at the end'
        return f'"{self.item.title}" {after_text} and {before_text}'

    @property
    def item_id(self) -> int:
        return self.item.id

    @property
    def next_id(self) -> int:
        return self.next_item.id if self.next_item else 0

    @property
    def previous_id(self) -> int:
        return self.previous_item.id if self.previous_item else 0


def sort_backlog(
    wit_client: WorkItemTrackingClient,
    work_client: WorkClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> Backlog:
    # Get the work items in the current sprint
    backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )

    LOGGER.debug('Current backlog:')
    for item in backlog:
        LOGGER.debug(item)

    # Verify the order of user stories by priority
    sorted_backlog = Backlog(sorted(backlog.work_items))

    LOGGER.debug('Sorted backlog:')
    for item in sorted_backlog:
        LOGGER.debug(item)

    is_in_order = backlog == sorted_backlog
    if is_in_order:
        LOGGER.info('all user stories are in correct order')
        return

    LOGGER.info('user stories are not in order of priority')
    reorder_backlog(backlog=backlog, target_backlog=sorted_backlog, work_client=work_client)

    new_backlog = get_backlog(
        wit_client=wit_client,
        work_client=work_client,
        team_context=team_context,
        backlog_category=backlog_category,
    )
    LOGGER.debug('New backlog:')
    for item in new_backlog:
        LOGGER.debug(item)

    assert new_backlog == sorted_backlog
    return new_backlog


def reorder_backlog(backlog: Backlog, target_backlog: Backlog, work_client: WorkClient) -> Backlog:
    swaps = _compute_swaps(backlog=backlog, target=target_backlog)
    for swap in swaps:
        LOGGER.info(f'Apply swap {swap}')
        _apply_swap_on_azure(swap=swap, work_client=work_client)


def _compute_swaps(original: Backlog, target: Backlog) -> list[Swap]:
    swaps = []

    current_backlog = original
    for target_item_idx, target_item in enumerate(target.work_items):
        current_items = current_backlog.work_items
        item_on_current_backlog = current_items[target_item_idx]

        if item_on_current_backlog.id == target_item.id:
            continue

        if target_item_idx == 0:
            previous_item = None
            next_item = current_items[target_item_idx]
        elif target_item_idx == len(target) - 1:
            previous_item = current_items[target_item_idx - 1]
            next_item = None
        else:
            previous_item = current_items[target_item_idx - 1]
            next_item = current_items[target_item_idx]

        swap = Swap(item=target_item, next_item=next_item, previous_item=previous_item)
        current_backlog = _apply_swap_on_backlog(swap=swap, backlog=current_backlog)
        swaps.append(swap)

    return swaps


def _apply_swap_on_azure(swap: Swap, work_client: WorkClient, team_context: TeamContext):
    reorder_operation = ReorderOperation(
        ids=[swap.item_id],
        iteration_path=None,
        next_id=swap.next_id,
        previous_id=swap.previous_id,
    )

    work_client.reorder_backlog_work_items(reorder_operation, team_context=team_context)


def _apply_swap_on_backlog(swap: Swap, backlog: Backlog):
    work_items = list(backlog.work_items)
    work_items.remove(swap.item)

    if swap.previous_item is None:
        work_items = [swap.item] + work_items
    elif swap.next_item is None:
        work_items = work_items + [swap.item]
    else:
        prev_item_idx = work_items.index(swap.previous_item)
        next_item_idx = work_items.index(swap.next_item)
        assert prev_item_idx == next_item_idx - 1

        work_items = work_items[: prev_item_idx + 1] + [swap.item] + work_items[next_item_idx:]

    return Backlog(work_items)
