from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple


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
