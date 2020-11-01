# coding: utf-8
from __future__ import absolute_import

import sys
import logging
import unittest

import pysbs
from pysbs.context import Context

if sys.version_info >= ( 3, 4 ):
    from importlib import reload
elif sys.version_info >= ( 3, 0 ):
    from imp import reload

from .utilities import ( logging_messages_interceptor, resetLogging )

class LoggingTestCase(unittest.TestCase):
    """
    This test case is focusing testing pysbs modules logger
    """

    def test_TopLevelLogger(self):
        """
        This test checks that pysbs - i.e. top-module - logger is correctly set.
        """
        self.assertFalse( hasattr( pysbs, 'init_log' ), 'Logging initialization function should not be available' )

        logger = logging.getLogger( 'pysbs' )

        self.assertTrue ( logger.isEnabledFor( logging.INFO ) , 'By default, pysbs logger enables INFO logging level' )
        self.assertFalse( logger.isEnabledFor( logging.DEBUG ), 'By default, pysbs logger enables DEBUG logging level' )

    def test_ContextLogger(self):
        """
        This test checks that pysbs.context logger is correctly set.
        """
        logger = logging.getLogger( 'pysbs.context' )

        self.assertTrue ( logger.isEnabledFor( logging.INFO ) , 'By default, pysbs.context logger enables INFO logging level' )
        self.assertFalse( logger.isEnabledFor( logging.DEBUG ), 'By default, pysbs.context logger enables DEBUG logging level' )

    def test_SbsContextCreation(self):
        """
        This test checks with default settings, logging messages coming from pysbs.context.Context creation are correctly emitted.
        """
        resetLogging( )

        reload( pysbs )
        reload( pysbs.context )

        messages_interceptor = logging_messages_interceptor( )

        logger = logging.getLogger( 'pysbs.context' )
        logger.addHandler( messages_interceptor )

        try:

            with messages_interceptor:
                ctx = pysbs.context.Context( )

                messages_interceptor.assertGreaterMessageCount( self, 0, 'messages are sent by first Context creation, and should be intercepted' )

            """
            Test effect on manually logged messages
            """
            with messages_interceptor:
                logger.debug( 'Debug Message' )

                messages_interceptor.assertEqualMessageCount( self, 0, 'by default, debug message are off, and thus not intercepted' )

            with messages_interceptor:
                logger.info( 'Info Message' )

                messages_interceptor.assertEqualMessageCount( self, 1, 'by default, info message are on, and thus intercepted' )

                lastReceivedMessage = messages_interceptor.interceptedMessages[-1].getMessage( )
                self.assertFalse(
                    lastReceivedMessage.startswith( '[LEVELNAME][NAME] ' ),
                    'pysbs logger formatter should be intact, instead we got {}.'.format( lastReceivedMessage )
                )

            """
            Test effect on manually logged messages on root logger
            """

            with messages_interceptor:
                logging.debug( 'Debug Message' )
                messages_interceptor.assertEqualMessageCount( self, 0, 'pysbs logger should be isolated, and thus not intercept root logger debug message' )

            with messages_interceptor:
                logging.info( 'Info Message' )
                messages_interceptor.assertEqualMessageCount( self, 0, 'pysbs logger should be isolated, and thus not intercept root logger info message' )

        finally:
            logger.removeHandler( messages_interceptor )


if __name__ == '__main__':
    unittest.main()
