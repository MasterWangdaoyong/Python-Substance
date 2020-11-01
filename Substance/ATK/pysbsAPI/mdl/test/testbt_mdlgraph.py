# coding: utf-8
import logging
log = logging.getLogger(__name__)
import unittest
import copy
import os
import shutil

from pysbs.api_exceptions import SBSImpossibleActionError, SBSLibraryError
from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import sbscommon
from pysbs import sbsgenerator

from pysbs.mdl import MDLGraph, MDLNode, MDLOperands, MDLOperandValue, MDLOperandArray, \
                    MDLNodeDefParam, MDLNodeDefInput, MDLNodeDefOutput, MDLImplSBSInstance
from pysbs.mdl import mdlenum


def _convertToAbsPath(aRelPath):
    return os.path.abspath(os.path.join(os.path.split(__file__)[0], aRelPath))

class MDLGraphTests(unittest.TestCase):
    @staticmethod
    def isPrivateMember(aMemberName):
        return aMemberName.startswith('__') and aMemberName.endswith('__')

    @staticmethod
    def openTestDocument(aFileName):
        docAbsPath = _convertToAbsPath('./resources/' + aFileName)

        aContext = context.Context()
        sbsDoc = substance.SBSDocument(aContext, docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_readWrite(self):
        """
        This test checks the ability to read & write a substance with a mdl graph
        """
        log.info("Test MDLGraph: Read & Write mdl graph")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        self.assertIsNotNone(sbsDoc)

        destFile = 'test_ReadWrite.sbs'
        destPath = sbsDoc.buildAbsPathFromRelToMePath(destFile)
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)

        resDoc = MDLGraphTests.openTestDocument(destFile)
        self.assertIsInstance(resDoc, substance.SBSDocument)

        self.assertTrue(sbsDoc.equals(resDoc))
        os.remove(destPath)


    def test_GraphAttributes(self):
        """
        This test checks the creation of a MDL Graph and settings of its attributes
        """
        log.info("Test MDLGraph: Create new mdl graph and set its attributes")
        destPath = _convertToAbsPath('testGraphAttributes.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath)
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='myMDL', aParentFolder='myFolder')
        mdlGraph.setAttribute(sbsenum.AttributesEnum.Category, u'myCatëgo€')
        self.assertEqual(mdlGraph.getAttribute(sbsenum.AttributesEnum.Category), u'myCatëgo€')
        with self.assertRaises(SBSImpossibleActionError):
                mdlGraph.setAttribute(sbsenum.AttributesEnum.Label, 'label')
        self.assertIsNone(mdlGraph.getAttribute(sbsenum.AttributesEnum.Author))

        mdlGraph.setAnnotation(mdlenum.MDLAnnotationEnum.AUTHOR, 'allegorithmic')
        self.assertEqual(mdlGraph.getAnnotationValue(mdlenum.MDLAnnotationEnum.AUTHOR), 'allegorithmic')

        mdlGraph.setAnnotation(mdlenum.MDLAnnotationEnum.IN_GROUP, 'myGrp')
        self.assertEqual(mdlGraph.getGroup(), 'myGrp')

        mdlGraph.setGroup('Grp', 'SGrp')
        self.assertEqual(mdlGraph.getGroup(), 'Grp/SGrp')

        self.assertIsNone(mdlGraph.getAnnotationValue(mdlenum.MDLAnnotationEnum.HIDDEN))
        mdlGraph.setAnnotation(mdlenum.MDLAnnotationEnum.HIDDEN, True)
        self.assertEqual(mdlGraph.getAnnotationValue(mdlenum.MDLAnnotationEnum.HIDDEN), True)

        with self.assertRaises(SBSLibraryError):    mdlGraph.getAnnotation(1000)
        with self.assertRaises(SBSLibraryError):    mdlGraph.setAnnotation(1000, 'invalid')
        with self.assertRaises(SBSImpossibleActionError): mdlGraph.setAnnotation(mdlenum.MDLAnnotationEnum.GAMMA_TYPE, 'invalid')


    def test_getGraphContent(self):
        """
        This test checks the ability to request the content of a mdl graph
        """
        log.info("Test MDLGraph: Requesting content of a mdl graph")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        self.assertIsNotNone(sbsDoc)

        mdlGraph = sbsDoc.getMDLGraph('MDL_Material')
        self.assertIsInstance(mdlGraph, MDLGraph)
        self.assertEqual(mdlGraph, sbsDoc.getMDLGraphList()[0])

        # Get all functions
        self.assertEqual(len(mdlGraph.getAllMDLConstants()), 11)
        self.assertEqual(len(mdlGraph.getAllMDLSelectors()), 4)
        self.assertEqual(len(mdlGraph.getAllMDLInstances()), 16)
        self.assertEqual(len(mdlGraph.getAllMDLGraphInstances()), 2)
        self.assertEqual(len(mdlGraph.getAllSBSInstances()), 2)

        self.assertEqual(len(mdlGraph.getAllMDLConstantsOfType('mdl::float')), 4)
        self.assertEqual(len(mdlGraph.getAllMDLConstantsWithName('roughness')), 1)
        self.assertEqual(len(mdlGraph.getAllMDLSelectorsWithName('tint')), 1)
        self.assertEqual(len(mdlGraph.getAllMDLSelectorsOfType('mdl::color')), 1)
        self.assertEqual(len(mdlGraph.getAllMDLInstancesOf('mdl::operator*')), 3)
        self.assertEqual(len(mdlGraph.getAllMDLInstancesOf('mdl::operator*(float,float)')), 2)
        self.assertEqual(len(mdlGraph.getAllMDLGraphInstancesOf(aSBSDocument=sbsDoc, aPath=sbsDoc.buildAbsPathFromRelToMePath('MDL_Dag.sbs/MDL_Material'))), 1)

        self.assertEqual(len(mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='pkg:///New_Graph')), 1)
        self.assertEqual(len(mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='sbs://bnw_spots_1.sbs')), 1)

        aDep = sbsDoc.getDependencyFromPath('sbs://bnw_spots_1.sbs')
        self.assertEqual(len(mdlGraph.getAllReferencesOnDependency(aDependency=aDep)), 1)

        # Graph Output
        node_material_constructors = mdlGraph.getAllMDLInstancesOf('mdl::material')
        self.assertTrue(len(node_material_constructors) > 0, 'Could not find any node matching "{}"'.format('mdl::material'))
        self.assertEqual(mdlGraph.getGraphOutput(), node_material_constructors[0])
        self.assertEqual(mdlGraph.getGraphOutputNode(), mdlGraph.getAllMDLInstancesOf('mdl::material$1.4(bool,material_surface,material_surface,color,material_volume,material_geometry)')[0])
        self.assertEqual(mdlGraph.getGraphOutputType(), 'mdl::material')

        # Graph Inputs
        self.assertEqual(len(mdlGraph.getAllInputs()), 8)
        self.assertEqual(len(mdlGraph.getInputParameters()), 6)
        self.assertEqual(len(mdlGraph.getInputImages()), 2)

        identifiers = ['normal','roughness','metallic','specular_level','base_color','texture_2d_1000','texture_2d_1001','material_1']
        self.assertEqual(mdlGraph.getAllInputIdentifiers(), identifiers)
        self.assertEqual(len(mdlGraph.getAllInputsInGroup(aGroup='Images')), 2)

        metallicNode =  mdlGraph.getNode(mdlGraph.mParamInputs[2].mNodeUID)
        self.assertEqual(mdlGraph.getInputIndex(metallicNode), 2)
        self.assertEqual(mdlGraph.getInputIndex('metallic'), 2)
        self.assertEqual(mdlGraph.getInputIndex('texture_2d_1001'), 6)
        self.assertEqual(mdlGraph.getInputIndex('invalid'), -1)

        self.assertIsInstance(metallicNode, MDLNode)
        self.assertTrue(mdlGraph.contains(metallicNode))
        self.assertEqual(mdlGraph.getInputFromUID(metallicNode.mUID), metallicNode)

        self.assertEqual(mdlGraph.getInputParameter('metallic'), metallicNode)
        self.assertEqual(mdlGraph.getInputParameterFromUID(metallicNode.mUID), metallicNode)

        textUID1 = mdlGraph.mParamInputs[5].mNodeUID
        textUID2 = mdlGraph.mParamInputs[6].mNodeUID
        self.assertEqual(mdlGraph.getInputImage('texture_2d_1001').mUID, textUID2)
        self.assertEqual(mdlGraph.getInputImageWithUsage(aUsage='Custom').mUID, textUID2)
        self.assertEqual(mdlGraph.getInputImageWithUsage(aUsage=sbsenum.UsageEnum.BASECOLOR).mUID, textUID1)

        # Graph Attributes
        self.assertEqual(mdlGraph.getAttribute(sbsenum.AttributesEnum.Category), 'Categ')
        self.assertEqual(mdlGraph.getAttribute(sbsenum.AttributesEnum.HideInLibrary), True)
        self.assertIsInstance(mdlGraph.getIcon(), sbscommon.SBSIcon)

        self.assertEqual(mdlGraph.getFirstInputOfType('mdl::float'), mdlGraph.getInputParameter('roughness'))


    def test_GuiObjects(self):
        """
        This test checks the creation/edition/removal of GUI Objects.
        It also checks getting the nodes included in a frame
        """
        log.info("Test MDLGraph: GUI Objects operation")

        testDir = os.path.abspath(os.path.split(__file__)[0])
        docAbsPath = os.path.join(testDir, 'resources','testGUIObjects.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath)
        aGraph = sbsDoc.createMDLGraph('MDL_Material')

        # Check creation of GUIObjects
        grComment1 = aGraph.createComment(aGUIPos = [-1066, -395, 0])
        grComment2 = aGraph.createComment(aCommentText = u'Test <div>\n&é""\'(-è\içà)=$^*ù!:', aGUIPos = [-245, 373, -100])
        grFrame1 = aGraph.createFrame(aGUIPos=[-1066, -395, 0], aSize=[310, 374])
        grFrame2 = aGraph.createFrame(aFrameTitle=u'é<div>\\t$£€&1', aCommentText=u'\n<is>à', aGUIPos=[-1174, 533, -100], aSize=[630, 246], aColor=[0.13, 0.66, 0, 0.1])
        grPin    = aGraph.createNavigationPin(aPinText=u'<éà>&i', aGUIPos=[-677, -522, 0])
        self.assertTrue(grComment1.isAComment())
        self.assertTrue(grComment2.isAComment())
        self.assertTrue(grFrame1.isAFrame())
        self.assertTrue(grFrame2.isAFrame())
        self.assertTrue(grPin.isANavigationPin())

        self.assertTrue(sbsDoc.writeDoc())

        # Check getting GUIObjects
        refDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        allNodeGraph = refDoc.getMDLGraph('MDL_Material')
        aGUIObjects = allNodeGraph.getAllGUIObjects()
        refComments = allNodeGraph.getAllComments()
        refFrames = allNodeGraph.getAllFrames()
        refPins = allNodeGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 6)
        self.assertEqual(len(refComments), 2)
        self.assertEqual(len(refFrames), 3)
        self.assertEqual(len(refPins), 1)

        # Compare created GUIObject with their reference in AllNodes graph
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath)
        self.assertTrue(resDoc.parseDoc())
        resGraph = resDoc.getMDLGraph('MDL_Material')
        aGUIObjects = resGraph.getAllGUIObjects()
        resComments = resGraph.getAllComments()
        resFrames = resGraph.getAllFrames()
        resPins = resGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 5)
        self.assertEqual(len(resComments), 2)
        self.assertEqual(len(resFrames), 2)
        self.assertEqual(len(resPins), 1)

        self.assertTrue(resFrames[0].equals(refFrames[0]))
        # self.assertTrue(resFrames[1].equals(refFrames[1]))
        self.assertTrue(resComments[0].equals(refComments[0]))
        # self.assertTrue(resComments[1].equals(refComments[1]))
        self.assertTrue(resPins[0].equals(refPins[0]))

        # Check getting nodes in the ROI of a frame
        refFrame = next((aFrame for aFrame in refFrames if aFrame.mTitle == 'Frame'), None)
        self.assertIsNotNone(refFrame)
        inFrameNodes = allNodeGraph.getNodesInFrame(refFrame)
        self.assertEqual(len(inFrameNodes), 5)
        aNode = allNodeGraph.getAllMDLConstantsWithName('roughness')[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllMDLConstantsWithName('specular_level')[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllMDLConstantsWithName('float_1')[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllSBSInstancesOf(aSBSDocument=refDoc, aPath='pkg:///New_Graph')[0]
        self.assertTrue(aNode in inFrameNodes)

        aOutput = allNodeGraph.getGraphOutputNode()
        aOutputFrame = allNodeGraph.createFrameAroundNodes(aNodeList = [aOutput], aFrameTitle='The output', aColor=[0, 0.75, 0.75, 0.19])
        refOutputFrame = next((aFrame for aFrame in refFrames if aFrame.mTitle == 'The output'), None)
        self.assertTrue(aOutputFrame.equals(refOutputFrame))
        self.assertTrue(aOutputFrame.mGUILayout.equals(refOutputFrame.mGUILayout))

        aOutputFrame2 = allNodeGraph.createFrameAroundNodes(aNodeList = [aOutput.mUID], aFrameTitle='The output', aColor=[0, 0.75, 0.75, 0.19])
        self.assertEqual(aOutputFrame.getRect(), aOutputFrame2.getRect())

        self.assertIsInstance(allNodeGraph.getRect(), sbscommon.Rect)

        # Check deleting GUIObjects
        aGraph.deleteComment(grComment1)
        aGraph.deleteComment(grComment2.mUID)
        aGraph.deleteFrame(grFrame1)
        aGraph.deleteFrame(grFrame2.mUID)
        aGraph.deleteNavigationPin(grPin)
        self.assertEqual(len(aGraph.getAllGUIObjects()), 0)
        self.assertEqual(len(aGraph.getAllComments()), 0)
        self.assertEqual(len(aGraph.getAllFrames()), 0)
        self.assertEqual(len(aGraph.getAllNavigationPins()), 0)

        os.remove(docAbsPath)
        log.info("Test MDLGraph: GUI Objects: OK\n")


    def test_SortAsDAG(self):
        """
        This test checks sorting the nodes of a graph
        """
        log.info("Test MDLGraph: Sort as DAG")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Dag.sbs')

        mdlGraph = sbsDoc.getMDLGraph('MDL_Material')
        unsortedNodes = copy.copy(mdlGraph.mNodes)
        sortedNodes = mdlGraph.sortNodesAsDAG()
        self.assertEqual(mdlGraph.mNodes, sortedNodes)
        refSortedIndices = [10, 14, 5, 3, 17, 8, 20, 18, 19, 13, 4, 16, 7, 15, 2, 6, 12, 9, 11, 1, 0]
        for i, index in enumerate(refSortedIndices):
            self.assertEqual(sortedNodes[i], unsortedNodes[index])

        log.info("Test MDLGraph: Sort as DAG: OK\n")


    def test_CreateNodesBasicTypes(self):
        """
        This test checks the creation of mdl nodes with basic types, with all kind of types (atomic, compound, vector..)
        """
        log.info("Test MDLGraph: Create basic mdl nodes")
        yOffset = [0, 96]
        destFile = 'test_MDL_Types.sbs'
        destPath = _convertToAbsPath('./resources/'+destFile)
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath)
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='MDL_Material', aCreateOutputNode=False)

        floatNode = mdlGraph.createMDLNodeInstance(aPath='mdl::float(bool)')
        n= mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float2', aName='myFloat2', aGUIPos=floatNode.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2(float)', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2(float,float)', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2(float,float).x(float2)', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2@(float2,int)', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float2[]', aName='myFloat2[]', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float2x2', aName='myFloat2x2', aExposed=True, aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2x2(float)', aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeInstance(aPath='mdl::float2x2(float,float,float,float)', aGUIPos=n.getOffsetPosition(yOffset))

        cst = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float', aName='myFloat', aExposed=True, aGUIPos=n.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeConst(aConstTypePath='mdl::color', aName='myColor', aGUIPos=cst.getOffsetPosition(yOffset))
        n= mdlGraph.createMDLNodeConst(aConstTypePath='mdl::base::color_layer', aName='myColorLayer', aGUIPos=n.getOffsetPosition(yOffset))

        # Check connection to an exposed constant is remove after unexposing the constant
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=floatNode, aRightNode=cst), sbscommon.SBSConnection)
        self.assertTrue(cst.isConnectedTo(aLeftNode=floatNode))
        self.assertTrue(cst.getMDLImplConstant().isExposed())
        mdlGraph.deleteInputParameter(aInputParameter=cst)
        self.assertFalse(cst.getMDLImplConstant().isExposed())
        self.assertFalse(cst.isConnectedTo(aLeftNode=floatNode))

        n= mdlGraph.createMDLNodeSelector(aGUIPos=n.getOffsetPosition(yOffset))

        instancePath = sbsDoc.buildAbsPathFromRelToMePath('MDL_Material.sbs')
        inst = mdlGraph.createMDLNodeMDLGraphInstanceFromPath(aSBSDocument=sbsDoc, aPath=instancePath, aGUIPos=n.getOffsetPosition(yOffset))

        # Check nb of inputs / parameters
        self.assertEqual(len(inst.getDefinition().getAllInputs()), 7)
        param = inst.getParameter('roughness')
        self.assertFalse(param.acceptConnection())
        inst.setPinVisibilityForParameter('roughness', True)
        self.assertTrue(param.acceptConnection())
        self.assertEqual(len(inst.getDefinition().getAllInputs()), 8)
        inst.setPinVisibilityForParameter('roughness', False)


        sbsInstancePath = 'sbs://blue_noise.sbs/blue_noise_fast'
        n= mdlGraph.createMDLNodeSBSGraphInstanceFromPath(aSBSDocument=sbsDoc, aPath=sbsInstancePath, aGUIPos=inst.getOffsetPosition(yOffset))

        cst1 = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float', aGUIPos=n.getOffsetPosition(yOffset))
        cst2 = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float', aGUIPos=cst1.getOffsetPosition(yOffset))
        cst3 = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float', aExposed=True, aGUIPos=cst2.getOffsetPosition(yOffset))
        cst4 = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float', aExposed=True, aGUIPos=cst3.getOffsetPosition(yOffset))
        self.assertTrue(cst1.getMDLImplConstant().mIdentifier, 'float')
        self.assertTrue(cst2.getMDLImplConstant().mIdentifier, 'float')
        self.assertTrue(cst3.getMDLImplConstant().mIdentifier, 'float_1')
        self.assertTrue(cst4.getMDLImplConstant().mIdentifier, 'float_2')

        aInputs = mdlGraph.getAllInputs()
        self.assertEqual(len(aInputs), 3)
        self.assertEqual(len(aInputs), len(mdlGraph.getInputParameters()))
        self.assertEqual(len(mdlGraph.getInputImages()), 0)
        self.assertEqual(mdlGraph.getInput('float_1'), cst3)

        sbsInstancePath = 'MDL_Material.sbs/blue_noise_fast'
        n= mdlGraph.createMDLNodeSBSGraphInstanceFromPath(aSBSDocument=sbsDoc, aPath=sbsInstancePath, aGUIPos=cst4.getOffsetPosition(yOffset))

        with self.assertRaises(SBSImpossibleActionError):
            mdlGraph.createMDLNodeInstance('mdl::base::compute_spheric_projection(float4,bool)')

        # Check mdl::call default value
        inst = mdlGraph.createMDLNodeInstance('mdl::material_geometry(float3,float,float3)', aGUIPos=n.getOffsetPosition(yOffset))
        param = inst.getParameter('normal')
        self.assertEqual(param.mType, 'mdl::call')
        self.assertTrue(param.mValue.startswith('mdl::state::normal_'))

        # Check the connection to a call
        output = mdlGraph.createMDLNodeOutput(aGUIPos=inst.getOffsetPosition(yOffset))
        conn = mdlGraph.connectNodes(aLeftNode=inst, aRightNode=output, aRightNodeInput='geometry')
        self.assertIsInstance(conn, sbscommon.SBSConnection)

        cst = mdlGraph.createMDLNodeConst('mdl::double2[]', aGUIPos=output.getOffsetPosition(yOffset))
        param = cst.getParameter()
        self.assertIsInstance(param, MDLOperandArray)
        self.assertEqual(param.getItems(), [])

        inst = mdlGraph.createMDLNodeInstance('mdl::float[].len(float[])', aGUIPos=cst.getOffsetPosition(yOffset))
        param = inst.getParameter('a')
        self.assertIsInstance(param, MDLOperandArray)
        self.assertEqual(param.getItems(), [])

        inst = mdlGraph.createMDLNodeInstance('mdl::alg::materials::physically_metallic_roughness::physically_metallic_roughness', aGUIPos=inst.getOffsetPosition(yOffset))
        self.assertEqual(inst.getParameterValue('baseColor'), '0.214041;0.214041;0.214041')
        self.assertTrue(inst.isAPotentialOutput())

        sbsDoc.writeDoc()
        resDoc = MDLGraphTests.openTestDocument(destFile)
        self.assertIsInstance(resDoc, substance.SBSDocument)
        self.assertTrue(sbsDoc.equals(resDoc))

        refDoc = MDLGraphTests.openTestDocument('MDL_Types.sbs')
        self.assertTrue(sbsDoc.equals(refDoc))

        # create passthrough
        mdl_graph = sbsDoc.createMDLGraph(aGraphIdentifier='test')
        passthrough = mdl_graph.createMDLNodePassThrough()
        const = mdl_graph.createMDLNodeConst(aConstTypePath='mdl::float', aName='myFloat')
        function = mdl_graph.createMDLNodeInstance(aPath='mdl::color(float)')
        mdl_graph.connectNodes(const, passthrough)
        mdl_graph.connectNodes(passthrough, function)
        mdl_graph.disconnectNodes(passthrough, function)
        mdl_graph.disconnectNodes(const, passthrough)

        os.remove(destPath)


    def test_InputParameters(self):
        """
        This test checks adding, getting and deleting input parameters on a graph
        """
        log.info("Test MDLGraph: Input parameters")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')

        mdlGraph = sbsDoc.getMDLGraph('MDL_Material')
        inputParams = mdlGraph.getAllInputs()
        self.assertEqual(len(inputParams), 8)

        baseColor = mdlGraph.getInputParameter('base_color')
        self.assertTrue(baseColor.isAnInput())
        self.assertIsInstance(baseColor, MDLNode)

        self.assertTrue(mdlGraph.deleteInputParameter(baseColor))
        self.assertFalse(baseColor.isAnInput())
        self.assertEqual(len(mdlGraph.getAllMDLConstantsWithName('base_color')), 1)

        mdlGraph.setConstantAsInputParameter(aMDLNode=baseColor)
        self.assertTrue(baseColor.isAnInput())
        self.assertTrue(mdlGraph.deleteInputParameter('base_color', aRemoveConstantNode=True))
        self.assertIsNone(mdlGraph.getNode(baseColor))
        self.assertIsNone(mdlGraph.getInputParameter('base_color'))

        self.assertTrue(mdlGraph.deleteInputParameter('metallic'))
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.deleteInputParameter('Invalid')
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.deleteInputParameter(None)
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.deleteInputParameter(baseColor)

        cstName = 'newParam'
        cst = mdlGraph.createMDLNodeConst(aName=cstName, aConstTypePath='mdl::float')
        self.assertIsNone(mdlGraph.getInput(cstName))

        mdlGraph.setConstantAsInputParameter(cst)
        self.assertEqual(cst.getMDLImplConstant().getIdentifier(), cstName)

        cst = mdlGraph.createMDLNodeConst(aName=cstName, aConstTypePath='mdl::float')
        mdlGraph.setConstantAsInputParameter(cst)
        self.assertEqual(cst.getMDLImplConstant().getIdentifier(), cstName+'_1')

        self.assertEqual(mdlGraph.getInputIndex('texture_2d_1000'), 3)
        self.assertEqual(mdlGraph.getInputIndex(cst), 7)

        mdlGraph.setInputIndex(aInput='texture_2d_1000', aIndex=0)
        self.assertEqual(mdlGraph.getInputIndex('texture_2d_1000'), 0)
        mdlGraph.setInputIndex(aInput=cst, aIndex=0)
        self.assertEqual(mdlGraph.getInputIndex(cst), 0)
        self.assertEqual(mdlGraph.getInputIndex('texture_2d_1000'), 1)

        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.setInputIndex('Invalid', 3)
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.setInputIndex('texture_2d_1000', 15)

        inst = mdlGraph.createMDLNodeInstance(aPath='mdl::float(int)')
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.setConstantAsInputParameter(inst)
        with self.assertRaises(SBSImpossibleActionError):   mdlGraph.setConstantAsInputParameter('Invalid')

        log.info("Test MDLGraph: Input parameters: OK\n")


    def test_ConnectDisconnect(self):
        """
        This test checks connecting and disconnecting nodes
        """
        log.info("Test MDLGraph: Connect / Disconnect Nodes")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        mdlGraph = sbsDoc.getMDLGraph('MDL_Material')

        # Check connection/disconnection between MDL instances
        outputNode = mdlGraph.getGraphOutput()
        matSurfNode = mdlGraph.getAllMDLInstancesOf('mdl::material_surface(bsdf,material_emission)')[0]
        self.assertTrue(outputNode.isConnectedTo(matSurfNode))

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=matSurfNode, aRightNode=outputNode, aRightNodeInput='backface'),
                              sbscommon.SBSConnection)
        mdlGraph.disconnectNodes(aLeftNode=matSurfNode, aRightNode=outputNode, aRightNodeInput='backface')
        self.assertTrue(outputNode.isConnectedTo(matSurfNode))
        mdlGraph.disconnectNodes(aLeftNode=matSurfNode, aRightNode=outputNode)

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=matSurfNode, aRightNode=outputNode),
                              sbscommon.SBSConnection)

        # Check connection/disconnection between a Constant and a SBS Graph instance with only one output
        metallicCst = mdlGraph.getInput('metallic')
        sbsInstance = mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='sbs://bnw_spots_1.sbs')[0]
        self.assertTrue(metallicCst.isConnectedTo(sbsInstance))

        mdlGraph.disconnectNodes(aLeftNode=sbsInstance, aRightNode=metallicCst)
        self.assertFalse(metallicCst.isConnectedTo(sbsInstance))

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=metallicCst),
                              sbscommon.SBSConnection)
        self.assertTrue(metallicCst.isConnectedTo(sbsInstance))

        # Check connection/disconnection between a Constant and a SBS Graph instance with several outputs
        specularCst = mdlGraph.getInput('specular_level')
        baseColorCst = mdlGraph.getInput('base_color')
        sbsInstance = mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='pkg:///New_Graph')[0]
        ggx = mdlGraph.getAllMDLInstancesOf('mdl::df::microfacet_ggx_smith_bsdf(float,float,color,float3,::df::scatter_mode,string)')[0]
        normal = mdlGraph.getAllMDLConstantsWithName('normal')[0]

        self.assertTrue(specularCst.isConnectedTo(sbsInstance))
        self.assertFalse(baseColorCst.isConnectedTo(sbsInstance))
        self.assertFalse(ggx.isConnectedTo(sbsInstance))
        self.assertFalse(normal.isConnectedTo(sbsInstance))

        mdlGraph.disconnectNodes(aLeftNode=sbsInstance, aRightNode=specularCst)
        self.assertFalse(specularCst.isConnectedTo(sbsInstance))

        # - Check that the compatible output is taken by default
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=specularCst),
                              sbscommon.SBSConnection)
        self.assertTrue(specularCst.isConnectedTo(sbsInstance))

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=baseColorCst),
                              sbscommon.SBSConnection)
        self.assertTrue(baseColorCst.isConnectedTo(sbsInstance))

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=ggx, aRightNodeInput='tangent_u'),
                              sbscommon.SBSConnection)
        self.assertTrue(ggx.isConnectedTo(sbsInstance))

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=normal),
                              sbscommon.SBSConnection)
        self.assertTrue(normal.isConnectedTo(sbsInstance))


        mdlGraph.disconnectNodes(aLeftNode=sbsInstance, aRightNode=specularCst)
        mdlGraph.disconnectNodes(aLeftNode=sbsInstance, aRightNode=baseColorCst)

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=specularCst, aLeftNodeOutput='output_1'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=outputNode),
                              sbscommon.SBSConnection)

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=outputNode),
                              sbscommon.SBSConnection)

        # Check connection/disconnection between a texture and a SBS Graph instance
        textureNode = mdlGraph.getInput('texture_2d_1001')
        self.assertFalse(sbsInstance.isConnectedTo(textureNode))
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=textureNode, aRightNode=sbsInstance),
                              sbscommon.SBSConnection)
        self.assertTrue(sbsInstance.isConnectedTo(textureNode))

        # Check that exception is raised for all invalid cases
        opMul = mdlGraph.getNodesConnectedFrom(specularCst)[0]
        self.assertIsInstance(opMul, MDLNode)

        with self.assertRaises(SBSImpossibleActionError):   # Incompatible type
            mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=specularCst, aLeftNodeOutput='output')
        with self.assertRaises(SBSImpossibleActionError):   # Invalid input
            mdlGraph.connectNodes(aLeftNode=textureNode, aRightNode=sbsInstance, aRightNodeInput='invalid')
        with self.assertRaises(SBSImpossibleActionError):   # Cycle
            mdlGraph.connectNodes(aLeftNode=specularCst, aRightNode=specularCst)
        with self.assertRaises(SBSImpossibleActionError):   # Cycle
            mdlGraph.connectNodes(aLeftNode=opMul, aRightNode=specularCst)

        # Check calls
        geom = mdlGraph.getAllMDLInstancesOf('mdl::material_geometry(float3,float,float3)')[0]
        newOutput = mdlGraph.createMDLNodeOutput()
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=geom, aRightNode=newOutput, aRightNodeInput='geometry'),
                              sbscommon.SBSConnection)

        # Check states
        normState = mdlGraph.createMDLNodeInstance(aPath='mdl::state::normal()')
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=normState, aRightNode=geom),
                              sbscommon.SBSConnection)


        # Check deleting the output node
        self.assertEqual(mdlGraph.getGraphOutputNode(), newOutput)
        mdlGraph.deleteNode(newOutput)
        self.assertEqual(mdlGraph.getGraphOutputNode(), None)

        destPath = sbsDoc.buildAbsPathFromRelToMePath('testConnections.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        os.remove(destPath)

        log.info("Test MDLGraph: Connect / Disconnect Nodes: OK\n")


    def test_Parameters(self):
        """
        This test checks getting and setting Parameters on MDL nodes
        """
        log.info("Test MDLGraph: Parameters")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        mdlGraph = sbsDoc.getMDLGraph('MDL_Material')

        # Case of a constant
        cst = mdlGraph.getAllMDLConstantsWithName('roughness')[0]
        self.assertEqual(cst.getParameterValue('roughness'), '0.5')

        cst.setParameterValue('roughness', 0.7)
        self.assertEqual(cst.getParameterValue('roughness'), '0.7')
        cst.resetParameter('roughness')
        self.assertEqual(cst.getParameterValue('roughness'), '0')

        self.assertIsNone(cst.getParameterValue('invalid'))
        with self.assertRaises(SBSLibraryError):
            cst.setParameterValue('invalid', 0.7)

        texture = mdlGraph.getInput('texture_2d_1001')
        res = sbsDoc.getSBSResource('Craters')
        self.assertEqual(texture.getParameterValue('texture_2d_1001'), res.getPkgResourcePath())
        texture.resetParameter()
        self.assertEqual(texture.getParameterValue('texture_2d_1001'), '')

        enum = mdlGraph.getAllMDLConstantsWithName('projection_mode')[0]
        self.assertEqual(enum.getParameterValue(), '1')
        enum.setParameterValue('projection_mode', 3)
        self.assertEqual(enum.getParameterValue(), '3')

        # - Check with a constant matrix
        cst = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float2x2')
        self.assertEqual(cst.getParameterValue(), '0;0;0;0')
        cst.setParameterValue('float2x2', [1,2,3,4])
        self.assertEqual(cst.getParameterValue(), '1;2;3;4')

        # - Check with a constant array
        cst = mdlGraph.getAllMDLConstantsOfType(aType='mdl::color[]')[0]
        param = cst.getParameter()
        self.assertIsInstance(param, MDLOperandArray)
        self.assertIsInstance(cst.getParameterValue(), list)
        self.assertEqual(cst.getParameterValue('color[0]'), '1.000000;0.000000;0.000000')
        self.assertEqual(cst.getParameterValue('color[1]'), '0.000000;1.000000;0.000000')
        self.assertIsNone(cst.getParameterValue('color[2]'))
        self.assertIsInstance(param.addItem(aValue=[0.5, 0.5, 0.5]), MDLOperandValue)
        self.assertEqual(param.getSize(), 3)

        cst.setParameterValue('color[0]', [0.5,0.5,0.5])
        self.assertEqual(cst.getParameterValue('color[0]'), '0.5;0.5;0.5')

        with self.assertRaises(SBSLibraryError):
            cst.setParameterValue('color[4]', [0.5,0.5,0.5])

        cstCopy = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::color[]')
        cstCopy.setParameterValue('color[]', cst.getParameterValue())
        cst.resetParameter()
        self.assertEqual(param.getSize(), 0)


        # Case of a MDL instance
        # NOTE(andrea.machizaud) not the actual signature, but it will be migrated to this versionned function
        node_material_constructors = mdlGraph.getAllMDLInstancesOf('mdl::material$1.4(bool,material_surface,material_surface,color,material_volume,material_geometry)')
        self.assertGreater(len(node_material_constructors), 0, 'Could not find any node matching "{}"'.format('mdl::material$1.4(bool,material_surface,material_surface,color,material_volume,material_geometry)'))

        output = node_material_constructors[0]
        self.assertEqual(output.getParameterValue('thin_walled'), 'false')

        output.setParameterValue('thin_walled', True)
        self.assertEqual(output.getParameterValue('thin_walled'), 'true')

        self.assertEqual(output.getParameterValue('ior'), '1.000000;1.000000;1.000000')
        output.setParameterValue('ior', [0.2, 0.8, 0.7])
        self.assertEqual(output.getParameterValue('ior'), '0.2;0.8;0.7')
        output.resetParameter('ior')
        self.assertEqual(output.getParameterValue('ior'), '0;0;0')

        inst = mdlGraph.createMDLNodeInstance(aPath='mdl::float2x2(float,float,float,float)')
        self.assertEqual(inst.getParameterValue('m00'), '0')
        inst.setParameterValue('m00', 1.123)
        self.assertEqual(inst.getParameterValue('m00'), '1.123')
        inst.resetParameter('m00')
        self.assertEqual(inst.getParameterValue('m00'), '0')

        # - Check with MDLOperandStruct
        self.assertIsInstance(output.getParameterValue('volume'), MDLOperands)
        self.assertEqual(output.getParameterValue('volume/absorption_coefficient'), '0;0;0')
        self.assertEqual(output.getParameterValue('volume/scattering'), '')
        output.setParameterValue('volume/absorption_coefficient', [0.2,0.3,0.4])
        self.assertEqual(output.getParameterValue('volume/absorption_coefficient'), '0.2;0.3;0.4')
        output.resetParameter('volume/absorption_coefficient')
        self.assertEqual(output.getParameterValue('volume/absorption_coefficient'), '0;0;0')

        with self.assertRaises(SBSLibraryError):
            output.setParameterValue('volume/invalid', [0.2,0.3,0.4])


        # Case of a SBS Graph instance
        sbsInst = mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='pkg:///New_Graph')[0]
        self.assertEqual(sbsInst.getParameterValue('$tiling'), '0.5')
        sbsInst.setParameterValue('$tiling', 0.2)
        self.assertEqual(sbsInst.getParameterValue('$tiling'), '0.2')

        self.assertEqual(sbsInst.getParameterValue('$pixelsize'), '1 1')
        sbsInst.setParameterValue('$pixelsize', [0.2, 0.8])
        self.assertEqual(sbsInst.getParameterValue('$pixelsize'), '0.2 0.8')

        self.assertEqual(sbsInst.getParameterValue('background'), '0 0 0 0')
        sbsInst.setParameterValue('background', [0.2, 0.8, 0.5, 1])
        self.assertEqual(sbsInst.getParameterValue('background'), '0.2 0.8 0.5 1')

        sbsInst.resetParameter('background')
        self.assertEqual(sbsInst.getParameterValue('background'), '0 0 0 0')
        self.assertTrue(sbsInst.getParameter('background').isDefaultValue())


        # Case of a MDL Graph instance
        mdlInst = mdlGraph.getAllMDLGraphInstancesOf(aSBSDocument=sbsDoc, aPath=sbsDoc.buildAbsPathFromRelToMePath('MDL_Dag.sbs/MDL_Material'))[0]
        self.assertEqual(mdlInst.getParameterValue('base_color'), '1.000000;1.000000;1.000000')
        mdlInst.setParameterValue('base_color', [0.5, 0.5, 0.5])
        self.assertEqual(mdlInst.getParameterValue('base_color'), '0.5;0.5;0.5')

        mdlInst.resetParameter('base_color')
        self.assertEqual(mdlInst.getParameterValue('base_color'), '1;1;1')


        mdlInst = mdlGraph.getAllMDLGraphInstancesOf(aSBSDocument=sbsDoc, aPath='pkg:///test')[0]
        self.assertIsInstance(mdlInst.getParameterValue('surface'), MDLOperands)
        self.assertEqual(mdlInst.getParameterValue('surface/emission/intensity'), '0.000000;0.000000;1.000000')

        mdlInst.setParameterValue('surface/emission/intensity', [0.2, 0.5, 1])
        self.assertEqual(mdlInst.getParameterValue('surface/emission/intensity'), '0.2;0.5;1')

        mdlInst.resetParameter('surface')
        self.assertEqual(mdlInst.getParameterValue('surface/emission/intensity'), '0;0;1')

        colorParam = mdlInst.getParameter('colorArray')
        self.assertIsInstance(colorParam, MDLOperandArray)
        mdlInst.setParameterValue('colorArray[0]', [0.5,0.5,0.5])
        self.assertEqual(mdlInst.getParameterValue('colorArray[0]'), '0.5;0.5;0.5')
        mdlInst.resetParameter('colorArray')
        self.assertEqual(mdlInst.getParameterValue('colorArray[0]'), '0;1;0')


        # Case of a Selector
        selector = mdlGraph.getNode('1289934280')
        self.assertEqual(selector.getParameterValue(), 'mono')
        self.assertEqual(selector.getParameterValue('member'), 'mono')
        self.assertEqual(selector.getOutputType(), 'mdl::float')

        selector.setParameterValue('member','tint')
        self.assertEqual(selector.getParameterValue(), 'tint')
        self.assertEqual(selector.getOutputType(), 'mdl::color')
        with self.assertRaises(SBSImpossibleActionError):
            selector.setParameterValue('member', 'invalid')

        self.assertEqual(selector.getOutputType(), 'mdl::color')
        selector.setParameterValue('member', 'mono')
        self.assertEqual(selector.getOutputType(), 'mdl::float')

        selector.resetParameter()
        self.assertEqual(selector.getParameterValue('member'), '')

        log.info("Test MDLGraph: Parameters: OK\n")


    def test_CreateNodesWithParameters(self):
        """
        This test checks the creation of mdl nodes with basic types, with all kind of types (atomic, compound, vector..)
        """
        log.info("Test MDLGraph: Create mdl nodes with parameters")
        destFile = 'test_MDL_Nodes_params.sbs'
        destPath = _convertToAbsPath('./resources/'+destFile)
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath)
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='MDL_Material')

        cst = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::float2', aName='myFloat2', aValue=[1.2,2.8],
                                          aAnnotations={mdlenum.MDLAnnotationEnum.HARD_RANGE:[0.1, 0.9],
                                                        mdlenum.MDLAnnotationEnum.IN_GROUP: 'MyGroup'})
        self.assertEqual(cst.getParameterValue(), '1.2;2.8')
        implCst = cst.getMDLImplConstant()
        self.assertEqual(implCst.getAnnotationValue(mdlenum.MDLAnnotationEnum.HARD_RANGE), ['0.1', '0.9'])
        self.assertEqual(implCst.getAnnotationValue(mdlenum.MDLAnnotationEnum.IN_GROUP), ['MyGroup','',''])

        implCst.removeAnnotation(mdlenum.MDLAnnotationEnum.HARD_RANGE)
        self.assertIsNone(implCst.getAnnotationValue(mdlenum.MDLAnnotationEnum.HARD_RANGE))

        self.assertIsNone(implCst.getAnnotationValue(mdlenum.MDLAnnotationEnum.SAMPLER_USAGE))
        self.assertIsNone(implCst.getUsage())
        implCst.setAnnotation(mdlenum.MDLAnnotationEnum.SAMPLER_USAGE, 'emissive')
        self.assertEqual(implCst.getAnnotationValue(mdlenum.MDLAnnotationEnum.SAMPLER_USAGE), 'emissive')
        implCst.setUsage('diffuse')
        self.assertEqual(implCst.getUsage(), 'diffuse')

        cst = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::material_surface',
                                          aParameters={'material_surface/emission/intensity':[1,0,0]})
        self.assertEqual(cst.getParameterValue('material_surface/emission/intensity'), '1;0;0')

        selector = mdlGraph.createMDLNodeSelector(aConnectToNode=cst, aMember='emission')
        self.assertEqual(selector.getParameterValue(), 'emission')

        inst = mdlGraph.createMDLNodeInstance(aPath='mdl::float(int)',
                                              aParameters={'value':3})
        self.assertEqual(inst.getParameterValue('value'), '3')

        sbsInstancePath = sbsDoc.buildAbsPathFromRelToMePath('MDL_Material.sbs/New_Graph')
        sbsInst = mdlGraph.createMDLNodeSBSGraphInstanceFromPath(aSBSDocument=sbsDoc, aPath=sbsInstancePath,
                                                       aParameters={'$tiling':0.8,
                                                                    '$outputsize':[9,7],
                                                                    'background':[0.2,0.3,0.5,1]})
        self.assertEqual(sbsInst.getParameterValue('$tiling'), '0.8')
        self.assertEqual(sbsInst.getParameterValue('background'), '0.2 0.3 0.5 1')

        instancePath = sbsDoc.buildAbsPathFromRelToMePath('MDL_Material.sbs')
        inst = mdlGraph.createMDLNodeMDLGraphInstanceFromPath(aSBSDocument=sbsDoc, aPath=instancePath,
                                                              aParameters={'base_color':[0,0,1]})
        self.assertEqual(inst.getParameterValue('base_color'), '0;0;1')

        sbsDoc.writeDoc()
        os.remove(destPath)


    def test_MDLResources(self):
        """
        This test checks the ability to create a resource used in mdl graph, and to use it in a mdl node
        """
        log.info("Test MDLGraph: Create light profile and mbsdf resources")
        destFile = 'test_MDLResources.sbs'
        destPath = _convertToAbsPath('./resources/'+destFile)
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath)
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='MDL_Material')

        bsdfPath = sbsDoc.buildAbsPathFromRelToMePath('SampleBsdfFile.mbsdf')
        bsdfResLinked = sbsDoc.createLinkedResource(aResourceTypeEnum=sbsenum.ResourceTypeEnum.M_BSDF, aResourcePath=bsdfPath)
        self.assertIsInstance(bsdfResLinked, substance.SBSResource)
        self.assertEqual(bsdfResLinked.mIdentifier, 'SampleBsdfFile')

        mdlNode = mdlGraph.createMDLNodeInstance(aPath='mdl::bsdf_measurement(string)')
        mdlNode.setParameterValue('name', bsdfResLinked.getPkgResourcePath())


        bsdfResImported = sbsDoc.createImportedResource(aResourceTypeEnum=sbsenum.ResourceTypeEnum.M_BSDF, aResourcePath=bsdfPath)
        self.assertIsInstance(bsdfResImported, substance.SBSResource)
        self.assertEqual(bsdfResImported.mIdentifier, 'SampleBsdfFile_1')

        mdlNode = mdlGraph.createMDLNodeInstance(aPath='mdl::bsdf_measurement(string)')
        mdlNode.setParameterValue('name', bsdfResImported.getPkgResourcePath())


        iesPath = sbsDoc.buildAbsPathFromRelToMePath('Comet.IES')
        iesResLinked = sbsDoc.createLinkedResource(aResourceTypeEnum=sbsenum.ResourceTypeEnum.LIGHT_PROFILE, aResourcePath=iesPath)
        self.assertIsInstance(iesResLinked, substance.SBSResource)
        self.assertEqual(iesResLinked.mIdentifier, 'Comet')

        mdlNode = mdlGraph.createMDLNodeInstance(aPath='mdl::light_profile(string)')
        mdlNode.setParameterValue('name', iesResLinked.getPkgResourcePath())


        iesResImported = sbsDoc.createImportedResource(aResourceTypeEnum=sbsenum.ResourceTypeEnum.LIGHT_PROFILE, aResourcePath=iesPath)
        self.assertIsInstance(iesResImported, substance.SBSResource)
        self.assertEqual(iesResImported.mIdentifier, 'Comet_1')

        mdlNode = mdlGraph.createMDLNodeInstance(aPath='mdl::light_profile(string)')
        mdlNode.setParameterValue('name', iesResImported.getPkgResourcePath())

        mdlImpl = mdlNode.getMDLImplMDLInstance()
        self.assertIsNotNone(mdlImpl)

        operand = mdlImpl.getOperand('name')
        self.assertIsNotNone(operand)

        operand.setConnectionAccepted(False)

        resourceFolder = sbsDoc.buildAbsPathFromRelToMePath(destFile[:-4]+'.resources')
        self.assertTrue(os.path.exists(resourceFolder))
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 4)

        # Check that all these nodes don't have input pin
        cstStr = mdlGraph.createMDLNodeConst(aConstTypePath='mdl::string', aValue='nope')
        with self.assertRaises(SBSImpossibleActionError):
            mdlGraph.connectNodes(aLeftNode=cstStr, aRightNode=mdlNode)

        # Enable the connection and try to connect
        mdlNode.setPinVisibilityForParameter(aParameter='name', aVisible=True)
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=cstStr, aRightNode=mdlNode), sbscommon.SBSConnection)
        mdlNode.setPinVisibilityForParameter(aParameter='name', aVisible=False)
        with self.assertRaises(SBSImpossibleActionError):
            mdlGraph.connectNodes(aLeftNode=cstStr, aRightNode=mdlNode)

        sbsDoc.writeDoc()
        shutil.rmtree(resourceFolder)
        os.remove(destPath)


    def test_Definitions(self):
        """
        This test checks getting the definition of MDL Nodes
        """
        log.info("Test MDLGraph: get MDL node definition")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        mdlGraph = sbsDoc.getMDLGraph(aGraphIdentifier='MDL_Material')

        # Non-exposed Constant
        cst = mdlGraph.getAllMDLConstantsWithName(aName='projection_mode')[0]
        nodeDef = cst.getDefinition()
        self.assertEqual(len(nodeDef.getAllInputs()), 0)
        self.assertEqual(len(nodeDef.getAllOutputs()), 1)
        self.assertEqual(len(nodeDef.getAllParameters()),1)
        self.assertIsNone(nodeDef.getInput('projection_mode'))
        self.assertIsInstance(nodeDef.getParameter('projection_mode'), MDLNodeDefParam)

        # Exposed Constant
        cst = mdlGraph.getAllMDLConstantsWithName(aName='base_color')[0]
        nodeDef = cst.getDefinition()
        self.assertEqual(len(nodeDef.getAllInputs()), 1)
        self.assertEqual(len(nodeDef.getAllOutputs()), 1)
        self.assertEqual(len(nodeDef.getAllParameters()),1)
        self.assertIsInstance(nodeDef.getInput('base_color'), MDLNodeDefInput)
        self.assertIsInstance(nodeDef.getParameter('base_color'), MDLNodeDefParam)

        # MDL instance
        inst = mdlGraph.createMDLNodeInstance(aPath='mdl::texture_2d(string,::tex::gamma_mode)')
        nodeDef = inst.getDefinition()
        self.assertEqual(len(nodeDef.getAllInputs()), 2)
        self.assertEqual(len(nodeDef.getAllOutputs()), 1)
        self.assertEqual(len(nodeDef.getAllParameters()),2)

        # MDL Graph instance
        inst = mdlGraph.getAllMDLGraphInstancesOf(aSBSDocument=sbsDoc, aPath=sbsDoc.buildAbsPathFromRelToMePath('MDL_Dag.sbs/MDL_Material'))[0]
        nodeDef = inst.getDefinition()
        self.assertEqual(len(nodeDef.getAllInputs()), 3)
        self.assertEqual(len(nodeDef.getAllOutputs()), 1)
        self.assertEqual(len(nodeDef.getAllParameters()), 7)
        self.assertIsInstance(nodeDef.getInput('base_color'), MDLNodeDefInput)
        self.assertIsInstance(nodeDef.getParameter('base_color'), MDLNodeDefParam)

        # SBS Graph instance
        inst = mdlGraph.getAllSBSInstancesOf(aSBSDocument=sbsDoc, aPath='pkg:///New_Graph')[0]
        nodeDef = inst.getDefinition()
        self.assertEqual(len(nodeDef.getAllInputs()), 2)
        self.assertEqual(len(nodeDef.getAllOutputs()), 3)
        self.assertEqual(len(nodeDef.getAllParameters()), 7)
        self.assertIsNone(nodeDef.getInput('background'))
        self.assertIsInstance(nodeDef.getParameter('background'), MDLNodeDefParam)
        self.assertIsInstance(nodeDef.getOutput('output'), MDLNodeDefOutput)
        self.assertEqual(nodeDef.getOutput('output').getType(), 'mdl::color')
        self.assertEqual(nodeDef.getOutput('output_1').getType(), 'mdl::float')
        self.assertEqual(nodeDef.getOutput('output_2').getType(), 'mdl::float3')


    def test_Iterations(self):
        """
        This test checks the ability to create iterations in a mdl graph
        """
        log.info("Test MDLGraph: get MDL node definition")
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Types.sbs')
        mdlGraph = sbsDoc.getMDLGraph(aGraphIdentifier='MDL_Material')
        offset = [48, 48]
        float1 = mdlGraph.getNode('1378478907')
        float2 = mdlGraph.getNode('1378478908')

        mul = mdlGraph.createMDLNodeInstance(aPath='mdl::operator*(float,float)', aGUIPos=float1.getOffsetPosition(offset))
        mdlGraph.connectNodes(aLeftNode=float1, aRightNode=mul, aRightNodeInput='x')
        mdlGraph.connectNodes(aLeftNode=float2, aRightNode=mul, aRightNodeInput='y')

        createdNodes = mdlGraph.createIterationOnNode(aNodeUID=mul.mUID, aNbIteration=10, aGUIOffset=offset)
        self.assertEqual(len(createdNodes), 10)
        self.assertTrue(createdNodes[0].isConnectedTo(mul))
        self.assertTrue(createdNodes[0].isConnectedTo(float2))
        createdNodes2 = mdlGraph.createIterationOnPattern(aNodeUIDs=[node.mUID for node in createdNodes],
                                          aNbIteration=2,
                                          aGUIOffset = [108,0])
        self.assertEqual(len(createdNodes2), 20)

        self.assertTrue(createdNodes2[0].isConnectedTo(createdNodes[-1]))
        self.assertTrue(createdNodes2[0].isConnectedTo(float2))

        destPath = sbsDoc.buildAbsPathFromRelToMePath('testIteration.sbs')
        sbsDoc.writeDoc(aNewFileAbsPath=destPath)
        os.remove(destPath)



    def test_MoveConnections(self):
        """
        This test checks the facilities to get and modify existing connections
        """
        sbsDoc = MDLGraphTests.openTestDocument('MDL_Material.sbs')
        mdlGraph = sbsDoc.getMDLGraph(aGraphIdentifier='MDL_Material')


        ggx = mdlGraph.getAllMDLInstancesOf('mdl::df::microfacet_ggx_smith_bsdf(float,float,color,float3,::df::scatter_mode,string)')[0]
        dirFactor = mdlGraph.getAllMDLInstancesOf('mdl::df::directional_factor(color,color,float,bsdf)')[0]
        curveLayer = mdlGraph.getAllMDLInstancesOf('mdl::df::custom_curve_layer')[0]
        diffuse = mdlGraph.getAllMDLInstancesOf('mdl::df::diffuse_reflection_bsdf')[0]
        sbsGraph = mdlGraph.getAllSBSInstancesOf(sbsDoc, 'pkg:///New_Graph')[0]
        baseColor = mdlGraph.getAllMDLConstantsWithName('base_color')[0]

        self.assertIsInstance(ggx, MDLNode)
        self.assertIsInstance(dirFactor, MDLNode)
        self.assertIsInstance(curveLayer, MDLNode)
        self.assertIsInstance(diffuse, MDLNode)
        self.assertIsInstance(sbsGraph, MDLNode)
        self.assertIsInstance(baseColor, MDLNode)

        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsGraph, aRightNode=dirFactor, aRightNodeInput='normal_tint'), sbscommon.SBSConnection)
        self.assertIsInstance(mdlGraph.connectNodes(aLeftNode=sbsGraph, aRightNode=dirFactor, aRightNodeInput='grazing_tint'), sbscommon.SBSConnection)

        self.assertTrue(dirFactor.isConnectedTo(ggx))
        self.assertTrue(curveLayer.isConnectedTo(ggx))
        self.assertTrue(curveLayer.isConnectedTo(diffuse))
        self.assertTrue(dirFactor.isConnectedTo(sbsGraph))

        ######################
        # Check output getters
        sbsImpl = sbsGraph.getMDLImplementation()
        self.assertIsInstance(sbsImpl, MDLImplSBSInstance)
        outputIdentifiers = sbsImpl.getDefinition().getAllOutputIdentifiers()
        self.assertEqual(outputIdentifiers, ['output','output_1','output_2'])
        for o in outputIdentifiers:
            ob = sbsImpl.getOutputBridgeUID(o)
            self.assertEqual(sbsImpl.getOutputIdentifier(ob), o)

        # Check output connections getters
        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=ggx)), 2)
        nodesConnected = mdlGraph.getNodesConnectedFrom(aLeftNode=ggx)
        self.assertEqual(len(nodesConnected), 2)
        self.assertTrue(dirFactor in nodesConnected)
        self.assertTrue(curveLayer in nodesConnected)

        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph)), 3)
        nbConnections = {'output':2, 'output_1':1, 'output_2':0}
        for output,nb in list(nbConnections.items()):
            self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph, aLeftNodeOutput=output)), nb)

        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=sbsGraph)), 2)
        nbNodesConnected = {'output':1, 'output_1':1, 'output_2':0}
        for output,nb in list(nbNodesConnected.items()):
            self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=sbsGraph, aLeftNodeOutput=output)), nb)

        # Move the connections of an output pin to another
        # Start from these connections and move to:
        # ggx ---------(base) dir factor    =>      ggx       .--(base) dir factor
        #          \                        =>               /
        #           `--(layer) curve layer  =>               |.--(layer) curve layer
        #           .--(base)               =>               /.--(base)
        # diffuse -/                        =>      diffuse -/
        mdlGraph.moveConnectionsOnPinOutput(aInitialNode=ggx, aTargetNode=diffuse)

        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=ggx)), 0)
        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=ggx)), 0)
        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=diffuse)), 3)
        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=diffuse)), 2)

        # Move the connections of an output pin to another with a SBSInstance
        # Start from these connections and move to:
        # sbsGraph (output) ---------- (normal) dir factor     =>      sbsGraph (output)        -- (normal) dir factor
        #          (output1)       \-- (grazing)                                (output1)      /-- (grazing)
        #          (output2)                                                    (output2)     /
        #                                                      =>                            /
        # baseColor                                            =>      baseColor -----------/
        mdlGraph.moveConnectionsOnPinOutput(aInitialNode=sbsGraph, aInitialNodeOutput='output', aTargetNode=baseColor)

        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph)), 1)
        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph, aLeftNodeOutput='output')), 0)
        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=sbsGraph)), 1)
        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=baseColor)), 2)
        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=baseColor)), 1)
        self.assertTrue(dirFactor.isConnectedTo(aLeftNode=baseColor))

        # Redo the opposite
        mdlGraph.moveConnectionsOnPinOutput(aInitialNode=baseColor, aTargetNode=sbsGraph, aTargetNodeOutput='output')
        self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph)), 3)
        nbConnections = {'output':2, 'output_1':1, 'output_2':0}
        for output,nb in list(nbConnections.items()):
            self.assertEqual(len(mdlGraph.getConnectionsFromNode(aLeftNode=sbsGraph, aLeftNodeOutput=output)), nb)

        self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=sbsGraph)), 2)
        nbNodesConnected = {'output':1, 'output_1':1, 'output_2':0}
        for output,nb in list(nbNodesConnected.items()):
            self.assertEqual(len(mdlGraph.getNodesConnectedFrom(aLeftNode=sbsGraph, aLeftNodeOutput=output)), nb)

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):       # invalid target output
            mdlGraph.moveConnectionsOnPinOutput(aInitialNode=sbsGraph, aInitialNodeOutput='output', aTargetNode=sbsGraph,aTargetNodeOutput='invalid')
        with self.assertRaises(SBSImpossibleActionError):       # invalid initial output
            mdlGraph.moveConnectionsOnPinOutput(aInitialNode=sbsGraph, aInitialNodeOutput='invalid', aTargetNode=baseColor)
        with self.assertRaises(SBSImpossibleActionError):       # incompatible output types
            mdlGraph.moveConnectionsOnPinOutput(aInitialNode=sbsGraph, aInitialNodeOutput='output_1', aTargetNode=baseColor)

        #################################
        # Check input connections getters
        self.assertEqual(len(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer)), 2)
        self.assertEqual(len(mdlGraph.getConnectionsToNode(aRightNode=curveLayer)), 3)
        self.assertEqual(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer, aRightNodeInput='layer')[0], diffuse)

        # Move the connections of an input pin to another
        mdlGraph.disconnectNodes(aLeftNode=diffuse, aRightNode=curveLayer, aRightNodeInput='layer')
        self.assertEqual(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer, aRightNodeInput='base'), [diffuse])
        self.assertEqual(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer, aRightNodeInput='layer'), [])
        mdlGraph.moveConnectionOnPinInput(aInitialNode=curveLayer, aInitialNodeInput='base',
                                          aTargetNode=curveLayer, aTargetNodeInput='layer')

        self.assertEqual(len(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer)), 2)
        self.assertEqual(len(mdlGraph.getConnectionsToNode(aRightNode=curveLayer)), 2)
        self.assertEqual(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer, aRightNodeInput='base'), [])
        self.assertEqual(mdlGraph.getNodesConnectedTo(aRightNode=curveLayer, aRightNodeInput='layer'), [diffuse])

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):   # initial connection not found
            mdlGraph.moveConnectionOnPinInput(aInitialNode=curveLayer, aInitialNodeInput='base',
                                              aTargetNode=curveLayer,  aTargetNodeInput='layer')
        with self.assertRaises(SBSImpossibleActionError):   # incompatible types
            mdlGraph.moveConnectionOnPinInput(aInitialNode=curveLayer, aInitialNodeInput='layer',
                                              aTargetNode=diffuse, aTargetNodeInput='normal_tint')


if __name__ == '__main__':
    unittest.main()
