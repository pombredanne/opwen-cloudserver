from abc import ABCMeta
from abc import abstractmethod


class EmailSender(metaclass=ABCMeta):
    @abstractmethod
    def send_email(self, email):
        """
        :type email: dict

        """
        raise NotImplementedError
