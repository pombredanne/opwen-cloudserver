from opwen_cloudserver.remotestorage import DownloadResult
from opwen_cloudserver.remotestorage import RemoteStorage


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
