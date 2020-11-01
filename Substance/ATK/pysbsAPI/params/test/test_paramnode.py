# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import sys

from pysbs.api_exceptions import SBSLibraryError
from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import context
from pysbs import substance

testModule = sys.modules[__name__]

class SBSParamNodeTests(unittest.TestCase):

    @staticmethod
    def openTestDocument():
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/Functions.sbs')
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_Parameters(self):
        """
        This test checks getting and setting Parameters on CompNodes
        """
        log.info("Test ParamNode: Parameters")
        sbsDoc = SBSParamNodeTests.openTestDocument()
        aFunction = sbsDoc.getSBSFunction('Function')

        # Case of a filter
        # Check getter
        getFloatNode = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.GET_FLOAT1)[0]
        floatValue = getFloatNode.getParameterValue(sbsenum.FunctionEnum.GET_FLOAT1)
        self.assertIsInstance(floatValue, str)

        aValue = 'myValue'
        self.assertTrue(getFloatNode.setParameterValue(sbsenum.FunctionEnum.GET_FLOAT1, aValue))
        self.assertEqual(getFloatNode.getParameterValue(sbsenum.FunctionEnum.GET_FLOAT1), aValue)

        self.assertTrue(getFloatNode.unsetParameter(sbsenum.FunctionEnum.GET_FLOAT1))
        self.assertEqual(getFloatNode.getParameterValue(sbsenum.FunctionEnum.GET_FLOAT1), '')

        # Check with incorrect values
        with self.assertRaises(SBSLibraryError): getFloatNode.unsetParameter(sbsenum.FunctionEnum.GET_FLOAT3)
        with self.assertRaises(SBSLibraryError): getFloatNode.getParameterValue('InvalidValue')
        with self.assertRaises(SBSLibraryError): getFloatNode.getParameterValue(1000)
        with self.assertRaises(SBSLibraryError): getFloatNode.setParameterValue(sbsenum.FunctionEnum.CONST_FLOAT, '2')
        with self.assertRaises(SBSLibraryError): getFloatNode.setParameterValue('BadParam', '2')
        with self.assertRaises(SBSLibraryError): getFloatNode.setParameterValue(1000, '2')

        log.info("Test ParamNode: Parameters: OK\n")

if __name__ == '__main__':
    unittest.main()
