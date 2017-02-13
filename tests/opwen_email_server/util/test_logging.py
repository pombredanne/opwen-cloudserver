from unittest import TestCase
from unittest.mock import Mock

from opwen_email_server.util.logging import log_execution
from opwen_email_server.util.logging import nameof


def _some_method(arg, kwarg=2):
    return arg * kwarg


class _SomeCallable(object):
    def __call__(self, arg, kwarg=2):
        return _some_method(arg, kwarg=kwarg)


def _some_throw(arg, kwarg=2):
    raise Exception('it threw for %s %s' % (arg, kwarg))


class NameofTests(TestCase):
    def test_nameof_function(self):
        name = nameof(_some_method)
        self.assertEqual(name, '_some_method')

    def test_nameof_callable(self):
        name = nameof(_SomeCallable)
        self.assertEqual(name, '_SomeCallable')


# noinspection PyTypeChecker
class LogExecutionTests(TestCase):
    def test_logger_is_called(self):
        logger = Mock()
        some_method = log_execution(logger)(_some_method)

        some_method('arg')

        self.assertEqual(logger.info.call_count, 2)

    def test_logger_is_called_for_callable_class(self):
        logger = Mock()
        some_method = log_execution(logger)(_SomeCallable())

        some_method('arg')

        self.assertEqual(logger.info.call_count, 2)

    def test_logger_is_called_for_exception(self):
        logger = Mock()
        some_method = log_execution(logger)(_some_throw)

        with self.assertRaises(Exception):
            some_method('arg')

        self.assertEqual(logger.info.call_count, 1)
        self.assertEqual(logger.exception.call_count, 1)
