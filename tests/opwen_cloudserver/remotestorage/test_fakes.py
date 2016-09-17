from tests.opwen_cloudserver.remotestorage.test_interfaces import TestRemoteStorage
from tests.utils.fakes import FakeRemoteStorage


class TestFakeRemoteStorage(TestRemoteStorage):
    @property
    def remote_storage(self):
        return FakeRemoteStorage({
            'test-root': {
                'emails': [{}],
                'accounts': []
            }})
