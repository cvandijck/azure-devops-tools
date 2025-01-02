import logging
from dataclasses import dataclass
from typing import Optional, Type

from azure.devops.v7_0.work import TeamContext, WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItem, WorkItemTrackingClient

# backlog categories
BACKLOG_EPIC_CATEGORY = 'Microsoft.EpicCategory'
BACKLOG_FEATURE_CATEGORY = 'Microsoft.FeatureCategory'
BACKLOG_REQUIREMENT_CATEGORY = 'Microsoft.RequirementCategory'

# work item fields
WI_ID_KEY = 'System.Id'
WI_TITLE_KEY = 'System.Title'
WI_PRIORITY_KEY = 'Microsoft.VSTS.Common.Priority'
WI_ITEM_TYPE_KEY = 'System.WorkItemType'
WI_ITERATION_PATH_KEY = 'System.IterationPath'
WI_STORY_POINTS_KEY = 'Microsoft.VSTS.Scheduling.StoryPoints'
WI_ASSIGNED_TO_KEY = 'System.AssignedTo'

WI_PARENT_RELATION = 'System.LinkTypes.Hierarchy-Reverse'
WI_RELATIONS = 'Relations'

# work item types
WI_EPIC_TYPE = 'Epic'
WI_FEATURE_TYPE = 'Feature'
WI_USER_STORY_TYPE = 'User Story'
WI_USER_STORY_TYPE_2 = 'Story'

BACKLOG_CATEGORY_WI_TYPE_MAP = {
    BACKLOG_EPIC_CATEGORY.lower(): WI_EPIC_TYPE,
    BACKLOG_FEATURE_CATEGORY.lower(): WI_FEATURE_TYPE,
    BACKLOG_REQUIREMENT_CATEGORY.lower(): WI_USER_STORY_TYPE,
}

BACKLOG_WI_TYPE_CATEGORY_MAP = {
    WI_EPIC_TYPE.lower(): BACKLOG_EPIC_CATEGORY,
    WI_FEATURE_TYPE.lower(): BACKLOG_FEATURE_CATEGORY,
    WI_USER_STORY_TYPE.lower(): BACKLOG_REQUIREMENT_CATEGORY,
    WI_USER_STORY_TYPE_2.lower(): BACKLOG_REQUIREMENT_CATEGORY,
}


def get_backlog_category_from_work_item_type(work_item_type: str) -> str:
    return BACKLOG_WI_TYPE_CATEGORY_MAP[work_item_type.lower()]


def get_work_item_type_from_backlog_category(backlog_category: str) -> str:
    return BACKLOG_CATEGORY_WI_TYPE_MAP[backlog_category.lower()]


LOGGER = logging.getLogger(__name__)


class AbstractWorkItem:
    PARENT_CLASS = Type['AbstractWorkItem']
    WI_TYPE = None

    PRINT_TITLE_LENGTH = 50
    PRINT_PARENT_PATH_SEP = ' > '

    def __init__(self, work_item: WorkItem, wit_client: WorkItemTrackingClient):
        if self.WI_TYPE and work_item.fields[WI_ITEM_TYPE_KEY] != self.WI_TYPE:
            raise ValueError(f'Work item is not a {self.WI_TYPE}')

        self._work_item = work_item
        self._wit_client = wit_client

        self._parent = None

    def update(self):
        wi = self._wit_client.get_work_item(id=self.id, expand=WI_RELATIONS)
        self._work_item = wi
        self._parent = None

    @property
    def id(self) -> int:
        return self._work_item.id

    @property
    def title(self) -> str:
        return self._get_field(WI_TITLE_KEY)

    @property
    def _normalized_title(self) -> str:
        title = self.title

        if not title:
            return None

        if len(title) > self.PRINT_TITLE_LENGTH:
            title = title[: self.PRINT_TITLE_LENGTH - 3] + '...'
        return f'{title: <{self.PRINT_TITLE_LENGTH}}'

    @property
    def iteration_path(self) -> str:
        return self._work_item.fields[WI_ITERATION_PATH_KEY]

    @property
    def assigned_to(self) -> Optional[str]:
        return self._get_field(WI_ASSIGNED_TO_KEY)

    @property
    def story_points(self) -> int:
        return self._get_field(WI_STORY_POINTS_KEY)

    @property
    def priority(self) -> int:
        return self._get_field(WI_PRIORITY_KEY)

    @property
    def parent(self):
        return self._get_parent()

    @property
    def item_path(self) -> tuple[str]:
        if self.parent is None:
            return (self.title,)
        return (*self.parent.item_path, self.title)

    @property
    def sort_key(self) -> tuple:
        return self.priority, self.iteration_path, self.priority, self.item_path

    def _get_field(self, field_name: str):
        return self._work_item.fields.get(field_name, None)

    def _get_parent(self):
        if self._parent is not None:
            return self._parent

        wi = _get_parent_work_item(self._work_item, self._wit_client)
        if not wi:
            return None

        self._parent = self.PARENT_CLASS(wi, self._wit_client)
        return self._parent

    def __lt__(self, other: 'AbstractWorkItem') -> bool:
        self_it_path = self.iteration_path.split('\\')
        other_it_path = other.iteration_path.split('\\')

        if len(self_it_path) == len(other_it_path):
            if self_it_path[-1] == other_it_path[-1]:
                self_sort = (self.priority, *self.item_path)
                other_sort = (other.priority, *other.item_path)
                return self_sort < other_sort
            else:
                return self_it_path[-1] > other_it_path[-1]
        else:
            # reversed to put backlog last
            return len(self_it_path) > len(other_it_path)

    def __str__(self) -> str:
        return f'[{self.id}] {self._normalized_title} | {self.iteration_path} | {self.PRINT_PARENT_PATH_SEP.join(self.item_path)}'  # noqa: E501

    def __repr__(self):
        return str(self)


class Epic(AbstractWorkItem):
    PARENT_CLASS = AbstractWorkItem
    WI_TYPE = WI_EPIC_TYPE

    def __init__(self, work_item: WorkItem, wit_client: WorkItemTrackingClient):
        super().__init__(work_item, wit_client)


class Feature(AbstractWorkItem):
    PARENT_CLASS = Epic
    WI_TYPE = WI_FEATURE_TYPE

    def __init__(self, work_item: WorkItem, wit_client: WorkItemTrackingClient):
        super().__init__(work_item, wit_client)


class UserStory(AbstractWorkItem):
    PARENT_CLASS = Feature
    WI_TYPE = WI_USER_STORY_TYPE

    def __init__(self, work_item: WorkItem, wit_client: WorkItemTrackingClient):
        super().__init__(work_item, wit_client)

    def __str__(self) -> str:
        return f'({self.priority}) {super().__str__()}'


@dataclass
class Backlog:
    work_items: list[AbstractWorkItem]

    def update(self):
        for wi in self.work_items:
            wi.update()

    def __iter__(self):
        return iter(self.work_items)

    def __getitem__(self, index):
        return self.work_items[index]

    def __len__(self):
        return len(self.work_items)

    def __eq__(self, other: 'Backlog'):
        return self.work_items == other.work_items

    def __str__(self):
        return '\n'.join(str(wi) for wi in self.work_items)


def _get_parent_work_item(work_item: WorkItem, wit_client: WorkItemTrackingClient) -> Optional[AbstractWorkItem]:
    relations = work_item.relations
    if not relations:
        return None

    for relation in relations:
        if relation.rel == WI_PARENT_RELATION:
            parent_id = relation.url.split('/')[-1]
            return wit_client.get_work_item(id=parent_id, expand=WI_RELATIONS)
    return None


def get_current_iteration(work_client: WorkClient, team_context: TeamContext) -> str:
    return work_client.get_team_iterations(team_context=team_context)


def create_team_context(project: str, team: str) -> TeamContext:
    return TeamContext(project=project, team=team)


def create_work_item_from_details(
    wi: WorkItem, wit_client: WorkItemTrackingClient, item_type: Optional[str] = None
) -> AbstractWorkItem:
    if item_type is None:
        item_type = wi.fields[WI_ITEM_TYPE_KEY]

    if item_type == WI_USER_STORY_TYPE:
        return UserStory(wi, wit_client)
    elif item_type == WI_FEATURE_TYPE:
        return Feature(wi, wit_client)
    elif item_type == WI_EPIC_TYPE:
        return Epic(wi, wit_client)
    else:
        raise ValueError(f'Unknown work item type: {item_type}')


def get_backlog(
    work_client: WorkClient,
    wit_client: WorkItemTrackingClient,
    team_context: TeamContext,
    backlog_category: str = BACKLOG_REQUIREMENT_CATEGORY,
) -> Backlog:
    # TODO: make work item type an input argument
    backlog_work_items = work_client.get_backlog_level_work_items(
        team_context=team_context, backlog_id=backlog_category
    ).work_items

    work_item_ids = [wi.target.id for wi in backlog_work_items]
    work_items_details = wit_client.get_work_items(ids=work_item_ids, expand=WI_RELATIONS)

    item_type = get_work_item_type_from_backlog_category(backlog_category)
    items = [create_work_item_from_details(wid, wit_client, item_type) for wid in work_items_details]
    return Backlog(items)
