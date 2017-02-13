import re

from azure.storage.blob import BlockBlobService
from azure.storage.table import TableBatch
from azure.storage.table import TableService

from opwen_domain.email import EmailStore


def _format_table_name(table_name, container):
    """
    :type table_name: str
    :type container: str
    :rtype: str

    """
    container = re.sub("[^a-zA-Z0-9]", "", container)
    return '{}{}'.format(container, table_name)


class AzureEmailStore(EmailStore):
    _is_pending_partition = 'pendingTrue'

    def __init__(self, auth, serializer):
        """
        :type auth: opwen_domain.sync.azure.AzureAuth
        :type serializer: opwen_infrastructure.serialization.Serializer

        """
        self._auth = auth
        self._serializer = serializer
        self._pending_table = _format_table_name('pending', auth.container)

    def _create_storage_client(self):
        """
        :rtype: azure.storage.blob.BlockBlobService

        """
        client = BlockBlobService(self._auth.account, self._auth.key)
        client.create_container(self._auth.container, fail_on_exist=False)
        return client

    def _create_search_client(self):
        """
        :rtype: azure.storage.table.TableService

        """
        client = TableService(self._auth.account, self._auth.key)
        client.create_table(self._pending_table, fail_on_exist=False)
        return client

    def _create(self, emails):
        storage = self._create_storage_client()
        search = self._create_search_client()
        search_batch = TableBatch()

        # todo: do this in parallel
        for email in emails:
            email_id = email['_uid']

            blob_exists = storage.exists(
                container_name=self._auth.container,
                blob_name=email_id)

            if blob_exists:
                continue

            blob = self._serializer.serialize(email)

            storage.create_blob_from_bytes(
                container_name=self._auth.container,
                blob_name=email_id,
                blob=blob)
            search_batch.insert_entity({
                'PartitionKey': self._is_pending_partition,
                'RowKey': email_id,
                'BlobName': email_id,
            })

        search.commit_batch(self._pending_table, search_batch)

    def _find_pending_entities(self, search):
        """
        :type: azure.storage.table.TableService
        :rtype: collections.Iterable[azure.storage.table.Entity]

        """
        query = "PartitionKey eq '{}'".format(self._is_pending_partition)
        entities = search.query_entities(self._pending_table, query)
        return entities

    def pending(self):
        storage = self._create_storage_client()
        search = self._create_search_client()

        # todo: do this in parallel
        for entity in self._find_pending_entities(search):
            blob = storage.get_blob_to_bytes(self._auth.container, entity['BlobName'])
            email = self._serializer.deserialize(blob.content)
            yield email

    def _mark_sent(self, uids):
        uids = frozenset(uids)
        search = self._create_search_client()
        delete_batch = TableBatch()

        for entity in self._find_pending_entities(search):
            if entity['RowKey'] in uids:
                delete_batch.delete_entity(entity['PartitionKey'], entity['RowKey'])

        search.commit_batch(self._pending_table, delete_batch)

    def _mark_read(self, email_address, uids):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def inbox(self, email_address):
        raise NotImplementedError

    def search(self, email_address, query):
        raise NotImplementedError

    def outbox(self, email_address):
        raise NotImplementedError

    def sent(self, email_address):
        raise NotImplementedError

    def get(self, uid):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
