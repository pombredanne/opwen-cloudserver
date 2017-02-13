from gzip import GzipFile
from io import BytesIO

from opwen_infrastructure.serialization import Serializer


def _gunzip(data):
    """
    :type data: bytes
    :type: bytes

    """
    with BytesIO(data) as bytes_file:
        with GzipFile(fileobj=bytes_file, mode='rb') as compressed_file:
            decompressed = compressed_file.read()

    return decompressed


def _gzip(data):
    """
    :type data: bytes
    :rtype: bytes

    """
    with BytesIO() as bytes_file:
        with GzipFile(fileobj=bytes_file, mode='wb') as compressed_file:
            compressed_file.write(data)
        bytes_file.seek(0)
        compressed = bytes_file.read()

    return compressed


class GzipSerializerDecorator(Serializer):
    def __init__(self, wrapped):
        """
        :type wrapped: opwen_infrastructure.serialization.Serializer

        """
        self._wrapped = wrapped

    def deserialize(self, compressed):
        serialized = _gunzip(compressed)
        deserialized = self._wrapped.deserialize(serialized)
        return deserialized

    def serialize(self, obj):
        serialized = self._wrapped.serialize(obj)
        compressed = _gzip(serialized)
        return compressed
