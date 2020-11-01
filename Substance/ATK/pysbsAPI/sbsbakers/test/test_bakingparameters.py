# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import shutil
import copy
import sys

from pysbs.api_exceptions import SBSImpossibleActionError, SBSLibraryError
from pysbs import python_helpers
from pysbs.sbsbakers.sbsbakersenum import *
from pysbs.sbsbakers import sbsbakersdictionaries

from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import sbsgenerator
from pysbs.sbsenum import OutputSizeEnum

testModule = sys.modules[__name__]


class BakingParametersTests(unittest.TestCase):

    @staticmethod
    def openTestDocument(aRelPath):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, aRelPath)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def compareBakingParameters(self, resource1, resource2):
        def compareBaker(baker1, baker2):
            properties1 = baker1.getAllParameters()
            properties2 = baker2.getAllParameters()

            # TODO: Full recursive here? Should this be considered len or a named operation to avoid confusion?
            self.assertEqual(len(properties1), len(properties2))

            for prop1 in properties1:
                prop2 = next((p for p in properties2 if p.mIdentifier == prop1.mIdentifier), None)
                properties2.remove(prop2)
                self.assertIsNotNone(prop2)
                self.assertEqual(prop1.getValue(), prop2.getValue())
                self.assertEqual(baker1.getOverrideState(prop1.mIdentifier), baker2.getOverrideState(prop2.mIdentifier))

        # Get the corresponding Baking Parameters
        options1 = sorted(resource1.getOptions(), key=lambda a: a.mName)
        BP1 = resource1.getBakingParameters()
        options2 = sorted(resource2.getOptions(), key=lambda a: a.mName)
        BP2 = resource2.getBakingParameters()

        self.assertEqual(len(options1), len(options2))

        # Compare option values
        self.assertEqual(len(BP1.mBakers), len(BP2.mBakers))
        for baker1 in BP1.mBakers:
            baker2 = BP2.getBaker(baker1.mIdentifier)
            compareBaker(baker1, baker2)

        for baker1 in BP1.mBakers:
            baker2 = BP2.getBaker(baker1.mIdentifier)
            compareBaker(baker2, baker1)

    def test_ReadWriteBakingParameters(self):
        log.info("Test BakingParametersTests: Read Write Parameters")
        sbsDoc = BakingParametersTests.openTestDocument('./resources/AllBakingParameters.sbs')

        # Get resource 'sphere'
        aSceneRes = sbsDoc.getSBSResource('sphere')
        initialRes = copy.deepcopy(aSceneRes)

        # Get the corresponding Baking Parameters
        initialBP = aSceneRes.getBakingParameters()

        # Reset the Baking Parameters without any modification
        aSceneRes.setBakingParameters(initialBP)

        destPath = sbsDoc.buildAbsPathFromRelToMePath('testBakingReadWrite.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        sbsDoc = substance.SBSDocument(context.Context(), destPath)
        sbsDoc.parseDoc()
        aSceneRes = sbsDoc.getSBSResource('sphere')

        # Compare the resulting options
        self.compareBakingParameters(initialRes, aSceneRes)

        os.remove(destPath)

    def test_AllBakingParameters(self):
        log.info("Test AllBakingParametersTests: All default parameters")

        # Get the reference values from the reference file AllBakingParameters.sbs
        resDoc = BakingParametersTests.openTestDocument('./resources/AllBakingParameters.sbs')

        refResource = resDoc.getSBSResource('sphere')
        initialBP = refResource.getBakingParameters()

        # Create a new package with all the baking parameters
        destPath = python_helpers.getAbsPathFromModule(testModule, './resources/testAllBakingParameters.sbs')

        # Create a new package
        aContext = context.Context()
        sbsDoc = sbsgenerator.createSBSDocument(aContext, destPath, aGraphIdentifier='AllBakingParameters')

        # Link a Scene resource
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath(aRelPathFromPackage='./sphere.obj')
        resResource = sbsDoc.createSceneResource(aIdentifier=u'MySceneResource',
                                                 aResourcePath=aRelPath)

        # Copy scenes options
        options = refResource.getSceneOptions()
        options.extend(refResource.getSceneInfoOptions())
        resResource.setOptions(options)

        # Create Baking Parameters and set global parameters as in AllBakingParameters.sbs
        aBakingParams = resResource.createBakingParameters()
        aBakingParams.addHighDefinitionMeshFromFile(aAbsFilePath=sbsDoc.buildAbsPathFromRelToMePath('sphere.obj'))
        aBakingParams.setFileParameterValueFromPath(aParameter=ConverterParamEnum.MESH__SKEW_PATH, aAbsPath=sbsDoc.buildAbsPathFromRelToMePath('Craters.png'))
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.MESH__MAX_REAR_DISTANCE, aParamValue=0.032)
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.MESH__USE_SKEW, aParamValue=True)
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.MESH__USE_LOW_AS_HIGH_POLY, aParamValue=True)
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.DEFAULT__OUTPUT_WIDTH, aParamValue=OutputSizeEnum.SIZE_1024)
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT, aParamValue=OutputSizeEnum.SIZE_1024)
        aBakingParams.setParameterValue(aParameter=ConverterParamEnum.OUTPUT__FOLDER, aParamValue=initialBP.getParameterValue(ConverterParamEnum.OUTPUT__FOLDER))

        # Create all bakers with their default values
        aBakingParams.addBaker(BakerEnum.AMBIENT_OCCLUSION)
        aBakingParams.addBaker(BakerEnum.AMBIENT_OCCLUSION)
        aBakingParams.addBaker(BakerEnum.AMBIENT_OCCLUSION_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.BENT_NORMALS_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.COLOR_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.CONVERT_UV_TO_SVG)
        aBakingParams.addBaker(BakerEnum.CURVATURE)
        aBakingParams.addBaker(BakerEnum.CURVATURE_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.HEIGHT_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.NORMAL_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.OPACITY_MASK_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.POSITION)
        aBakingParams.addBaker(BakerEnum.POSITION_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.THICKNESS_MAP_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.TRANSFERRED_TEXTURE_FROM_MESH)
        aBakingParams.addBaker(BakerEnum.WORLD_SPACE_DIRECTION)
        aBakingParams.addBaker(BakerEnum.WORLD_SPACE_NORMALS)

        # Save the result
        resResource.setBakingParameters(aBakingParams)
        sbsDoc.writeDoc()
        sbsDoc = substance.SBSDocument(context.Context(), destPath)
        sbsDoc.parseDoc()
        resResource = sbsDoc.getSBSResource('MySceneResource')

        # Compare the resulting options
        self.compareBakingParameters(refResource, resResource)

        os.remove(destPath)

    def test_AddRemoveBakers(self):
        log.info("Test BakingParametersTests: Add/Remove converters")
        sbsDoc = BakingParametersTests.openTestDocument('./resources/SimpleBakingParameters.sbs')
        # Get baking params of resource 'MySphere'
        aSceneRes = sbsDoc.getSBSResource('sphere')
        aBakingParams = aSceneRes.getBakingParameters()

        # Get the position converter and deselect it
        Position_baker = aBakingParams.getBaker(aBaker=BakerEnum.POSITION)
        aBakingParams.selectBaker(aBaker=Position_baker, aSelected=False)

        # Add another position baker
        Position_baker2 = aBakingParams.addBaker(aIdentifier=BakerEnum.POSITION)
        self.assertEqual(Position_baker2.mIdentifier, 'Position [2]')

        # Remove the initial Position baker
        aBakingParams.removeBaker(Position_baker)

        # Add two other position baker
        Position_baker3 = aBakingParams.addBaker(aIdentifier=BakerEnum.POSITION)
        self.assertEqual(Position_baker3.mIdentifier, 'Position')
        Position_baker4 = aBakingParams.addBaker(aIdentifier=BakerEnum.POSITION)
        self.assertEqual(Position_baker4.mIdentifier, 'Position [3]')

        # Serialize Baking Parameters
        aSceneRes.setBakingParameters(aBakingParams)

        destPath = sbsDoc.buildAbsPathFromRelToMePath('testBakingAddRemoveBakers.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        os.remove(destPath)

    def test_AddFromMeshBakers(self):
        log.info("Test BakingParametersTests: Add and Configure From Mesh converter")
        sbsDoc = BakingParametersTests.openTestDocument('./resources/SimpleBakingParameters.sbs')
        # Get baking params of resource 'MySphere'
        aSceneRes = sbsDoc.getSBSResource('sphere')
        aBakingParams = aSceneRes.getBakingParameters()

        # Get the existing bakers
        Curv_baker = aBakingParams.getBaker(aBaker=BakerEnum.CURVATURE)
        Pos_baker  = aBakingParams.getBaker(aBaker=BakerEnum.POSITION)
        self.assertIsNotNone(Curv_baker)
        self.assertIsNotNone(Pos_baker)

        # Add a Normal Map From Mesh baker
        NM_baker = aBakingParams.addBaker(aIdentifier=BakerEnum.NORMAL_MAP_FROM_MESH)

        # Set the existing resource as a HighDefinitionMesh
        self.assertTrue(aBakingParams.addHighDefinitionMeshFromResource(aSceneRes))
        self.assertFalse(aBakingParams.addHighDefinitionMeshFromResource(aSceneRes))

        # Check normal behavior when setting a resource parameter:
        aBakingParams.setFileParameterValueFromResource(ConverterParamEnum.MESH__CAGE_PATH, aSceneRes)

        # Check invalid cases:
        with self.assertRaises(SBSImpossibleActionError):
            NM_baker.setFileParameterValueFromResource(ConverterParamEnum.DETAIL_SECONDARY_COMMON__DISTRIBUTION, aSceneRes)
        with self.assertRaises(SBSImpossibleActionError):
            NM_baker.setFileParameterValueFromResource(ConverterParamEnum.ADDITIONAL__NORMAL_MAP, aSceneRes)

        # Add a World Space Direction baker
        WSD_baker = aBakingParams.addBaker(aIdentifier=BakerEnum.WORLD_SPACE_DIRECTION)
        WSD_baker.setFileParameterValueFromPreviousBaker(ConverterParamEnum.WORLD_DIRECTION__DIRECTION_MAP, Pos_baker)

        # Modify converters order
        with self.assertRaises(SBSImpossibleActionError):
            Curv_baker.moveUp()
        Pos_baker.moveDown()
        Pos_baker.moveDown()
        with self.assertRaises(SBSImpossibleActionError):
            Pos_baker.moveDown()

        with self.assertRaises(SBSImpossibleActionError):
            WSD_baker.setFileParameterValueFromPreviousBaker(ConverterParamEnum.WORLD_DIRECTION__DIRECTION_MAP, Pos_baker)

        # Serialize Baking Parameters
        aSceneRes.setBakingParameters(aBakingParams)

        destPath = sbsDoc.buildAbsPathFromRelToMePath('testBakingAddFromMeshBaker.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        os.remove(destPath)


    def test_ModifyBakingParameters(self):
        log.info("Test BakingParametersTests: Read Write Parameters")
        sbsDoc = BakingParametersTests.openTestDocument('./resources/SimpleBakingParameters.sbs')
        self.assertTrue(sbsDoc.parseDoc())

        # Get resource 'sphere' and its baking parameters
        aSceneRes = sbsDoc.getSBSResource('sphere')
        aBakingParams= aSceneRes.getBakingParameters()

        # Set scene parameters
        aColor = aBakingParams.getSubMeshColor(1, 0)
        aColor.setColorHexa(aColor='#ffffff')
        aBakingParams.setSubMeshColorHexa(1, 0, aColor='#000000')
        self.assertEqual(aColor.getColorHexa(), '#000000')

        aBakingParams.setSubMeshSelection(1, 0, False)

        # Get the Curvature converter
        aCurvBaker = aBakingParams.getBaker(aBaker=BakerEnum.CURVATURE)

        # Check bad parameter:
        with self.assertRaises(SBSLibraryError):
            aCurvBaker.setParameterValue(aParameter='BadParam', aParamValue=0)
        with self.assertRaises(SBSLibraryError):
            aCurvBaker.setParameterValue(aParameter=1000, aParamValue=0)

        # Check boolean parameter value
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), True)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue=False)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), False)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue='True')
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), True)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue=0)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), False)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue='1')
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), True)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue=None)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__ENABLE_SEAMS), False)

        with self.assertRaises(ValueError):
            aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__ENABLE_SEAMS, aParamValue='invalid')


        # Check enum (e.g integer) parameter
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT), OutputSizeEnum.SIZE_2048)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_2048)

        aCurvBaker.setParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT, OutputSizeEnum.SIZE_1024)
        aCurvBaker.setParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH, OutputSizeEnum.SIZE_128)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT), OutputSizeEnum.SIZE_1024)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_128)

        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__PER_VERTEX), BakerCurvatureAlgoEnum.PER_PIXEL)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__PER_VERTEX, aParamValue=BakerCurvatureAlgoEnum.PER_VERTEX)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__PER_VERTEX), BakerCurvatureAlgoEnum.PER_VERTEX)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__PER_VERTEX, aParamValue='0')
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__PER_VERTEX), BakerCurvatureAlgoEnum.PER_PIXEL)

        aCurvBaker.setParameterValue(aParameter='Curvature.PerVertex', aParamValue=1.0)
        self.assertEqual(aCurvBaker.getParameterValue('Curvature.PerVertex'), BakerCurvatureAlgoEnum.PER_VERTEX)

        aCurvBaker.setParameterValue(aParameter='Curvature.PerVertex', aParamValue='1.0')
        self.assertEqual(aCurvBaker.getParameterValue('Curvature.PerVertex'), BakerCurvatureAlgoEnum.PER_VERTEX)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__PER_VERTEX, aParamValue=None)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__PER_VERTEX), BakerCurvatureAlgoEnum.PER_PIXEL)

        with self.assertRaises(ValueError):
            aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__PER_VERTEX, aParamValue='invalid')


        # Check float parameter
        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER, aParamValue=0.81)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER), 0.81)

        aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER, aParamValue='0.10')
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER), 0.1)

        aCurvBaker.setParameterValue(aParameter='Curvature.CurvMult', aParamValue=1)
        self.assertEqual(aCurvBaker.getParameterValue('Curvature.CurvMult'), 1.0)

        aCurvBaker.setParameterValue(aParameter='Curvature.CurvMult', aParamValue=None)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER), 0.0)

        with self.assertRaises(ValueError):
            aCurvBaker.setParameterValue(aParameter=ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER, aParamValue='invalid')


        # Modify global size and check new baker parameters
        self.assertEqual(aBakingParams.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT), OutputSizeEnum.SIZE_2048)
        self.assertEqual(aBakingParams.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_2048)

        aBakingParams.setParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH, OutputSizeEnum.SIZE_512)
        self.assertEqual(aBakingParams.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_512)

        aBakingParams.setParameterValue(ConverterParamEnum.DEFAULT__FORMAT, BakerOutputFormatEnum.JPEG)
        self.assertEqual(aBakingParams.getParameterValue(ConverterParamEnum.DEFAULT__FORMAT),
                         sbsbakersdictionaries.getBakerOutputFormatName(BakerOutputFormatEnum.JPEG))

        # Check that the previous baker are updated with the new default parameters depending on their overrides
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_128)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__FORMAT),
                         sbsbakersdictionaries.getBakerOutputFormatName(BakerOutputFormatEnum.JPEG))

        # Add a new baker and check that the updated global parameters are present
        aHeightBaker = aBakingParams.addBaker(BakerEnum.HEIGHT_MAP_FROM_MESH)
        self.assertEqual(aHeightBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT), OutputSizeEnum.SIZE_2048)
        self.assertEqual(aHeightBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_512)
        self.assertEqual(aHeightBaker.getParameterValue(ConverterParamEnum.DEFAULT__FORMAT),
                         sbsbakersdictionaries.getBakerOutputFormatName(BakerOutputFormatEnum.JPEG))

        # Reset an overriden property to the default global value
        aCurvBaker.resetDefaultProperty(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH)
        self.assertEqual(aCurvBaker.getParameterValue(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH), OutputSizeEnum.SIZE_512)


        # Serialize Baking Parameters
        aSceneRes.setBakingParameters(aBakingParams)
        destPath = sbsDoc.buildAbsPathFromRelToMePath('testBakingModifyBaker.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        os.remove(destPath)


    def test_FromScratch(self):
        log.info("Test BakingParametersTests: Read From Scratch")
        aDestPath = python_helpers.getAbsPathFromModule(testModule, './resources/testFromScratch.sbs')

        # Create a new package
        aContext = context.Context()
        sbsDoc = sbsgenerator.createSBSDocument(aContext, aDestPath)
        aResourceDir = sbsDoc.buildAbsPathFromRelToMePath('testFromScratch.resources')
        aResourcePath = sbsDoc.buildAbsPathFromRelToMePath('Craters.png')

        # Link a bitmap resource
        aResourceLinked = sbsDoc.createLinkedResource(aIdentifier='linkedRes', aResourcePath=aResourcePath, aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
        self.assertIsInstance(aResourceLinked, substance.resource.SBSResource)

        # Import a bitmap resource
        aResourceImported = sbsDoc.createImportedResource(aIdentifier='importedRes', aResourcePath=aResourcePath, aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
        self.assertIsInstance(aResourceImported, substance.resource.SBSResource)
        self.assertTrue(os.path.exists(aResourceDir))

        # Link a Scene resource
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath(aRelPathFromPackage='./sphere.obj')
        aSceneResource = sbsDoc.createLinkedResource(aIdentifier=u'MySceneResource',
                                                   aResourcePath=aRelPath,
                                                   aResourceTypeEnum=sbsenum.ResourceTypeEnum.SCENE)

        # Check that if the same resource is created, no new resource is created
        aSceneResource2 = sbsDoc.createLinkedResource(aIdentifier='MySceneResource',
                                                   aResourcePath=aRelPath,
                                                   aResourceTypeEnum=sbsenum.ResourceTypeEnum.SCENE)
        self.assertEqual(aSceneResource, aSceneResource2)

        # Create Baking Parameters
        aBakingParams = aSceneResource.createBakingParameters()
        aCurvBaker = aBakingParams.addBaker(BakerEnum.CURVATURE)
        aCurvBaker.setFileParameterValueFromResource(ConverterParamEnum.ADDITIONAL__NORMAL_MAP, aResourceImported)
        aCurvBaker.setFileParameterValueFromResource(ConverterParamEnum.ADDITIONAL__NORMAL_MAP, aResourceLinked)
        aSceneResource.setBakingParameters(aBakingParams)

        # Check wrong behaviors
        with self.assertRaises(SBSImpossibleActionError):   aResourceImported.createBakingParameters()
        with self.assertRaises(SBSImpossibleActionError):   aResourceLinked.createBakingParameters()
        with self.assertRaises(SBSImpossibleActionError):
            sbsDoc.createImportedResource(aResourcePath=aRelPath, aResourceTypeEnum=sbsenum.ResourceTypeEnum.SCENE)

        self.assertEqual(len(sbsDoc.getSBSResourceList()), 3)

        # Serialize Baking Parameters
        sbsDoc.writeDoc()

        # Clean data generated by the test
        os.remove(aResourceImported.mFileAbsPath)
        os.remove(aDestPath)
        shutil.rmtree(aResourceDir)


if __name__ == '__main__':
    log.info("Test Baking Parameters")
    unittest.main()