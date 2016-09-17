from unittest import skipUnless

from config import Config
from opwen_cloudserver.remotestorage.azure import AzureRemoteStorage
from tests.opwen_cloudserver.remotestorage.test_interfaces import TestRemoteStorage


@skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
class TestAzureRemoteStorage(TestRemoteStorage):
    @property
    def remote_storage(self):
        return AzureRemoteStorage(
            account_name=Config.STORAGE_ACCOUNT_NAME,
            account_key=Config.STORAGE_ACCOUNT_KEY,
            container=Config.STORAGE_ACCOUNT_CONTAINER)
