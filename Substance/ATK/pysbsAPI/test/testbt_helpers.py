# coding: utf-8

import unittest
import os
import shutil
import sys

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import sbscleaner
from pysbs import sbsimpactmanager
from pysbs import context
from pysbs import substance
from pysbs import sbsgenerator
from pysbs import sbsenum

testModule = sys.modules[__name__]


class SBSImpactManagerTests(unittest.TestCase):

    @staticmethod
    def getTestResourceDir():
        return python_helpers.getAbsPathFromModule(testModule, 'resources/BTImpactPropag')

    @staticmethod
    def openTestDocument(aFileName):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFileName)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    @staticmethod
    def mock_raw_input_True(s):
        return 'y'


    def test_GlobalClean(self):
        """
        This test checks the global cleaning of a Substance
        """
        sbsDoc = SBSImpactManagerTests.openTestDocument('testCleaner.sbs')
        self.assertEqual(len(sbsDoc.getSBSDependencyList(aIncludeHimself=True)), 2)
        aGraph = sbsDoc.getSBSGraph('Graph')

        instNode = aGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://alveolus.sbs')[0]
        fxMapNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0]
        aGraph.disconnectNodes(aLeftNode=instNode, aRightNode=fxMapNode)

        # Global clean
        sbscleaner.cleanSubstance(sbsDoc)

        self.assertEqual(len(sbsDoc.getSBSDependencyList(aIncludeHimself=True)), 1)

        destPath = sbsDoc.buildAbsPathFromRelToMePath('resCleaner.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destPath))
        resDoc = substance.SBSDocument(context.Context(), destPath)
        self.assertTrue(resDoc.parseDoc())

        refPath = sbsDoc.buildAbsPathFromRelToMePath('refCleaner.sbs')
        refDoc = substance.SBSDocument(context.Context(), refPath)
        self.assertTrue(refDoc.parseDoc())

        self.assertTrue(resDoc.equals(refDoc))
        os.remove(resDoc.mFileAbsPath)

    def test_ImpactMoveUpAndDown(self):
        """
        This test checks the main error cases, and check moving a Substance from a folder to another in different direction.
        It also checks with aliased paths.
        """
        def createTestResourceTree(aContext, aResTree, aDestTree, aFileToMove, aFileWithRef):
            """
            Create the Folders and Substances needed for this test
            """
            os.makedirs(aResTree)
            os.makedirs(aDestTree)
            sbsToMove  = sbsgenerator.createSBSDocument(aContext, aFileToMove, 'Graph')
            sbsToMove.createFunction(aFunctionIdentifier='Function')
            sbsToMove.createMDLGraph(aGraphIdentifier='MDLGraph')
            sbsToMove.writeDoc()

            sbsWithRef = sbsgenerator.createSBSDocument(aContext, aFileWithRef, 'Graph')
            aFunction = sbsWithRef.createFunction(aFunctionIdentifier='Function')
            aFunction.createFunctionInstanceNodeFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/Function')


            try:
                aGraph = sbsWithRef.getSBSGraph('Graph')
                aGraph.createCompInstanceNodeFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/Graph')
                aMDLGraph = sbsWithRef.createMDLGraph(aGraphIdentifier='MDLGraph')
                aMDLGraph.createMDLNodeMDLGraphInstanceFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/MDLGraph')
                aMDLGraph.createMDLNodeSBSGraphInstanceFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/Graph')
            except:
                pass
            sbsWithRef.writeDoc()

        def checkResult(aContext, aIM, aUpdatedSBS, aFileWithRef, aAbsFilePath, aRelFilePath):
            """
            Check the resulting dependency
            """
            self.assertEqual(len(aUpdatedSBS), 1)
            self.assertEqual(len(aIM.getUpdatedPackages()), 1)
            self.assertEqual(len(aIM.getErrorPackages()), 0)

            docWithRef = substance.SBSDocument(aContext, aFileWithRef)
            docWithRef.parseDoc()
            depList = docWithRef.getSBSDependencyList()
            self.assertEqual(len(depList), 1)
            self.assertEqual(depList[0].mFileAbsPath, os.path.normpath(aAbsFilePath))
            self.assertEqual(depList[0].mFilename, aRelFilePath)

        def checkResultAborted(aContext, aIM, aUpdatedSBS, aFileWithRef, aAbsFilePath, aRelFilePath):
            """
            Check the resulting dependencies when the process is aborted by the user
            """
            self.assertEqual(len(aUpdatedSBS), 0)
            self.assertEqual(len(aIM.getUpdatedPackages()), 0)
            self.assertEqual(len(aIM.getErrorPackages()), 0)

            docWithRef = substance.SBSDocument(aContext, aFileWithRef)
            docWithRef.parseDoc()
            depList = docWithRef.getSBSDependencyList()
            self.assertEqual(len(depList), 1)

        def testSequence(interactiveMode, checkMethod):
            """
            Test scenario
            """
            aContext = context.Context()
            rootTree = SBSImpactManagerTests.getTestResourceDir() + '1'
            with python_helpers.createTempFolders(rootTree):
                destFolderName =   u'DestTreë'
                fileToMoveName = u'FiléToMove_upDown.sbs'
                destTree = os.path.join(rootTree, destFolderName)
                resTree = os.path.join(rootTree, 'ResTree')
                fileToMove = os.path.join(rootTree, fileToMoveName)
                fileWithRef = os.path.join(resTree, 'Ref.sbs')

                #Generate this tree:
                #BTImpactPropag
                #    FileToMove.sbs
                #    ResTree
                #        Ref.sbs (with a ref on ../FileToMove.sbs
                #    DestTree
                createTestResourceTree(aContext,
                                       aResTree     = resTree,
                                       aDestTree    = destTree,
                                       aFileToMove  = fileToMove,
                                       aFileWithRef = fileWithRef)

                IM = sbsimpactmanager.SBSImpactManager()
                # Check bad path
                with self.assertRaises(SBSImpossibleActionError):
                    IM.declareSBSMoved(aContext, oldPath = fileToMove, newPath = destTree, withinTree = resTree, interactiveMode=interactiveMode)

                # Check file not moved yet
                destFile = os.path.join(destTree, fileToMoveName)
                with self.assertRaises(SBSImpossibleActionError):
                    IM.declareSBSMoved(aContext, oldPath = fileToMove, newPath = destFile, withinTree = resTree, interactiveMode=interactiveMode)

                # Check bad extension
                destFile = os.path.join(destTree, 'FileToMove.bad')
                shutil.copy(fileToMove, destFile)
                with self.assertRaises(SBSImpossibleActionError):
                    IM.declareSBSMoved(aContext, oldPath = fileToMove, newPath = destFile, withinTree = resTree, interactiveMode=interactiveMode)
                os.remove(destFile)

                # Check correct case
                destFile = os.path.join(destTree, fileToMoveName)
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='../'+destFolderName+'/'+fileToMoveName)

                # At this point we have:
                # BTImpactPropag
                #   ResTree
                #       Ref.sbs (with a ref on ../DestTree/FileToMove.sbs
                #   DestTree
                #       FileToMove.sbs
                # Do the reverse operation => test down to up move
                fileToMove, destFile = destFile, fileToMove
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='../'+fileToMoveName)

                # Redo the same process but with an alias on the rootTree folder
                aContext.getUrlAliasMgr().setAliasAbsPath('tmp://', rootTree)
                fileToMove, destFile = destFile, fileToMove
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='tmp://'+destFolderName+'/'+fileToMoveName)

                # Redo the reverse operation => test down to up move
                fileToMove, destFile = destFile, fileToMove
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='tmp://'+fileToMoveName)

                # At this point we have:
                # BTImpactPropag
                #    FileToMove.sbs
                #    ResTree
                #        Ref.sbs (with a ref on tmp://FileToMove.sbs
                #    DestTree
                # This time move the file outside of the alias context
                fileToMove = destFile
                destFile = os.path.join(rootTree, '..', fileToMoveName)
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='../../'+fileToMoveName)
                fileToMove, destFile = destFile, fileToMove
                shutil.move(fileToMove, destFile)
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, aAbsFilePath=destFile, aRelFilePath='tmp://'+fileToMoveName)

                return True

        self.assertTrue(testSequence(interactiveMode=False, checkMethod=checkResult))
        sbsimpactmanager.imRawInput = SBSImpactManagerTests.mock_raw_input_True
        self.assertTrue(testSequence(interactiveMode=True, checkMethod=checkResult))

        inputs = ['y', 'n', 'y', 'y', 'n', 'y', 'y', 'n', 'y']
        input_generator = (i for i in inputs)
        sbsimpactmanager.imRawInput = lambda prompt: next(input_generator)
        self.assertTrue(testSequence(interactiveMode=True, checkMethod=checkResultAborted))


if __name__ == '__main__':
    unittest.main()
