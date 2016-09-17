from abc import ABCMeta
from abc import abstractproperty
from os import path
from unittest import TestCase
from unittest import skipUnless

from config import Config
from opwen_cloudserver.remotestorage.azure import StorageForUploadsFromOpwen


# noinspection PyUnresolvedReferences,PyPep8Naming
class RemoteStorageTestCase(metaclass=ABCMeta):
    @abstractproperty
    def remote_storage(self):
        """
        :rtype: opwen_cloudserver.remotestorage.RemoteStorage

        """
        raise NotImplementedError

    def assertIsNotEmpty(self, collection):
        """
        :type collection: collections.Sized

        """
        self.assertIsNotNone(collection)
        self.assertGreater(len(collection), 0, 'collection is empty')

    def assertFileExists(self, filepath):
        """
        :type filepath: str

        """
        self.assertTrue(path.isfile(filepath),
                        'file {} does not exist'.format(filepath))

    def assertAllAttachmentsExist(self, emails):
        """
        :type emails: collections.Iterable[dict]

        """
        for email in emails:
            for attachment in email.get('attachments', []):
                self.assertFileExists(attachment.get('relativepath'))

    def test_list_roots(self):
        roots = self.remote_storage.list_roots()

        self.assertIsNotEmpty(roots)

    def test_download(self):
        root = self.remote_storage.list_roots().pop()
        downloaded = self.remote_storage.download(root)

        self.assertIsNotNone(downloaded.accounts)
        self.assertIsNotEmpty(downloaded.emails)
        self.assertAllAttachmentsExist(downloaded.emails)


@skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
class TestStorageForUploadsFromOpwen(RemoteStorageTestCase, TestCase):
    @property
    def remote_storage(self):
        return StorageForUploadsFromOpwen(
            account_name=Config.STORAGE_ACCOUNT_NAME,
            account_key=Config.STORAGE_ACCOUNT_KEY,
            container=Config.STORAGE_ACCOUNT_CONTAINER)
