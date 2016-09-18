from opwen_cloudserver.state.sql import SqlAccountsStore
from opwen_cloudserver.state.sql import SqlDeliveredEmailsStore
from tests.opwen_cloudserver.state.test_interfaces import Base


class TestSqlAccountsStore(Base.TestAccountsStore):
    store = None

    def setUp(self):
        self.store = SqlAccountsStore(
            database_uri='sqlite://',
            email_host='testhost.ca')


class TestSqlDeliveredEmailsStore(Base.TestDeliveredEmailsStore):
    store = None

    def setUp(self):
        self.store = SqlDeliveredEmailsStore(
            database_uri='sqlite://')
