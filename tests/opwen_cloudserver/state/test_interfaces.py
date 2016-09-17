from abc import abstractproperty
from unittest import TestCase


class TestAccountsStore(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = None
        if self.__class__ != TestAccountsStore:
            # noinspection PyUnresolvedReferences
            self.run = TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda this, *ar, **kw: None

    @abstractproperty
    def accounts_store(self):
        """
        :rtype: opwen_cloudserver.state.AccountsStore

        """
        raise NotImplementedError


class TestDeliveredEmailsStore(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = None
        if self.__class__ != TestDeliveredEmailsStore:
            # noinspection PyUnresolvedReferences
            self.run = TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda this, *ar, **kw: None

    @abstractproperty
    def delivered_emails_store(self):
        """
        :rtype: opwen_cloudserver.state.DeliveredEmailsStore

        """
        raise NotImplementedError
