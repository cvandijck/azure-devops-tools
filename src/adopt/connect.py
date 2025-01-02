from typing import Optional

from azure.devops.connection import Connection
from azure.devops.v7_0.work import WorkClient
from azure.devops.v7_0.work_item_tracking import WorkItemTrackingClient
from msrest.authentication import BasicAuthentication


def create_connection(organization_url: str, token_password: str, user: Optional[str] = None) -> Connection:
    user = user if user else ''
    credentials = BasicAuthentication(username=user, password=token_password)
    connection = Connection(base_url=organization_url, creds=credentials)
    return connection


def get_work_item_tracking_client(connection: Connection) -> WorkItemTrackingClient:
    return connection.clients.get_work_item_tracking_client()


def get_work_client(connection: Connection) -> WorkClient:
    return connection.clients.get_work_client()
