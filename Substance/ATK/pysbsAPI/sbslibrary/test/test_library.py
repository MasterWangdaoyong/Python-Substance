# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import inspect

from pysbs.api_exceptions import SBSLibraryError
from pysbs import python_helpers
from pysbs import context, sbsgenerator

from pysbs.sbsenum import FilterEnum, FunctionEnum, FxMapNodeEnum, WidgetEnum, WidgetTypeEnum, WidgetOptionEnum, \
    AttributesEnum, InputEnum, OutputEnum, CompNodeParamEnum, FunctionInputEnum, UsageEnum, ComponentsEnum, \
    GraphTemplateEnum, ColorSpacesEnum

from pysbs.sbslibrary import CompNodeDef, FxMapNodeDef, FunctionDef, InputParamWidget, \
    CompNodeInput, CompNodeOutput, FunctionInput, FunctionOutput, CompNodeParam, FunctionParam, \
    getFilterDefinition, getFunctionDefinition, getFxMapNodeDefinition, getDefaultWidget, \
    getFilterEnum, getFunctionEnum, getFxMapNodeEnum, getColorSpace, getColorSpaceEnum, \
    getInputBridgeDefinition, getOutputBridgeDefinition, \
    getUsage, getComponents, getAttribute, getCompNodeInput, getCompNodeOutput, getCompNodeParam, getFunctionInput, getFunctionOutput, \
    getWidgetName, getWidgetOptionName, getSubstanceGraphTemplatePath


class LibraryTests(unittest.TestCase):
    @staticmethod
    def isPrivateMember(aMember):
        return isinstance(aMember, tuple) and aMember[0].startswith('__') and aMember[0].endswith('__')

    def test_Libraries(self):
        """
        This test checks consistency between enumerations in sbsenum and libraries in sbslibrary.
        It also checks the behavior when calling a library related getter with an invalid value.
        """
        enumerations           = [FilterEnum,          FunctionEnum,          FxMapNodeEnum         , WidgetEnum       ]
        objectDefinitions      = [CompNodeDef,         FunctionDef,           FxMapNodeDef          , InputParamWidget ]
        getDefinitionFunctions = [getFilterDefinition, getFunctionDefinition, getFxMapNodeDefinition, getDefaultWidget ]
        getEnumFunctions       = [getFilterEnum,       getFunctionEnum,       getFxMapNodeEnum      , None             ]

        # Parse all libraries
        for enumeration, objectDef, defFunction, enumFunction in \
                zip(enumerations, objectDefinitions, getDefinitionFunctions, getEnumFunctions):
            log.info('\nCheck library associated to enumeration ' + enumeration.__name__)

            # Retrieve enumeration values
            members = inspect.getmembers(enumeration)
            enumValues = [member for member in members if not LibraryTests.isPrivateMember(member)]

            # Check if all enumeration has its associated definition in the library
            for name, enum in enumValues:
                definition = defFunction(enum)
                self.assertIsInstance(definition, objectDef)

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

        # Check input & output bridge
        self.assertIsInstance(getInputBridgeDefinition(), CompNodeDef)
        self.assertIsInstance(getOutputBridgeDefinition(), CompNodeDef)


    def test_Dictionaries(self):
        """
        This test checks consistency between enumerations in sbsenum and dictionaries in sbslibrary.
        It also checks the behavior when calling a dictionary related getter with an invalid value.
        """
        enumerations = [(AttributesEnum, getAttribute, None),
                        (InputEnum, getCompNodeInput, None),
                        (OutputEnum, getCompNodeOutput, None),
                        (CompNodeParamEnum, getCompNodeParam, None),
                        (FunctionInputEnum, getFunctionInput, None),
                        (UsageEnum, getUsage, None),
                        (ComponentsEnum, getComponents, None),
                        (WidgetTypeEnum, getWidgetName, None),
                        (WidgetOptionEnum, getWidgetOptionName, None),
                        (GraphTemplateEnum, getSubstanceGraphTemplatePath, None),
                        (ColorSpacesEnum, getColorSpace, getColorSpaceEnum)]
        # Parse all dictionaries
        for enumeration, getNameFunction, getEnumFunction in enumerations:
            log.info('Check dictionary associated to enumeration %s', enumeration.__name__)
            # Retrieve enumeration values
            members = inspect.getmembers(enumeration)
            enumValues = [member for member in members if not LibraryTests.isPrivateMember(member)]

            # Check that all enumeration has an entry in the dictionary
            for name, enum in enumValues:
                dictName = getNameFunction(enum)
                self.assertTrue(python_helpers.isStringOrUnicode(dictName))
                # If we have a mapping from string to enum, make sure it gives the right result
                if getEnumFunction:
                    self.assertEqual(getEnumFunction(dictName), enum)
            # Check behavior with invalid values
            with self.assertRaises(SBSLibraryError): getNameFunction('NotAValidName')
            with self.assertRaises(SBSLibraryError): getNameFunction(1000)
            with self.assertRaises(SBSLibraryError): getNameFunction(members)
            with self.assertRaises(SBSLibraryError): getNameFunction(self)


    def test_Parameters(self):
        """
        This test checks the return value of getters of parameters on CompNodeParam and FunctionParam classes.
        It also checks the behavior when calling these getters with an invalid value.
        """
        filterDef = getFilterDefinition(FilterEnum.BITMAP)
        self.assertIsInstance(filterDef.getParameter(CompNodeParamEnum.PIXEL_SIZE), CompNodeParam)
        self.assertIsInstance(filterDef.getParameter(CompNodeParamEnum.PIXEL_RATIO), CompNodeParam)
        self.assertIsInstance(filterDef.getParameter(CompNodeParamEnum.BITMAP_RESOURCE_PATH), CompNodeParam)
        self.assertIsInstance(filterDef.getParameter(getCompNodeParam(CompNodeParamEnum.COLOR_MODE)), CompNodeParam)
        self.assertIsInstance(filterDef.getParameter(getCompNodeParam(CompNodeParamEnum.BITMAP_RESIZE_METHOD)), CompNodeParam)

        self.assertIsNone(filterDef.getParameter(CompNodeParamEnum.FX_SELECTOR))
        self.assertIsNone(filterDef.getParameter(getCompNodeParam(CompNodeParamEnum.FX_PATTERN_OFFSET)))
        self.assertIsNone(filterDef.getParameter('NotAValidName'))
        with self.assertRaises(SBSLibraryError): filterDef.getParameter(1000)
        with self.assertRaises(SBSLibraryError): filterDef.getParameter(self)


        fxmapDef = getFxMapNodeDefinition(FxMapNodeEnum.QUADRANT)
        self.assertIsInstance(fxmapDef.getParameter(CompNodeParamEnum.FX_BRANCH_OFFSET), CompNodeParam)
        self.assertIsInstance(fxmapDef.getParameter(getCompNodeParam(CompNodeParamEnum.FX_PATTERN_OFFSET)), CompNodeParam)

        self.assertIsNone(fxmapDef.getParameter(CompNodeParamEnum.COLOR_MODE))
        self.assertIsNone(fxmapDef.getParameter(CompNodeParamEnum.PIXEL_SIZE))
        self.assertIsNone(fxmapDef.getParameter(getCompNodeParam(CompNodeParamEnum.ALPHA_BLENDING)))
        self.assertIsNone(fxmapDef.getParameter('NotAValidName'))
        with self.assertRaises(SBSLibraryError): filterDef.getParameter(1000)
        with self.assertRaises(SBSLibraryError): filterDef.getParameter(self)


        functionDef = getFunctionDefinition(FunctionEnum.CONST_FLOAT3)
        self.assertIsInstance(functionDef.getParameter(FunctionEnum.CONST_FLOAT3), FunctionParam)
        self.assertIsInstance(functionDef.getParameter(getFunctionDefinition(FunctionEnum.CONST_FLOAT3).mIdentifier), FunctionParam)

        self.assertIsNone(functionDef.getParameter(FunctionEnum.CONST_FLOAT))
        self.assertIsNone(functionDef.getParameter(getFunctionDefinition(FunctionEnum.CONST_FLOAT2).mIdentifier))
        self.assertIsNone(functionDef.getParameter('NotAValidName'))
        with self.assertRaises(SBSLibraryError): functionDef.getParameter(1000)
        with self.assertRaises(SBSLibraryError): functionDef.getParameter(self)


        functionDef = getFunctionDefinition(FunctionEnum.ADD)
        self.assertIsNone(functionDef.getParameter(FunctionEnum.ADD))


    def test_Inputs(self):
        """
        This test checks the return value of getters of inputs on CompNodeParam and FunctionParam classes.
        It also checks the behavior when calling these getters with an invalid value.
        """
        filterDef = getFilterDefinition(FilterEnum.BLEND)
        self.assertIsInstance(filterDef.getInput(InputEnum.DESTINATION), CompNodeInput)
        self.assertIsInstance(filterDef.getInput(getCompNodeInput(InputEnum.SOURCE)), CompNodeInput)

        self.assertIsNone(filterDef.getInput(InputEnum.BACKGROUND))
        self.assertIsNone(filterDef.getInput(getCompNodeInput(InputEnum.INPUT_GRADIENT)))
        with self.assertRaises(SBSLibraryError): filterDef.getInput(1000)
        with self.assertRaises(SBSLibraryError): filterDef.getInput(self)

        fxmapDef = getFxMapNodeDefinition(FxMapNodeEnum.QUADRANT)
        self.assertIsInstance(fxmapDef.getParameter(CompNodeParamEnum.FX_BRANCH_OFFSET), CompNodeParam)
        self.assertIsNone(fxmapDef.getParameter(CompNodeParamEnum.COLOR_MODE))
        self.assertIsNone(fxmapDef.getParameter(CompNodeParamEnum.PIXEL_SIZE))

        functionDef = getFunctionDefinition(FunctionEnum.CONST_FLOAT3)
        self.assertIsInstance(functionDef.getParameter(FunctionEnum.CONST_FLOAT3), FunctionParam)
        self.assertIsNone(functionDef.getParameter(FunctionEnum.CONST_FLOAT))

        functionDef = getFunctionDefinition(FunctionEnum.ADD)
        self.assertIsNone(functionDef.getParameter(FunctionEnum.CONST_FLOAT3))
        self.assertIsNone(functionDef.getParameter(FunctionEnum.ADD))


    def test_Outputs(self):
        """
        This test checks the return value of getters of outputs on CompNodeParam class.
        It also checks the behavior when calling these getters with an invalid value.
        """
        filterDef = getFilterDefinition(FilterEnum.DISTANCE)
        self.assertIsInstance(filterDef.getOutput(OutputEnum.OUTPUT), CompNodeOutput)
        self.assertIsInstance(filterDef.getOutput(getCompNodeOutput(OutputEnum.OUTPUT)), CompNodeOutput)

        self.assertIsNone(filterDef.getOutput(OutputEnum.OUTPUT1))
        self.assertIsNone(filterDef.getOutput(getCompNodeOutput(OutputEnum.OUTPUT2)))
        with self.assertRaises(SBSLibraryError): filterDef.getOutput(1000)
        with self.assertRaises(SBSLibraryError): filterDef.getOutput(self)


        fxmapDef = getFxMapNodeDefinition(FxMapNodeEnum.ITERATE)
        self.assertIsInstance(fxmapDef.getOutput(OutputEnum.OUTPUT1), CompNodeOutput)
        self.assertIsInstance(fxmapDef.getOutput(getCompNodeOutput(OutputEnum.OUTPUT0)), CompNodeOutput)
        self.assertIsNone(fxmapDef.getParameter(OutputEnum.OUTPUT))
        self.assertIsNone(filterDef.getOutput(getCompNodeOutput(OutputEnum.OUTPUT3)))


    def test_Definitions(self):
        """
        This test checks getting the definition and identifiers of CompNodeDef, FxMapNodeDef and FunctionDef
        """
        # Filter BLEND
        filterDef = getFilterDefinition(FilterEnum.BLEND)
        self.assertIsInstance(filterDef, CompNodeDef)
        # - identifier
        self.assertEqual(filterDef.getIdentifier(), getFilterDefinition(FilterEnum.BLEND).mIdentifier)
        # - inputs
        inputs = [InputEnum.SOURCE, InputEnum.DESTINATION, InputEnum.OPACITY]
        inputList = filterDef.getAllInputs()
        inputIdentifierList = filterDef.getAllInputIdentifiers()
        self.assertEqual(len(inputList), len(inputs))
        self.assertEqual(len(inputIdentifierList), len(inputs))
        for i,aInput in enumerate(inputs):
            self.assertEqual(filterDef.mInputs[i].getIdentifier(), aInput)
            self.assertEqual(filterDef.mInputs[i].getIdentifierStr(), getCompNodeInput(aInput))
            self.assertEqual(filterDef.mInputs[i].getIdentifierStr(), inputIdentifierList[i])

        # - outputs
        outputs = [OutputEnum.OUTPUT]
        outputList = filterDef.getAllOutputs()
        outputIdentifierList = filterDef.getAllOutputIdentifiers()
        self.assertEqual(len(outputList), len(outputs))
        self.assertEqual(len(outputIdentifierList), len(outputs))
        for i,aOutput in enumerate(outputs):
            self.assertEqual(filterDef.mOutputs[i].getIdentifier(), aOutput)
            self.assertEqual(filterDef.mOutputs[i].getIdentifierStr(), getCompNodeOutput(aOutput))
            self.assertEqual(filterDef.mOutputs[i].getIdentifierStr(), outputIdentifierList[i])

        # - parameters
        params = [CompNodeParamEnum.OPACITY, CompNodeParamEnum.ALPHA_BLENDING, CompNodeParamEnum.BLENDING_MODE,
                  CompNodeParamEnum.CROPPING_AREA, CompNodeParamEnum.OUTPUT_SIZE, CompNodeParamEnum.OUTPUT_FORMAT,
                  CompNodeParamEnum.PIXEL_SIZE, CompNodeParamEnum.PIXEL_RATIO, CompNodeParamEnum.TILING_MODE,
                  CompNodeParamEnum.QUALITY, CompNodeParamEnum.RANDOM_SEED]
        paramList = filterDef.getAllParameters()
        paramIdentifierList = filterDef.getAllParameterIdentifiers()
        self.assertEqual(len(paramList), len(params))
        self.assertEqual(len(paramIdentifierList), len(params))
        for i,aParam in enumerate(params):
            self.assertEqual(filterDef.mParameters[i].getIdentifier(), aParam)
            self.assertEqual(filterDef.mParameters[i].getIdentifierStr(), getCompNodeParam(aParam))
            self.assertEqual(filterDef.mParameters[i].getIdentifierStr(), paramIdentifierList[i])

        aInput = filterDef.getInput(InputEnum.DESTINATION)
        self.assertIsInstance(aInput, CompNodeInput)
        aInput = filterDef.getInput('opacity')
        self.assertIsInstance(aInput, CompNodeInput)
        aInput = filterDef.getInput('Invalid')
        self.assertIsNone(aInput)
        aOutput = filterDef.getOutput(OutputEnum.OUTPUT)
        self.assertIsInstance(aOutput, CompNodeOutput)
        aOutput = filterDef.getOutput('output')
        self.assertIsInstance(aOutput, CompNodeOutput)
        aOutput = filterDef.getOutput('Invalid')
        self.assertIsNone(aOutput)
        aParam = filterDef.getParameter('blendingmode')
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = filterDef.getParameter(CompNodeParamEnum.OPACITY)
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = filterDef.getParameter(CompNodeParamEnum.OUTPUT_SIZE)
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = filterDef.getParameter('Invalid')
        self.assertIsNone(aParam)


        # FxMap node QUADRANT
        fxDef = getFxMapNodeDefinition(FxMapNodeEnum.QUADRANT)
        self.assertIsInstance(fxDef, FxMapNodeDef)
        # - identifier
        self.assertEqual(fxDef.getIdentifier(), getFxMapNodeDefinition(FxMapNodeEnum.QUADRANT).mIdentifier)
        # - inputs
        inputs = [InputEnum.INPUT]
        inputList = fxDef.getAllInputs()
        inputIdentifierList = fxDef.getAllInputIdentifiers()
        self.assertEqual(len(inputList), len(inputs))
        self.assertEqual(len(inputIdentifierList), len(inputs))
        for i,aInput in enumerate(inputs):
            self.assertEqual(fxDef.mInputs[i].getIdentifier(), aInput)
            self.assertEqual(fxDef.mInputs[i].getIdentifierStr(), getCompNodeInput(aInput))
            self.assertEqual(fxDef.mInputs[i].getIdentifierStr(), inputIdentifierList[i])

        # - outputs
        outputs = [OutputEnum.OUTPUT0, OutputEnum.OUTPUT1, OutputEnum.OUTPUT2, OutputEnum.OUTPUT3]
        outputList = fxDef.getAllOutputs()
        outputIdentifierList = fxDef.getAllOutputIdentifiers()
        self.assertEqual(len(outputList), len(outputs))
        self.assertEqual(len(outputIdentifierList), len(outputs))
        for i,aOutput in enumerate(outputs):
            self.assertEqual(fxDef.mOutputs[i].getIdentifier(), aOutput)
            self.assertEqual(fxDef.mOutputs[i].getIdentifierStr(), getCompNodeOutput(aOutput))
            self.assertEqual(fxDef.mOutputs[i].getIdentifierStr(), outputIdentifierList[i])

        # - parameters
        params = [CompNodeParamEnum.FX_COLOR_LUM, CompNodeParamEnum.FX_BRANCH_OFFSET, CompNodeParamEnum.FX_PATTERN_TYPE,
                  CompNodeParamEnum.FX_PATTERN_OFFSET, CompNodeParamEnum.FX_PATTERN_SIZE, CompNodeParamEnum.FX_PATTERN_ROTATION,
                  CompNodeParamEnum.FX_PATTERN_VARIATION, CompNodeParamEnum.FX_BLENDING_MODE, CompNodeParamEnum.FX_RANDOM_SEED,
                  CompNodeParamEnum.FX_RANDOM_INHERITED, CompNodeParamEnum.FX_IMAGE_INDEX, CompNodeParamEnum.FX_IMAGE_ALPHA_PREMUL,
                  CompNodeParamEnum.FX_IMAGE_FILTERING]
        paramList = fxDef.getAllParameters()
        paramIdentifierList = fxDef.getAllParameterIdentifiers()
        self.assertEqual(len(paramList), len(params))
        self.assertEqual(len(paramIdentifierList), len(params))
        for i,aParam in enumerate(params):
            self.assertEqual(fxDef.mParameters[i].getIdentifier(), aParam)
            self.assertEqual(fxDef.mParameters[i].getIdentifierStr(), getCompNodeParam(aParam))
            self.assertEqual(fxDef.mParameters[i].getIdentifierStr(), paramIdentifierList[i])

        aInput = fxDef.getInput(InputEnum.INPUT)
        self.assertIsInstance(aInput, CompNodeInput)
        aInput = fxDef.getInput('input')
        self.assertIsInstance(aInput, CompNodeInput)
        aInput = fxDef.getInput('Invalid')
        self.assertIsNone(aInput)
        aOutput = fxDef.getOutput(OutputEnum.OUTPUT0)
        self.assertIsInstance(aOutput, CompNodeOutput)
        aOutput = fxDef.getOutput('output0')
        self.assertIsInstance(aOutput, CompNodeOutput)
        aOutput = fxDef.getOutput('Invalid')
        self.assertIsNone(aOutput)
        aParam = fxDef.getParameter('imagepremul')
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = fxDef.getParameter(CompNodeParamEnum.FX_COLOR_LUM)
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = fxDef.getParameter('Invalid')
        self.assertIsNone(aParam)
        aParam = fxDef.getParameter(CompNodeParamEnum.OUTPUT_SIZE)
        self.assertIsNone(aParam)


        # Function SET
        fctDef = getFunctionDefinition(FunctionEnum.SET)
        self.assertIsInstance(fctDef, FunctionDef)
        # - identifier
        self.assertEqual(fctDef.getIdentifier(), getFunctionDefinition(FunctionEnum.SET).mIdentifier)
        # - inputs
        inputs = [FunctionInputEnum.VALUE]
        inputList = fctDef.getAllInputs()
        inputIdentifierList = fctDef.getAllInputIdentifiers()
        self.assertEqual(len(inputList), len(inputs))
        self.assertEqual(len(inputIdentifierList), len(inputs))
        for i,aInput in enumerate(inputs):
            self.assertEqual(fctDef.mInputs[i].getIdentifier(), aInput)
            self.assertEqual(fctDef.mInputs[i].getIdentifierStr(), getFunctionInput(aInput))
            self.assertEqual(fctDef.mInputs[i].getIdentifierStr(), inputIdentifierList[i])

        self.assertEqual(fctDef.mInputs[0].getIdentifier(), FunctionInputEnum.VALUE)
        self.assertEqual(fctDef.mInputs[0].getIdentifierStr(), getFunctionInput(FunctionInputEnum.VALUE))

        # - outputs
        outputs = [OutputEnum.OUTPUT]
        outputList = fctDef.getAllOutputs()
        outputIdentifierList = fctDef.getAllOutputIdentifiers()
        self.assertEqual(len(outputList), len(outputs))
        self.assertEqual(len(outputIdentifierList), len(outputs))
        for i,aOutput in enumerate(outputs):
            self.assertEqual(fctDef.mOutputs[i].getIdentifier(), aOutput)
            self.assertEqual(fctDef.mOutputs[i].getIdentifierStr(), getFunctionOutput(aOutput))
            self.assertEqual(fctDef.mOutputs[i].getIdentifierStr(), outputIdentifierList[i])

        # - parameters
        params = [FunctionEnum.SET]
        paramList = fctDef.getAllParameters()
        paramIdentifierList = fctDef.getAllParameterIdentifiers()
        self.assertEqual(len(paramList), len(params))
        self.assertEqual(len(paramIdentifierList), len(params))
        for i,aParam in enumerate(params):
            self.assertEqual(fctDef.mFunctionDatas[i].getIdentifier(), aParam)
            self.assertEqual(fctDef.mFunctionDatas[i].getIdentifierStr(), getFunctionDefinition(aParam).mIdentifier)
            self.assertEqual(fctDef.mFunctionDatas[i].getIdentifierStr(), paramIdentifierList[i])

        aInput = fctDef.getInput(FunctionInputEnum.VALUE)
        self.assertIsInstance(aInput, FunctionInput)
        aInput = fctDef.getInput('value')
        self.assertIsInstance(aInput, FunctionInput)
        aInput = fctDef.getInput('Invalid')
        self.assertIsNone(aInput)
        aOutput = fctDef.getOutput(OutputEnum.OUTPUT)
        self.assertIsInstance(aOutput, FunctionOutput)
        aOutput = fctDef.getOutput('output')
        self.assertIsInstance(aOutput, FunctionOutput)
        aOutput = fctDef.getOutput('Invalid')
        self.assertIsNone(aOutput)
        aParam = fctDef.getParameter('set')
        self.assertIsInstance(aParam, FunctionParam)
        aParam = fctDef.getParameter(FunctionEnum.SET)
        self.assertIsInstance(aParam, FunctionParam)
        aParam = fctDef.getParameter('Invalid')
        self.assertIsNone(aParam)


        # Instance of emboss_with_gloss
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath='test.sbs', aGraphIdentifier='Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        aInstance= aGraph.createCompInstanceNodeFromPath(sbsDoc, 'sbs://emboss_with_gloss.sbs')
        instanceDef = aInstance.getDefinition()
        # - identifier
        self.assertEqual(instanceDef.getIdentifier(), getFilterDefinition(FilterEnum.COMPINSTANCE).mIdentifier)
        # - inputs
        inputs = ['Source', 'Height']
        inputList = instanceDef.getAllInputs()
        inputIdentifierList = instanceDef.getAllInputIdentifiers()
        self.assertEqual(len(inputList), len(inputs))
        self.assertEqual(len(inputIdentifierList), len(inputs))
        for i,aInput in enumerate(inputs):
            self.assertEqual(instanceDef.mInputs[i].getIdentifier(), aInput)
            self.assertEqual(instanceDef.mInputs[i].getIdentifierStr(), aInput)
            self.assertEqual(instanceDef.mInputs[i].getIdentifierStr(), inputIdentifierList[i])

        # - outputs
        outputs = ['Emboss_With_Gloss']
        outputList = instanceDef.getAllOutputs()
        outputIdentifierList = instanceDef.getAllOutputIdentifiers()
        self.assertEqual(len(outputList), len(outputs))
        self.assertEqual(len(outputIdentifierList), len(outputs))
        for i,aOutput in enumerate(outputs):
            self.assertEqual(instanceDef.mOutputs[i].getIdentifier(), aOutput)
            self.assertEqual(instanceDef.mOutputs[i].getIdentifierStr(), aOutput)
            self.assertEqual(instanceDef.mOutputs[i].getIdentifierStr(), outputIdentifierList[i])

        # - parameters
        params = [CompNodeParamEnum.OUTPUT_SIZE, CompNodeParamEnum.OUTPUT_FORMAT, CompNodeParamEnum.PIXEL_SIZE,
                  CompNodeParamEnum.PIXEL_RATIO, CompNodeParamEnum.TILING_MODE, CompNodeParamEnum.QUALITY,
                  CompNodeParamEnum.RANDOM_SEED, 'HighlightColor', 'ShadowColor', 'Gloss',
                  'Intensity', 'LightAngle']
        paramList = instanceDef.getAllParameters()
        paramIdentifierList = instanceDef.getAllParameterIdentifiers()
        self.assertEqual(len(paramList), len(params))
        self.assertEqual(len(paramIdentifierList), len(params))
        for i in range(7):
            self.assertEqual(instanceDef.mParameters[i].getIdentifier(), params[i])
            self.assertEqual(instanceDef.mParameters[i].getIdentifierStr(), getCompNodeParam(params[i]))
            self.assertEqual(instanceDef.mParameters[i].getIdentifierStr(), paramIdentifierList[i])
        for i in range(7,12):
            self.assertEqual(instanceDef.mParameters[i].getIdentifier(), params[i])
            self.assertEqual(instanceDef.mParameters[i].getIdentifierStr(), params[i])
            self.assertEqual(instanceDef.mParameters[i].getIdentifierStr(), paramIdentifierList[i])

        aInput = instanceDef.getInput('Source')
        self.assertIsInstance(aInput, CompNodeInput)
        aInput = instanceDef.getInput('Invalid')
        self.assertIsNone(aInput)
        aOutput = instanceDef.getOutput('Emboss_With_Gloss')
        self.assertIsInstance(aOutput, CompNodeOutput)
        aOutput = instanceDef.getOutput('Invalid')
        self.assertIsNone(aOutput)
        aParam = instanceDef.getParameter('HighlightColor')
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = instanceDef.getParameter(CompNodeParamEnum.OUTPUT_SIZE)
        self.assertIsInstance(aParam, CompNodeParam)
        aParam = instanceDef.getParameter('Invalid')
        self.assertIsNone(aParam)

        # Instance of bevel
        aInstance = aGraph.createCompInstanceNodeFromPath(sbsDoc, 'sbs://bevel.sbs')
        instanceDef = aInstance.getDefinition()
        # - input named 'input'
        self.assertIsInstance(instanceDef.getInput('input'), CompNodeInput)

        # Instance of blend_switch
        aInstance = aGraph.createCompInstanceNodeFromPath(sbsDoc, 'sbs://blend_switch.sbs/multi_switch')
        instanceDef = aInstance.getDefinition()
        # - output named 'output'
        self.assertIsInstance(instanceDef.getOutput('output'), CompNodeOutput)



if __name__ == '__main__':
    log.info("Test Libraries")
    unittest.main()
