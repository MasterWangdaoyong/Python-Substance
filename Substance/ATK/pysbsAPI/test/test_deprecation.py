from pysbs.api_decorators import deprecated
import logging
import unittest

from .utilities import logging_messages_interceptor


class TestCase(unittest.TestCase):

    def test_deprecatedFunction(self):
        """
        Makes sure a deprecated function reports a warning
        """
        messages_interceptor = logging_messages_interceptor()
        logger = logging.getLogger('pysbs.api_decorators')
        logger.addHandler(messages_interceptor)
        try:
            def a():
                pass

            @deprecated(__name__, '2018.2.0', 'No specific reason', 'use a')
            def b():
                a()
            a()
            messages_interceptor.assertEqualMessageCount(self, 0, 'No message when calling a is expected')
            b()
            messages_interceptor.assertEqualMessageCount(self, 1, 'A one line warning expected when calling b')
        finally:
            logger.removeHandler(messages_interceptor)
