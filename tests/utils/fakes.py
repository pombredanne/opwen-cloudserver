from collections import defaultdict

from opwen_cloudserver.services.remotestorage import DownloadResult
from opwen_cloudserver.services.remotestorage import RemoteStorage

from opwen_cloudserver.services.email import EmailSender
from opwen_cloudserver.state import AccountsStore
from opwen_cloudserver.state import DeliveredEmailsStore
from opwen_cloudserver.state.interfaces import ReceivedEmailsStore


class FakeEmailSender(EmailSender):
    def __init__(self, sent=None):
        """
        :type sent: list[dict]

        """
        self.sent = sent or []

    def send_email(self, email):
        self.sent.append(email)
        return True


class FakeRemoteStorage(RemoteStorage):
    def __init__(self, downloads):
        """
        :type downloads: dict[str, dict[str, list]]

        """
        self._roots = sorted(downloads.keys())
        self._downloads = downloads

    def list_roots(self):
        return self._roots

    def download(self, root):
        return DownloadResult(
            emails=self._downloads.get(root, {}).get('emails', []),
            accounts=self._downloads.get(root, {}).get('accounts', []))

    def delete(self, root):
        self._downloads.pop(root, None)


class InMemoryAccountsStore(AccountsStore):
    def __init__(self, email_host):
        """
        :type email_host: str

        """
        self._store = defaultdict(dict)
        self._email_host = email_host

    def get(self, client_name, user):
        email = self._store[client_name].get(user)
        if email:
            return email
        if '@' not in user:
            raise ValueError
        return user

    def create(self, client_name, username):
        email = self._store[client_name].get(username)
        if email:
            return email

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


class FakeReceivedEmailsStore(ReceivedEmailsStore):
    def __init__(self, email_host):
        """
        :type email_host: str

        """
        self._email_host = email_host

    def add(self, email):
        for client in self._parse_clients(email, self._email_host):
            print('received for client {}: {}'.format(client, email))
