import json
from abc import ABCMeta
from abc import abstractmethod


class AccountsStore(metaclass=ABCMeta):
    @abstractmethod
    def get(self, client_name, email_or_username):
        """
        :type client_name: str
        :type email_or_username: str
        :rtype: str
        :raises ValueError if the user does not have an account

        """
        raise NotImplementedError

    def create(self, client_name, username):
        """
        :type client_name: str
        :type username: str
        :rtype: str
        :raises ValueError if the user's account already exists

        """
        raise NotImplementedError

    @classmethod
    def _format_email(cls, client, user, host):
        """
        :type client: str
        :type user: str
        :type host: str
        :rtype: str

        """
        return '{user}@{client}.{host}'.format(
            user=user,
            client=client,
            host=host)


class DeliveredEmailsStore(metaclass=ABCMeta):
    @abstractmethod
    def contains(self, client_name, email):
        """
        :type client_name: str
        :type email: dict
        :rtype: bool

        """
        raise NotImplementedError

    @abstractmethod
    def add(self, client_name, email):
        """
        :type client_name: str
        :type email: dict

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, client_name):
        """
        :type client_name: str

        """
        raise NotImplementedError

    @classmethod
    def _hash_email(cls, email):
        """
        :type email: dict
        :rtype: int

        """
        return hash(json.dumps(email, sort_keys=True))
