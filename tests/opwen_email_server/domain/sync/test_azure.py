from unittest import TestCase

from opwen_domain.sync.azure import AzureAuth
from opwen_infrastructure.serialization.json import JsonSerializer

from opwen_email_server.domain.sync.azure import MultiClientAzureSync


class MultiClientAzureSyncTests(TestCase):
    @property
    def _sync(self):
        return MultiClientAzureSync(
            auth=AzureAuth('account', 'key', 'container'),
            email_info=('download', 'upload', '.ascoderu.ca'),
            serializer=JsonSerializer())

    def test_extract_client_matching(self):
        client = self._sync._extract_client('foobar@vancouver.ascoderu.ca')
        self.assertEqual(client, 'vancouver')

    def test_extract_client_matching_named(self):
        client = self._sync._extract_client('Foo Bar <foobar@vancouver.ascoderu.ca>')
        self.assertEqual(client, 'vancouver')

    def test_extract_client_not_matching(self):
        client = self._sync._extract_client('foobar@test.com')
        self.assertIsNone(client)

    def test_extract_client_not_matching_named(self):
        client = self._sync._extract_client('Foo Bar <foobar@test.com>')
        self.assertIsNone(client)

    def test_extract_client_not_matching_named_with_at(self):
        client = self._sync._extract_client('Foo B@r <foobar@test.com>')
        self.assertIsNone(client)

    def test_extract_client_matching_named_with_at(self):
        client = self._sync._extract_client('Foo B@r <foobar@vancouver.ascoderu.ca>')
        self.assertEqual(client, 'vancouver')

    def test_extract_client_not_matching_named_with_client(self):
        client = self._sync._extract_client('foobar.ascoderu.ca <foobar@test.com>')
        self.assertIsNone(client)

    def test_extract_client_matching_named_with_client(self):
        client = self._sync._extract_client('foobar.ascoderu.ca <foobar@vancouver.ascoderu.ca>')
        self.assertEqual(client, 'vancouver')
