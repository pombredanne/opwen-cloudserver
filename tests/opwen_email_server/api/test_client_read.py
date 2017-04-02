from contextlib import contextmanager
from os import environ
from unittest import TestCase


class DownloadTests(TestCase):
    def test_denies_unknown_client(self):
        with self._given_clients('{"client1": "id1"}') as download:
            message, status = download('unknown_client')
            self.assertEqual(status, 403)

    @classmethod
    @contextmanager
    def _given_clients(cls, clients: str):
        environ['LOKOLE_CLIENTS'] = clients
        from opwen_email_server.api import client_read
        yield client_read.download
        del client_read