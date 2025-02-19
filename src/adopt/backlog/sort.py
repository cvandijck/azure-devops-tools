import logging
from dataclasses import dataclass
from functools import cmp_to_key
from typing import Optional

from azure.devops.v7_0.work import ReorderOperation, TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient

from adopt.utils import BACKLOG_REQUIREMENT_CATEGORY, Backlog, BaseWorkItem, get_backlog

LOGGER = logging.getLogger(__name__)


@dataclass
class Swap:
    item: BaseWorkItem
    next_item: Optional[BaseWorkItem]
    previous_item: Optional[BaseWorkItem]

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


def compare_work_items(item1: BaseWorkItem, item2: BaseWorkItem) -> int:
    item1_iter_parts = item1.iteration_path.split('\\')
    item2_iter_parts = item2.iteration_path.split('\\')

    item1_hierarchy = item1.hierarchy
    item2_hierarchy = item2.hierarchy

    item1_ranks = [item.backlog_rank for item in item1_hierarchy[:-1]]
    item2_ranks = [item.backlog_rank for item in item2_hierarchy[:-1]]

    if len(item1_iter_parts) == len(item2_iter_parts):
        # both in backlog or both in sprint
        if item1_iter_parts[-1] == item2_iter_parts[-1]:
            # both in same sprint
            # sort by priority and full path (titles of parents and self)
            sort_tuple_1 = (item1.priority, *item1_ranks)
            sort_tuple_2 = (item2.priority, *item2_ranks)
            return -1 if sort_tuple_1 < sort_tuple_2 else 1
        else:
            return -1 if item1_iter_parts[-1] > item2_iter_parts[-1] else 1
    else:
        # one in backlog and one in sprint
        # put sprint items first
        return -1 if len(item1_iter_parts) > len(item2_iter_parts) else 1


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
    # rank_func = partial(
    #     get_work_item_backlog_rank,
    #     work_client=work_client,
    #     team_context=team_context,
    #     backlog_category=backlog_category,
    # )
    # compare_func = partial(compare_work_items, rank_func=rank_func)

    sorted_work_items = sorted(backlog.work_items, key=cmp_to_key(compare_work_items))
    sorted_backlog = Backlog(sorted_work_items)

    LOGGER.debug('Sorted backlog:')
    for item in sorted_backlog:
        LOGGER.debug(item)

    is_in_order = backlog == sorted_backlog
    if is_in_order:
        LOGGER.info('all user stories are in correct order')
        return

    LOGGER.info('user stories are not in the correct order')
    reorder_backlog(backlog=backlog, target_backlog=sorted_backlog, work_client=work_client, team_context=team_context)

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


def reorder_backlog(
    backlog: Backlog, target_backlog: Backlog, work_client: WorkClient, team_context: TeamContext
) -> Backlog:
    swaps = compute_swaps(backlog=backlog, target=target_backlog)
    for swap in swaps:
        LOGGER.info(f'Apply swap {swap}')
        _apply_swap_on_azure(swap=swap, work_client=work_client, team_context=team_context)


def reorder_backlog_local(backlog: Backlog, target_backlog: Backlog) -> Backlog:
    swaps = compute_swaps(backlog=backlog, target=target_backlog)
    for swap in swaps:
        LOGGER.info(f'Apply swap {swap}')
        _apply_swap_on_backlog(swap=swap, backlog=backlog)


def compute_swaps(backlog: Backlog, target: Backlog) -> list[Swap]:
    swaps = []

    current_backlog = backlog.copy()
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
        _apply_swap_on_backlog(swap=swap, backlog=current_backlog)
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
    work_items = backlog.work_items
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
    backlog.work_items = work_items
