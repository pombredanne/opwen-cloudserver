import json
from abc import ABCMeta
from abc import abstractmethod
from collections import defaultdict
from collections import namedtuple
from contextlib import contextmanager
from os import path
from shutil import rmtree
from tempfile import mkdtemp
from uuid import uuid4
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from azure.storage.blob import BlockBlobService


# noinspection PyClassHasNoInit
class DownloadResult(namedtuple('DownloadResult',
                                'accounts emails')):
    pass


class RemoteStorage(metaclass=ABCMeta):
    @abstractmethod
    def list_roots(self):
        """
        :rtype collections.Iterable[str]

        """
        raise NotImplementedError

    @abstractmethod
    def download(self, root):
        """
        :type root: str
        :rtype DownloadResult

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, root):
        """
        :type root: str

        """
        raise NotImplementedError


class StorageForUploadsFromOpwen(RemoteStorage):
    _upload_prefix = 'from_opwen'

    def __init__(self, account_name, account_key, container):
        self._blob = BlockBlobService(account_name, account_key)
        self._container = container
        self._processed_local_directories = defaultdict(lambda: set())
        self._processed_blob_names = defaultdict(lambda: set())

    def list_roots(self):
        roots = set()
        for blob in self._blob.list_blobs(self._container):
            roots.add(blob.name.split('/')[0])
        return roots

    def delete(self, root):
        for blob_name in _safepop(self._processed_blob_names, root):
            self._blob.delete_blob(self._container, blob_name)
        for directory_path in _safepop(self._processed_local_directories, root):
            rmtree(directory_path)

    def download(self, root):
        accounts = []
        emails = []

        prefix = '{}/{}'.format(root, self._upload_prefix)
        for blob in self._blob.list_blobs(self._container, prefix):
            download_result = self._download_blob(root, blob.name)
            accounts.extend(download_result.accounts)
            emails.extend(download_result.emails)

        return DownloadResult(accounts, emails)

    def _download_blob(self, root, blobname):
        """
        :type root: str
        :type blobname: str
        :rtype: DownloadResult

        """
        with self._mark_for_deletion(root, blobname) as root_directory:
            self._download_archive(blobname, root_directory)
            accounts = self._load_accounts(root_directory)
            emails = self._load_emails(root_directory)

        return DownloadResult(accounts, emails)

    @classmethod
    def _load_emails(cls, from_directory):
        """
        :type from_directory: str
        :rtype: collections.Iterable[dict]

        """
        emails_path = path.join(from_directory, 'emails.jsonl')
        emails = _load_jsonl(emails_path)
        return cls._fixup_emails(from_directory, emails)

    @classmethod
    def _load_accounts(cls, from_directory):
        """
        :type from_directory: str
        :rtype: collections.Iterable[dict]

        """
        accounts_path = path.join(from_directory, 'accounts.jsonl')
        return _load_jsonl(accounts_path)

    @classmethod
    def _fixup_emails(cls, from_directory, emails):
        """
        :type from_directory: str
        :type emails: collections.Iterable[dict]
        :rtype: collections.Iterable[dict]

        """
        for email in emails:
            for attachment in email.get('attachments', []):
                cls._fixup_attachment(from_directory, attachment)
            yield email

    @classmethod
    def _fixup_attachment(cls, from_directory, attachment):
        """
        :type from_directory: str
        :type attachment: dict

        """
        relativepath = attachment.get('relativepath')
        if relativepath:
            attachment['relativepath'] = path.join(from_directory, relativepath)

    def _download_archive(self, from_blobname, to_directory):
        """
        :tryp from_blobname: str
        :tryp to_directory: str

        """
        to_path = path.join(to_directory, str(uuid4()))

        self._blob.get_blob_to_path(self._container, from_blobname, to_path)

        with ZipFile(to_path, 'r', ZIP_DEFLATED) as archive:
            archive.extractall(to_directory)

        return to_path

    @contextmanager
    def _mark_for_deletion(self, root, blobname):
        """
        :type root: str
        :type blobname: str
        :rtype: str

        """
        scratch_directory = mkdtemp()
        yield scratch_directory
        self._processed_blob_names[root].add(blobname)
        self._processed_local_directories[root].add(scratch_directory)


def _load_jsonl(filepath, encoding='utf-8'):
    """
    :type filepath: str
    :type encoding: str
    :rtype: collections.Iterable[dict]

    """
    if not path.isfile(filepath):
        return

    with open(filepath, 'rb') as jsonl:
        for line in jsonl:
            yield json.loads(line.decode(encoding))


def _safepop(d, key):
    """
    :type d: defaultdict[X, Y]
    :type key: X
    :rtype: Y

    """
    try:
        return d.pop(key)
    except KeyError:
        return d.default_factory()
