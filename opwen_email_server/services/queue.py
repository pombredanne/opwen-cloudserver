from json import loads

from azure.storage.queue import QueueService
from typing import Callable
from typing import Iterable

from opwen_email_server.utils.log import LogMixin
from opwen_email_server.utils.serialization import to_json


class AzureQueue(LogMixin):
    def __init__(self, account: str, key: str, name: str,
                 client: QueueService=None,
                 factory: Callable[..., QueueService]=QueueService) -> None:

        self._account = account
        self._key = key
        self._name = name
        self.__client = client
        self._client_factory = factory

    @property
    def _client(self) -> QueueService:
        if self.__client is not None:
            return self.__client
        client = self._client_factory(self._account, self._key)
        client.create_queue(self._name)
        self.__client = client
        return client

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def _pack(cls, content: dict) -> str:
        return to_json(content)

    @classmethod
    def _unpack(cls, message: str) -> dict:
        return loads(message)

    def enqueue(self, content: dict):
        message = self._pack(content)
        self._client.put_message(self._name, message)
        self.log_debug('received message')

    # noinspection PyBroadException
    def dequeue(self, batch: int=1, lock_seconds: int=10) -> Iterable[dict]:
        messages = self._client.get_messages(self._name, batch, lock_seconds)
        for message in messages:
            try:
                payload = self._unpack(message.content)
            except Exception:
                self.log_exception('error unpacking message')
                pass
            else:
                try:
                    yield payload
                except Exception:
                    self.log_exception('error processing message payload')
                    continue
            self._client.delete_message(self._name, message.id,
                                        message.pop_receipt)
            self.log_debug('done with message %r, deleting', message.id)

    def extra_log_args(self):
        yield 'queue %s', self._name
