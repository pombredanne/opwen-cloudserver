from tests.opwen_cloudserver.state.test_interfaces import TestAccountsStore
from tests.opwen_cloudserver.state.test_interfaces import TestDeliveredEmailsStore
from tests.utils.fakes import InMemoryAccountsStore
from tests.utils.fakes import InMemoryDeliveredEmailsStore


class TestInMemoryAccountsStore(TestAccountsStore):
    store = None

    def setUp(self):
        self.store = InMemoryAccountsStore('testhost.ca')


class TestInMemoryDeliveredEmailsStore(TestDeliveredEmailsStore):
    store = None

    def setUp(self):
        self.store = InMemoryDeliveredEmailsStore()
