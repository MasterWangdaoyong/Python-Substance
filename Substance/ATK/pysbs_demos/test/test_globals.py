import unittest
import logging
log = logging.getLogger(__name__)
import copy
import os
import shutil
import filecmp
import sys
import xml.etree.ElementTree as ET

from pysbs_demos import demos, demohelloworld

from pysbs import python_helpers
from pysbs import compnode
from pysbs import context
from pysbs import sbscommon
from pysbs import sbsenum
from pysbs import substance
from pysbs import sbsbakers


testModule = sys.modules[__name__]

class GlobalTests(unittest.TestCase):
    """
    These global tests allow checking the result of the demo scripts, considering a reference result available in resources/
    """
    def test_ReadWrite(self):
        log.info('GlobalTests: test_ReadWrite')
        aContext = context.Context()
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoIteration.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoReadWrite.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoReadWriteSBS(aContext, fileAbsPath, destAbsPath))

        docSource = substance.SBSDocument(aContext, fileAbsPath)
        docSource.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docSource.equals(docDest))

        self.assertEqual(len(docDest.getSBSDependencyList()), 3)
        self.assertEqual(len(docDest.getSBSResourceList()), 1)

        os.remove(destAbsPath)

    def test_DemoBakingParameters(self):
        log.info('GlobalTests: test_DemoBakingParameters')
        aContext = context.Context()
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/DemoBakingParameters.sbs')
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoBakingParameters.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoBakingParameters.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoBakingParameters(aContext, fileAbsPath, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()

        aResource = docDest.getSBSResource('LowResMesh')
        aBakingParams = aResource.getBakingParameters()
        self.assertEqual(aBakingParams.getNbBakers(), 3)

        BN_baker = aBakingParams.getBaker(sbsbakers.BakerEnum.BENT_NORMALS_FROM_MESH)
        self.assertEqual(BN_baker.getParameter(sbsbakers.ConverterParamEnum.DETAIL__SUB_SAMPLING).getValue(),
                         sbsbakers.BakerFromMeshSubSamplingEnum.SUBSAMPLING_4x4)

        NM_baker = aBakingParams.getBaker(sbsbakers.BakerEnum.NORMAL_MAP_FROM_MESH)
        self.assertEqual(NM_baker.getParameter(sbsbakers.ConverterParamEnum.DETAIL__SUB_SAMPLING).getValue(),
                         sbsbakers.BakerFromMeshSubSamplingEnum.SUBSAMPLING_2x2)

        aHighPolyFilePath = os.path.normpath(os.path.join(os.path.dirname(fileAbsPath), 'Models/m41_high.fbx'))
        aHighPolyFilePath = 'file:///' + aHighPolyFilePath.replace('\\','/')

        aHighMeshParam = aBakingParams.getParameter(sbsbakers.ConverterParamEnum.MESH__HIGH_DEF_MESHES).getValue()[0]
        self.assertEqual(aHighMeshParam, aHighPolyFilePath)

        AO_baker = aBakingParams.getBaker(sbsbakers.BakerEnum.AMBIENT_OCCLUSION)
        aNormalMapFileParam = AO_baker.getParameter(sbsbakers.ConverterParamEnum.ADDITIONAL__NORMAL_MAP).getValue()
        self.assertEqual(aNormalMapFileParam, 'baker://' + NM_baker.mIdentifier)

        os.remove(destAbsPath)

    def test_DemoHelloWorld(self):
        log.info('GlobalTests: test_DemoHelloWorld')
        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoHelloWorld.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoHelloWorld.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demohelloworld.demoHelloWorld(destAbsPath))

        aContext = context.Context()
        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    def test_DemoCreation(self):
        log.info('GlobalTests: test_DemoCreation')
        aContext = context.Context()
        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoCreation.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoCreation.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoCreation(aContext, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    def test_DemoIteration(self):
        log.info('GlobalTests: test_DemoIteration')
        aContext = context.Context()
        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoIteration.sbs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/DemoIteration.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoIteration.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoIteration(aContext, fileAbsPath, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        # Check connections:
        graph = docDest.getSBSGraph('DemoIterationVerticalPattern')
        initialNodes = graph.mCompNodes[0:6]

        # Sort the node list as a DAG
        connectionsInsidePattern = graph.mNodeList.computeConnectionsInsidePattern(initialNodes)
        sortedIndices = graph.mNodeList.computeSortedIndicesOfDAG(initialNodes, connectionsInsidePattern)
        sortedNodeList = []
        for index in sortedIndices:
            sortedNodeList.append(initialNodes[index])

        firstInstance = next((aNode for aNode in initialNodes if aNode.isAnInstance()), None)
        secondInstance = next((aNode for aNode in initialNodes if aNode.isAnInstance() and aNode != firstInstance), None)
        self.assertEqual(firstInstance, sortedNodeList[2])
        self.assertEqual(secondInstance, sortedNodeList[4])

        firstPixProc = sortedNodeList[3]
        self.assertTrue(firstPixProc.isAPixelProcessor())
        secondPixProc = sortedNodeList[5]
        self.assertTrue(secondPixProc.isAPixelProcessor())

        createdNodes = graph.mCompNodes[6:]
        self.assertTrue(createdNodes[0].mConnections[0].getConnectedNodeUID() == secondInstance.mUID)
        self.assertTrue(createdNodes[1].mConnections[0].getConnectedNodeUID() == createdNodes[0].mUID)
        self.assertTrue(createdNodes[1].mConnections[1].getConnectedNodeUID() == secondPixProc.mUID)

        os.remove(destAbsPath)

    def test_DemoIterationPixProc(self):
        log.info('GlobalTests: test_DemoIterationPixProc')
        aContext = context.Context()
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoIterationPixProc.sbs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/TerrainMultiFractal.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoIterationPixProc.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoIterationPixProc(aContext, fileAbsPath, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    def test_DemoIterationFlame(self):
        log.info('GlobalTests: test_DemoIterationFlame')
        aContext = context.Context()
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoIterationFlame.sbs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/Flame.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoIterationFlame.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoIterationFlame(aContext, fileAbsPath, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        self.assertTrue(docRef.parseDoc())
        docDest = substance.SBSDocument(aContext, destAbsPath)
        self.assertTrue(docDest.parseDoc())
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    def test_DemoMassiveModification(self):
        log.info('GlobalTests: test_DemoMassiveModification')
        aContext = context.Context()
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoMassiveModification.sbs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/blend_switch.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoMassiveModification.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoMassiveModification(aContext, fileAbsPath, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        self.assertTrue(docRef.parseDoc())
        docDest = substance.SBSDocument(aContext, destAbsPath)
        self.assertTrue(docDest.parseDoc())
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    def test_DemoExportWithDependencies(self):
        def compareXML(aXMLPath1, aXMLPath2):
            treeRef = ET.parse(aXMLPath1)
            strRef  = ET.tostring(treeRef.getroot())
            treeDest = ET.parse(aXMLPath2)
            strDest  = ET.tostring(treeDest.getroot())
            # hack  to skip uid comparison
            strDest = str(strDest).replace("1377775032", "1377775031")
            return str(strRef) == strDest

        log.info('GlobalTests: test_DemoExportWithDependencies')
        aContext = context.Context()
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refExportWithDependencies')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/TerrainMultiFractal.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/ExportSBS')
        if os.path.exists(destAbsPath):
            shutil.rmtree(destAbsPath)
        self.assertTrue(demos.demoExportWithDependencies(aContext, fileAbsPath, destAbsPath))

        # Compare root exported .sbs between reference and created one
        docRef = substance.SBSDocument(aContext, os.path.join(refAbsPath, 'TerrainMultiFractal/TerrainMultiFractal.sbs'))
        self.assertTrue(docRef.parseDoc())
        docDest = substance.SBSDocument(aContext, os.path.join(destAbsPath, 'TerrainMultiFractal/TerrainMultiFractal.sbs'))
        self.assertTrue(docDest.parseDoc())
        self.assertTrue(docRef.equals(docDest))

        # Compare them as xml (should be the exact same content):
        self.assertTrue(compareXML(docRef.mFileAbsPath, docDest.mFileAbsPath))

        # Compare exported directory and zip content
        for aFile in os.listdir(destAbsPath):
            if aFile.endswith('.zip'):
                os.rename(os.path.join(destAbsPath, aFile), os.path.join(destAbsPath, aFile[:-24]+'.zip'))
                break

        aComp = filecmp.dircmp(refAbsPath, destAbsPath)
        self.assertEqual(len(aComp.common), 2)
        self.assertEqual(len(aComp.left_list), 2)
        self.assertEqual(len(aComp.right_list), 2)
        self.assertEqual(len(aComp.left_only), 0)
        self.assertEqual(len(aComp.right_only), 0)

        refAbsPath2 = os.path.join(refAbsPath,'TerrainMultiFractal')
        destAbsPath2 = os.path.join(destAbsPath,'TerrainMultiFractal')

        aComp = filecmp.dircmp(refAbsPath2, destAbsPath2)
        self.assertEqual(len(aComp.common), 2)
        self.assertEqual(len(aComp.left_list), 2)
        self.assertEqual(len(aComp.right_list), 2)
        self.assertEqual(len(aComp.left_only), 0)
        self.assertEqual(len(aComp.right_only), 0)
        self.assertEqual(len(aComp.subdirs), 1)
        aSubDirCmp = list(aComp.subdirs.items())[0][1]
        self.assertEqual(len(aSubDirCmp.common), 4)
        self.assertEqual(len(aSubDirCmp.left_list), 4)
        self.assertEqual(len(aSubDirCmp.right_list), 4)
        self.assertEqual(len(aSubDirCmp.left_only), 0)
        self.assertEqual(len(aSubDirCmp.right_only), 0)
        self.assertEqual(len(aSubDirCmp.subdirs), 0)

        shutil.rmtree(destAbsPath)

    def test_Connections(self):
        log.info('GlobalTests: test_Connections')
        aContext = context.Context()
        refAbsPath  = python_helpers.getAbsPathFromModule(testModule, './resources/refFluvialErosion.sbs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, '../sample/FluvialErosion.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testFluvialErosion.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)

        docDest = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(docDest.parseDoc())

        # Create iteration
        aGraph = docDest.getSBSGraph(aGraphIdentifier='FluvialErosion100Step')
        self.assertIsNotNone(aGraph)
        nbIterations = 98
        createdNodes = aGraph.createIterationOnPattern(aNbIteration=nbIterations,
                                                       aNodeUIDs=['1255614799'],
                                                       aNodeUIDs_NextPattern=['1260900799'],
                                                       aForceRandomSeed=True,
                                                       aIncrementIteration=True)
        self.assertIsNotNone(createdNodes)
        self.assertEqual(len(createdNodes), nbIterations)

        docRef = substance.SBSDocument(aContext, refAbsPath)
        self.assertTrue(docRef.parseDoc())
        self.assertTrue(docRef.equals(docDest))

        aEndNode = aGraph.getNode('1260899131')
        self.assertIsInstance(aEndNode, compnode.SBSCompNode)

        aConn1 = copy.deepcopy(aGraph.connectNodes(aLeftNode=createdNodes[-1], aLeftNodeOutput=None,
                                                   aRightNode=aEndNode, aRightNodeInput=None))
        self.assertIsInstance(aConn1, sbscommon.SBSConnection)

        aConn2 = copy.deepcopy(aGraph.connectNodes(aLeftNode=createdNodes[-1], aLeftNodeOutput='out_Height',
                                                   aRightNode=aEndNode, aRightNodeInput=None))
        self.assertIsInstance(aConn2, sbscommon.SBSConnection)

        aConn3 = copy.deepcopy(aGraph.connectNodes(aLeftNode=createdNodes[-1], aLeftNodeOutput=None,
                                                   aRightNode=aEndNode, aRightNodeInput='in_Height'))
        self.assertIsInstance(aConn3, sbscommon.SBSConnection)
        aConn4 = copy.deepcopy(aGraph.connectNodes(aLeftNode=createdNodes[-1], aLeftNodeOutput='out_Water',
                                                   aRightNode=aEndNode, aRightNodeInput='in_Water'))
        self.assertIsInstance(aConn4, sbscommon.SBSConnection)

        self.assertTrue(aConn1.equals(aConn2))
        self.assertTrue(aConn1.equals(aConn3))
        self.assertFalse(aConn1.equals(aConn4))

        lastIteration = int(createdNodes[-1].getParameterValue(sbsenum.CompNodeParamEnum.ITERATION))
        self.assertEqual(lastIteration, nbIterations)

        self.assertTrue(docDest.writeDoc(aNewFileAbsPath = destAbsPath, aUpdateRelativePaths=True))

        os.remove(destAbsPath)


if __name__ == '__main__':
    unittest.main(verbosity=2)
