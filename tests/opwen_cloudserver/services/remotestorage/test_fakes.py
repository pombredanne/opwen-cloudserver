from tests.opwen_cloudserver.services.remotestorage.test_interfaces import Base
from tests.utils.fakes import FakeRemoteStorage


class TestFakeRemoteStorage(Base.TestRemoteStorage):
    @property
    def remote_storage(self):
        return FakeRemoteStorage({
            'test-root': {
                'emails': [{}],
                'accounts': []
            }})
