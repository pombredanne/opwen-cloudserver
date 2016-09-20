from collections import defaultdict
from contextlib import contextmanager
from os import path
from shutil import rmtree
from tempfile import mkdtemp
from uuid import uuid4
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from azure.storage.blob import BlockBlobService
from jsonlines import jsonlines

from opwen_cloudserver.remotestorage import DownloadResult
from opwen_cloudserver.remotestorage import RemoteStorage


class AzureRemoteStorage(RemoteStorage):
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
            self._download_archive(root, blobname, root_directory)
            download_result = self._load_archive(root_directory)

        return download_result

    @classmethod
    def _load_archive(cls, from_directory):
        """
        :type from_directory: str
        :rtype: DownloadResult

        """
        emails = []
        accounts = set()

        for email in cls._load_emails(from_directory):
            emails.append(email)

            sender = email['from']
            if '@' not in sender:
                accounts.add(sender)

        accounts = [{'name': name} for name in accounts]
        return DownloadResult(accounts=accounts, emails=emails)

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

    def _download_archive(self, root, from_blobname, to_directory):
        """
        :type root: str
        :type from_blobname: str
        :type to_directory: str

        """
        with self._mark_file_for_deletion(root, '.zip') as to_path:
            self._blob.get_blob_to_path(self._container, from_blobname, to_path)

            with ZipFile(to_path, 'r', ZIP_DEFLATED) as archive:
                archive.extractall(to_directory)

        return to_path

    @contextmanager
    def _mark_file_for_deletion(self, root, suffix=''):
        """
        :type root: str
        :type suffix: str | None
        :rtype: str

        """
        with self._mark_for_deletion(root) as directory:
            filepath = path.join(directory, '{}{}'.format(uuid4(), suffix))
            yield filepath

    @contextmanager
    def _mark_for_deletion(self, root, blobname=None):
        """
        :type root: str
        :type blobname: str | None
        :rtype: str

        """
        scratch_directory = mkdtemp()
        yield scratch_directory
        if blobname:
            self._processed_blob_names[root].add(blobname)
        self._processed_local_directories[root].add(scratch_directory)


def _load_jsonl(filepath):
    """
    :type filepath: str
    :rtype: collections.Iterable[dict]

    """
    if not path.isfile(filepath):
        return

    with jsonlines.open(filepath) as fobj:
        for line in fobj:
            yield line


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
