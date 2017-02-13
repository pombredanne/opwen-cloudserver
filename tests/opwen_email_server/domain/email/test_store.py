from itertools import count
from unittest import TestCase
from unittest import skipUnless

from opwen_domain.sync.azure import AzureAuth
from opwen_infrastructure.serialization.json import JsonSerializer
from opwen_tests.config import TestConfig

from opwen_email_server.domain.email.store import AzureEmailStore


@skipUnless(reason='integration tests disabled',
            condition=all((TestConfig.RUN_INTEGRATION_TESTS,
                           TestConfig.AZURE_STORAGE_ACCOUNT_KEY,
                           TestConfig.AZURE_STORAGE_ACCOUNT_NAME,
                           TestConfig.AZURE_STORAGE_ACCOUNT_CONTAINER)))
class AzureEmailStoreTests(TestCase):
    _email1 = {
        'from': 'clemens.wolff@gmail.com',
        'to': ['clemens@vancouver.ascoderu.ca', 'laura@vancouver.ascoderu.ca'],
        'subject': 'azure test',
        'body': '<b>hi from</b> <i>Azure</i>',
    }

    _email2 = {
        'from': 'clemens.wolff@gmail.com',
        'to': ['clemens@vancouver.ascoderu.ca', 'laura@vancouver.ascoderu.ca'],
        'subject': 'azure test part 2',
        'body': '<b>hi from</b> <i>Azure</i> part 2',
    }

    def setUp(self):
        self._counter = count()

    def tearDown(self):
        store = self.create_email_store()
        blob = store._create_storage_client()
        blob.delete_container(store._auth.container)
        table = store._create_search_client()
        table.delete_table(store._pending_table)

    def _create_add_uid(self):
        def patched(email):
            email['_uid'] = '{}'.format(next(self._counter))
            return email
        return patched

    def create_email_store(self):
        """
        :rtype: opwen_domain.email.azure.AzureEmailStore

        """
        auth = AzureAuth(
            container=TestConfig.AZURE_STORAGE_ACCOUNT_CONTAINER,
            account=TestConfig.AZURE_STORAGE_ACCOUNT_NAME,
            key=TestConfig.AZURE_STORAGE_ACCOUNT_KEY)

        email_store = AzureEmailStore(auth=auth, serializer=JsonSerializer())
        email_store._add_uid = self._create_add_uid()

        return email_store

    def test_end_to_end(self):
        email_store = self.create_email_store()

        email_store.create([self._email1])
        pending = list(email_store.pending())
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0], self._email1)

        email_store.mark_sent(pending)
        pending = list(email_store.pending())
        self.assertEqual(len(pending), 0)

        email_store.create([self._email1, self._email2])
        pending = list(email_store.pending())
        self.assertEqual(len(pending), 2)

        pending = list(email_store.pending())
        self.assertEqual(len(pending), 2)
