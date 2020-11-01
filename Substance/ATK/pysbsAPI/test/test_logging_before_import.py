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

class LoggingConfigurationBeforeTestCase(unittest.TestCase):
    """
    This test case is focusing testing pysbs does not conflicts with Python standard library logging configuration
    This test case is separated from `LoggingConfigurationAfterTestCase` to avoid side-effect resulting from calling `logging.basicConfig`
    """

    def test_LoggingBasicConfigCalledBeforeImport(self):
        """
        This test checks with default settings, logging messages coming from pysbs.context.Context creation are correctly emitted.
        Even if logging.basicConfig is called after importing pysbs
        """
        resetLogging( )

        messages_interceptor = logging_messages_interceptor( )

        logger = logging.getLogger( 'pysbs.context' )
        logger.addHandler( messages_interceptor )
        try:
            logging.basicConfig( level=logging.DEBUG, format='[LEVELNAME][NAME] %(message)s' )

            reload( pysbs )
            reload( pysbs.context )

            """
            Test effect on implicit logged messages
            """

            with messages_interceptor:
                Context._Context__computeSATPaths( )
                messages_interceptor.assertGreaterMessageCount( self, 0, 'messages are sent by first Context creation, and should be intercepted' )

                for record in messages_interceptor.interceptedMessages:
                    self.assertFalse(
                        record.getMessage( ).startswith( '[LEVELNAME][NAME] ' ),
                        'pysbs logger formatter should be intact, instead we got {}.'.format( record.getMessage( ) )
                    )

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
