__author__  = 'Adobe'
__version__ = '2020.1.3'
__all__ = [
    'api_decorators',
    'api_exceptions',
    'api_helpers',
    'autograph',
    'base',
    'batchtools',
    'common_interfaces',
    'compnode',
    'context',
    'freeimagebindings',
    'graph',
    'lzmabindings',
    'mdl',
    'params',
    'psdparser',
    'python_helpers',
    'qtclasses',
    'sbsarchive',
    'sbsbakers',
    'sbscleaner',
    'sbscommon',
    'sbsenum',
    'sbsexporter',
    'sbsgenerator',
    'sbsimpactmanager',
    'sbslibrary',
    'sbspreset',
    'sbsproject',
    'sbsparser',
    'sbswriter',
    'substance',
]

def init_log( ):
    """
    Initialize top-Level module logger
    """
    import os
    import logging

    logger = logging.getLogger( __name__ )

    logger.propagate = False
    logger.setLevel( os.environ.get( "LOGLEVEL", logging.INFO ) )

    formatter = logging.Formatter( '[%(levelname)s][%(name)s] %(message)s' )

    handler = logging.StreamHandler( )
    handler.setFormatter( formatter )

    logger.addHandler( handler )

    return logger

init_log( )

del init_log

from pysbs import python_helpers, api_helpers, api_decorators, api_exceptions, qtclasses, sbsenum, base
from pysbs.batchtools import batchtools
from pysbs import common_interfaces, sbslibrary, sbsbakers
from pysbs import sbsparser, sbswriter, psdparser
from pysbs import sbsgenerator, sbsexporter, sbscleaner, sbsimpactmanager
from pysbs import sbscommon, compnode, params, graph, mdl, substance, sbsarchive, context
from pysbs import autograph
from pysbs import lzmabindings
from pysbs import freeimagebindings
