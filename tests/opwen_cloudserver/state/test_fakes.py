from tests.opwen_cloudserver.state.test_interfaces import Base
from tests.utils.fakes import InMemoryAccountsStore
from tests.utils.fakes import InMemoryDeliveredEmailsStore


class TestInMemoryAccountsStore(Base.TestAccountsStore):
    store = None

    def setUp(self):
        self.store = InMemoryAccountsStore('testhost.ca')


class TestInMemoryDeliveredEmailsStore(Base.TestDeliveredEmailsStore):
    store = None

    def setUp(self):
        self.store = InMemoryDeliveredEmailsStore()
