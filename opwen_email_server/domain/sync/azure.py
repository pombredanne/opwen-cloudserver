from collections import OrderedDict
from itertools import chain

from opwen_domain.sync import Sync
from opwen_domain.sync.azure import AzureSync


class MultiClientAzureSync(Sync):
    def __init__(self, auth, email_info, serializer):
        """
        :type auth: opwen_domain.sync.azure.AzureAuth
        :type email_info: (str, str, str)
        :type serializer: opwen_infrastructure.serialization.Serializer

        """
        self._auth = auth
        self._download_locations_pattern = email_info[0]
        self._upload_locations_pattern = email_info[1]
        self._email_host = email_info[2]
        self._serializer = serializer

    def upload(self, items):
        emails_by_client = self._infer_upload_clients(items)
        sync = self._create_sync(emails_by_client.keys())
        return sync.upload(emails_by_client.values())

    def download(self):
        clients = self._discover_download_clients()
        sync = self._create_sync(clients)
        return sync.download()

    def _create_sync(self, clients):
        """
        :type clients: collections.Iterable[str]
        :rtype: opwen_domain.sync.azure.AzureSync

        """
        return AzureSync(
            auth=self._auth,
            download_locations=map(self._download_locations_pattern.format, clients),
            upload_locations=map(self._upload_locations_pattern.format, clients),
            serializer=self._serializer)

    def _discover_download_clients(self):
        """
        :rtype: collections.Iterable[str]

        """
        sync = self._create_sync(clients=[])
        return sync.list_roots()

    def _infer_upload_clients(self, emails):
        """
        :type emails: collections.Iterable[dict]
        :rtype: collections.OrderedDict[str,list[dict]]

        """
        emails_by_clients = OrderedDict()
        for email in emails:
            for client in self._extract_clients(email):
                emails_by_clients.setdefault(client, []).append(email)
        return emails_by_clients

    def _extract_clients(self, email):
        """
        :type email: dict
        :type: set[str]

        """
        clients = set()
        for email_address in self._get_recipients(email):
            client = self._extract_client(email_address)
            if client is not None:
                clients.add(client)
        return clients

    def _extract_client(self, email_address):
        """
        :type email_address: str
        :rtype: str | None

        """
        host_index = email_address.rfind(self._email_host)
        if host_index == -1:
            return None

        at_index = email_address.rfind('@', 0, host_index)
        if at_index == -1:
            return None

        return email_address[at_index+1:host_index]

    @classmethod
    def _get_recipients(cls, email):
        """
        :type email: dict
        :rtype: collections.Iterable[str]

        """
        return chain(email.get('to', []),
                     email.get('cc', []),
                     email.get('bcc', []))
