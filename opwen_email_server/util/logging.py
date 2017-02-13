from functools import wraps


def nameof(func_or_call):
    """
    :type func_or_call: typing.Callable
    :rtype: str

    """
    try:
        return func_or_call.__name__
    except AttributeError:
        return func_or_call.__class__.__name__


def log_execution(logger):
    """
    :type logger: logging.Logger

    """
    def decorator(func):
        func_name = nameof(func)

        # noinspection PyBroadException
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info('starting %s', func_name)
            try:
                result = func(*args, **kwargs)
            except Exception:
                logger.exception('exception in %s', func_name, exc_info=True)
                raise
            else:
                logger.info('finished %s', func_name)
                return result
        return wrapper
    return decorator
