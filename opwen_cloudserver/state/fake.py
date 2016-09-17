import json
from collections import defaultdict

from opwen_cloudserver.state import AccountsStore
from opwen_cloudserver.state import DeliveredEmailsStore


class InMemoryAccountsStore(AccountsStore):
    def __init__(self, email_host):
        """
        :type email_host: str

        """
        self._store = defaultdict(dict)
        self._email_host = email_host

    def get(self, client_name, user):
        return self._store[client_name].get(user, user)

    def create(self, client_name, username):
        if username in self._store[client_name]:
            raise ValueError

        email = self._format_email(client_name, username, self._email_host)
        self._store[client_name][username] = email
        return email


class InMemoryDeliveredEmailsStore(DeliveredEmailsStore):
    def __init__(self):
        self._store = defaultdict(lambda: defaultdict(bool))

    def add(self, client_name, email):
        email = self._hash_email(email)
        self._store[client_name][email] = True

    def delete(self, client_name):
        self._store.pop(client_name, None)

    def contains(self, client_name, email):
        email = self._hash_email(email)
        return self._store[client_name][email]

    @classmethod
    def _hash_email(cls, email):
        """
        :type email: dict
        :rtype: int

        """
        return hash(json.dumps(email, sort_keys=True))