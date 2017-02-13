from opwen_infrastructure.serialization.json import JsonSerializer
from opwen_tests.opwen_infrastructure.test_serialization import Base

from opwen_email_server.util.serialization.gzip import GzipSerializerDecorator


class GzipSerializerDecoratorTests(Base.SerializerTests):
    def create_serializer(self):
        decorated = JsonSerializer()
        return GzipSerializerDecorator(decorated)
