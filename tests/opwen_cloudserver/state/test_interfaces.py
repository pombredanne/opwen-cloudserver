from abc import abstractproperty
from unittest import TestCase


class TestAccountsStore(TestCase):
    test_client = 'test-client'
    test_user = 'user'
    test_email = 'user@foo.net'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = None
        if self.__class__ != TestAccountsStore:
            # noinspection PyUnresolvedReferences
            self.run = TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda this, *ar, **kw: None

    @abstractproperty
    def store(self):
        """
        :rtype: opwen_cloudserver.state.AccountsStore

        """
        raise NotImplementedError

    def test_get_after_create(self):
        created = self.store.create(self.test_client, self.test_user)
        retrieved = self.store.get(self.test_client, self.test_user)

        self.assertEqual(created, retrieved)

    def test_get_before_create_with_email(self):
        retrieved = self.store.get(self.test_client, self.test_email)
        self.assertEqual(self.test_email, retrieved)

    def test_get_before_create_without_email(self):
        with self.assertRaises(ValueError):
            self.store.get(self.test_client, self.test_user)

    def test_create_with_existing(self):
        self.store.create(self.test_client, self.test_user)
        with self.assertRaises(ValueError):
            self.store.create(self.test_client, self.test_user)


class TestDeliveredEmailsStore(TestCase):
    test_client = 'test-client'
    test_email = {'from': 'foo@test.net',
                  'to': ['bar@test.net'],
                  'subject': 'hi'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = None
        if self.__class__ != TestDeliveredEmailsStore:
            # noinspection PyUnresolvedReferences
            self.run = TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda this, *ar, **kw: None

    @abstractproperty
    def store(self):
        """
        :rtype: opwen_cloudserver.state.DeliveredEmailsStore

        """
        raise NotImplementedError

    def test_contains_after_add(self):
        self.store.add(self.test_client, self.test_email)
        contained = self.store.contains(self.test_client, self.test_email)

        self.assertTrue(contained)

    def test_contains_after_delete(self):
        self.store.add(self.test_client, self.test_email)
        self.store.delete(self.test_client)
        contained = self.store.contains(self.test_client, self.test_email)

        self.assertFalse(contained)
