# coding: utf-8
"""
Module **utilities** provides class and functions to ease writing test code, and share them across test modules.
"""

import logging

class logging_messages_interceptor( logging.Handler ):
    """Logger testing utilities to catch received messages by acting as a `logging.Handler`.

    Attributes:
        interceptedMessages: list of received logging.LogRecord.

    In addition to acting as a logging handler, it also has testing methods and contextmanager behavior.

    Acting as a context manager, it will monitor received messages for the encompassed scope.
    NOTE: When scope starts, previously received messages are removed.

    Testing method wraps a `unittest.TestCast`, and allows making assertions regarding current received messages state.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.interceptedMessages = [ ]

    def emit( self, record ):
        self.interceptedMessages.append( record )

    def __enter__(self):
        self.interceptedMessages = []

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def assertEqualMessageCount( self, tester, expected, reason ):
        """Test via `tester` if we have received exactly `expected` messages so far. If not, the test will fail.

        Args:
            tester: a testing utility, a la unittest.TestCase.
            expected: expected number of messages.
            reason: failure message to display in case the test fails.

        Raises:
            AssertionError: An error occurred because the test failed.
        """
        tester.assertEqual(
            len( self.interceptedMessages ), expected,
'''
    Exactly {expected} messages expected instead of {result}: {reason}.
    Intercepted messages:\n\t{messages}
'''         .format(
                expected=expected,
                result=len( self.interceptedMessages ),
                reason=reason,
                messages='\n\t'.join( [ _.getMessage( ) for _ in self.interceptedMessages ] )
            )
        )

    def assertGreaterMessageCount( self, tester, expected, reason ):
        """Test via `tester` if we have received at least `expected + 1` messages so far. If not, the test will fail.

        Args:
            tester: a testing utility, a la unittest.TestCase.
            expected: expected number of messages.
            reason: failure message to display in case the test fails.

        Raises:
            AssertionError: An error occurred because the test failed.
        """
        tester.assertGreater(
            len( self.interceptedMessages ), expected,
'''
    More than {expected} messages expected instead got {result} messages: {reason}.
    Intercepted messages:\n\t{messages}
'''         .format(
                expected=expected,
                result=len( self.interceptedMessages ),
                reason=reason,
                messages='\n\t'.join( [ _.getMessage( ) for _ in self.interceptedMessages ] )
            )
        )

def resetLogging( ):
    """Not very nice hack to try to reset the logging Python mdule global state.

    The intent of that method is to reset sufficient logging global state, so that calling logging.basicConfig after it will trigger a new setup
    """
    rootLogger = logging.getLogger( )

    for handler in list( rootLogger.handlers ):
        rootLogger.removeHandler( handler )
