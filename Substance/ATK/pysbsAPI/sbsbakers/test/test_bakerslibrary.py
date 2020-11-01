# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import inspect

from pysbs.api_exceptions import SBSLibraryError
from pysbs import python_helpers

from pysbs.sbsbakers.sbsbakersenum import BakerEnum, BakingStructureTagEnum, ConverterParamEnum, BakerOutputFormatEnum
from pysbs.sbsbakers import BakingParameters
from pysbs.sbsbakers import getBakingStructureTagName, getConverterParamName, \
    getBakerEnum, getBakerDefinition, getBakerOutputFormatName


class BakersLibraryTests(unittest.TestCase):
    @staticmethod
    def isPrivateMember(aMember):
        return isinstance(aMember, tuple) and aMember[0].startswith('__') and aMember[0].endswith('__')

    def test_BakersLibraries(self):
        """
        This test checks consistency between enumerations in sbsenum and libraries in sbsbakerslibrary and sbsbakersdictionaries.
        It also checks the behavior when calling a library related getter with an invalid value.
        """
        enumerations           = [BakerEnum         ]
        objectClassName        = ['BakingConverter' ]
        getDefinitionFunctions = [getBakerDefinition]
        getEnumFunctions       = [getBakerEnum      ]

        # Parse all libraries
        for enumeration, objectClassName, defFunction, enumFunction in \
                zip(enumerations, objectClassName, getDefinitionFunctions, getEnumFunctions):
            log.info('Check library associated to enumeration ' + enumeration.__name__)

            # Retrieve enumeration values
            members = inspect.getmembers(enumeration)
            enumValues = [member for member in members if not BakersLibraryTests.isPrivateMember(member)]

            # Check if all enumeration has its associated definition in the library
            for name, enum in enumValues:
                definition = defFunction(enum)
                self.assertEqual(definition.__class__.__name__, objectClassName)

                if enumFunction is not None:
                    sameDefinition = defFunction(definition.mIdentifier)
                    self.assertEqual(definition, sameDefinition)
                    self.assertEqual(enumFunction(definition.mIdentifier), enum)

            # Check behavior with invalid values
            with self.assertRaises(SBSLibraryError): defFunction('NotAValidName')
            with self.assertRaises(SBSLibraryError): defFunction(1000)
            with self.assertRaises(SBSLibraryError): defFunction(members)
            with self.assertRaises(SBSLibraryError): defFunction(self)

            if enumFunction is not None:
                self.assertIsNone(enumFunction('NotAValidName'))
                with self.assertRaises(SBSLibraryError): enumFunction(1000)
                with self.assertRaises(SBSLibraryError): enumFunction(members)
                with self.assertRaises(SBSLibraryError): enumFunction(self)

    def test_BakersDictionaries(self):
        """
        This test checks consistency between enumerations in sbsenum and dictionaries in sbsbakerslibrary and sbsbakersdictionaries.
        It also checks the behavior when calling a dictionary related getter with an invalid value.
        """
        enumerations =     [BakingStructureTagEnum,    ConverterParamEnum,                         BakerOutputFormatEnum]
        getNameFunctions = [getBakingStructureTagName, [getConverterParamName], getBakerOutputFormatName]

        # Parse all dictionaries
        for enumeration, getNameFunction in zip(enumerations, getNameFunctions):
            log.info('Check dictionary associated to enumeration ' + enumeration.__name__)
            # Retrieve enumeration values
            members = inspect.getmembers(enumeration)
            enumValues = [member for member in members if not BakersLibraryTests.isPrivateMember(member)]

            if not isinstance(getNameFunction, list):
                getNameFunction = [getNameFunction]

            # Check that all enumeration has an entry in the dictionary
            for name, enum in enumValues:
                dictName = None
                for fct in getNameFunction:
                    try:
                        dictName = fct(enum)
                        break
                    except:
                        pass
                self.assertIsNotNone(dictName)
                self.assertTrue(python_helpers.isStringOrUnicode(dictName))

            # Check behavior with invalid values
            for fct in getNameFunction:
                with self.assertRaises(SBSLibraryError): fct('NotAValidName')
                with self.assertRaises(SBSLibraryError): fct(1000)
                with self.assertRaises(SBSLibraryError): fct(members)
                with self.assertRaises(SBSLibraryError): fct(self)

    def test_BakersParameters(self):
        """
        This test checks the return value of getters of parameters on CompNodeParam and FunctionParam classes.
        It also checks the behavior when calling these getters with an invalid value.
        """
        bp = BakingParameters()
        AO_Def = bp.addBaker(BakerEnum.AMBIENT_OCCLUSION)
        AO_Param = AO_Def.getParameter(ConverterParamEnum.SEAO__DISTANCE_FADE)
        self.assertEqual(AO_Param.__class__.__name__, 'BakingConverterParam')

        self.assertIsNone(AO_Def.getParameter(ConverterParamEnum.CURVATURE__SEAMS_POWER))
        self.assertIsNone(AO_Def.getParameter(ConverterParamEnum.DETAIL_AO__ATTENUATION))
        with self.assertRaises(SBSLibraryError): AO_Def.getParameter('NotAValidName')
        with self.assertRaises(SBSLibraryError): AO_Def.getParameter(1000)
        with self.assertRaises(SBSLibraryError): AO_Def.getParameter(self)


if __name__ == '__main__':
    log.info("Test Bakers Library")
    unittest.main()
