# coding: utf-8

import unittest
import os
import shutil
import sys

from pysbs.api_exceptions import SBSImpossibleActionError, SBSProcessInterruptedError
from pysbs import python_helpers
from pysbs import sbsimpactmanager
from pysbs import context
from pysbs import substance
from pysbs import sbsgenerator

testModule = sys.modules[__name__]


class SBSImpactManagerTests(unittest.TestCase):

    @staticmethod
    def getTestResourceDir():
        return python_helpers.getAbsPathFromModule(testModule, 'resources/ImpactPropag')

    @staticmethod
    def mock_raw_input_True(s):
        return 'y'

    def test_GetAllSubstances(self):
        """
        This test checks the correct parsing of a tree to get all the .sbs files. It uses the .sbs provided in the package,
        so the checked value must be updated each time a sbs resource is added to the package.
        """
        pysbsDir = python_helpers.getAbsPathFromModule(testModule, '..')
        IM = sbsimpactmanager.SBSImpactManager()
        sbsFiles = IM.getAllSubstancesInTree(pysbsDir)
        self.assertEqual(len(sbsFiles), 64)


    def test_ImpactSbs2Sbsar(self):
        """
        This test checks changing the extension of a Substance, between .sbs and .sbsar
        """
        def createTestResourceTree(aContext, aSbsFile, aSbsarFile, aFileWithRef):
            """
            Create the Folders and Substances needed for this test
            """
            os.makedirs(os.path.dirname(aFileWithRef))
            sbsWithRef = sbsgenerator.createSBSDocument(aContext, aFileWithRef, 'Graph')
            aGraph = sbsWithRef.getSBSGraph('Graph')
            aGraph.createCompInstanceNodeFromPath(sbsWithRef, aSbsFile)
            aGraph.createCompInstanceNodeFromPath(sbsWithRef, aSbsarFile)
            sbsWithRef.writeDoc()

        def testSequence(interactiveMode, checkMethod):
            aContext = context.Context()
            rootTree = SBSImpactManagerTests.getTestResourceDir() + '2'
            with python_helpers.createTempFolders(rootTree):
                sbsFile = os.path.join(rootTree, '..', 'Flame.sbs')
                sbsarFile = os.path.join(rootTree, '..', 'Flame.sbsar')
                resTree = os.path.join(rootTree, 'ResTree')
                fileWithRef = os.path.join(resTree, 'Ref.sbs')
                fileWithRefCopy = os.path.join(rootTree, 'RefCopy.sbs')

                #Generate a SBS file with a ref on Flame.sbs and Flame.sbsar:
                #ImpactPropag
                #    Ref.sbs (with a ref on ../Flame.sbs AND ../Flame.sbsar
                createTestResourceTree(aContext,
                                       aSbsFile     = sbsFile,
                                       aSbsarFile   = sbsarFile,
                                       aFileWithRef = fileWithRef)
                shutil.copy(fileWithRef, fileWithRefCopy)

                IM = sbsimpactmanager.SBSImpactManager()

                # Replace dependency on Flame.sbs by Flame.sbsar
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=sbsFile, newPath=sbsarFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, sbsarFile)

                # Now replace dependency on Flame.sbsar by Flame.sbs
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=sbsarFile, newPath=sbsFile, withinTree=resTree, interactiveMode=interactiveMode)
                checkMethod(aContext, IM, updatedSBS, fileWithRef, sbsFile)

                # Check himself dependency
                copiedSbs = os.path.join(resTree, os.path.basename(sbsFile))
                shutil.copy(sbsFile, copiedSbs)
                IM.declareSBSMoved(aContext, oldPath=copiedSbs, newPath=sbsFile, withinTree=resTree, interactiveMode=interactiveMode)
                self.assertEqual(len(IM.getUpdatedPackages()), 0)
                self.assertEqual(len(IM.getErrorPackages()), 0)

                return True

        def checkResult(aContext, aIM, aUpdatedSBS, aFileWithRef, aAbsFilePath):
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
            self.assertEqual(len(docWithRef.getAllReferencesOnDependency(depList[0])), 2)
            with self.assertRaises(SBSImpossibleActionError):
                docWithRef.removeDependency(depList[0])

        def checkResultAborted(aContext, aIM, aUpdatedSBS, aFileWithRef, aAbsFilePath):
            """
            Check the resulting dependencies when the process is aborted by the user
            """
            self.assertEqual(len(aUpdatedSBS), 0)
            self.assertEqual(len(aIM.getUpdatedPackages()), 0)
            self.assertEqual(len(aIM.getErrorPackages()), 0)

            docWithRef = substance.SBSDocument(aContext, aFileWithRef)
            docWithRef.parseDoc()
            depList = docWithRef.getSBSDependencyList()
            self.assertEqual(len(depList), 2)
            self.assertEqual(len(docWithRef.getAllReferencesOnDependency(depList[0])), 1)
            self.assertEqual(len(docWithRef.getAllReferencesOnDependency(depList[1])), 1)
            with self.assertRaises(SBSImpossibleActionError):
                docWithRef.removeDependency(depList[0])
            with self.assertRaises(SBSImpossibleActionError):
                docWithRef.removeDependency(depList[1])

        self.assertTrue(testSequence(interactiveMode=False, checkMethod = checkResult))
        sbsimpactmanager.imRawInput = SBSImpactManagerTests.mock_raw_input_True
        self.assertTrue(testSequence(interactiveMode=True, checkMethod = checkResult))

        inputs = ['y', 'n', 'y', 'n', 'y']
        input_generator = (i for i in inputs)
        sbsimpactmanager.imRawInput = lambda prompt: next(input_generator)
        self.assertTrue(testSequence(interactiveMode=True, checkMethod = checkResultAborted))


    def testProcessErrors(self):
        """
        This test checks that the process of update stops correctly or not errors, depending on parameter stopOnException
        """
        def createTestResourceTree(aContext, aResTree, aDestTree, aFileToMove):
            """
            Create the Folders and Substances needed for this test
            """
            os.makedirs(aResTree)
            os.makedirs(aDestTree)
            sbsToMove = sbsgenerator.createSBSDocument(aContext, aFileToMove, 'Graph')
            sbsToMove.writeDoc()
            badFile1 = os.path.join(aResTree, 'Bad1.sbs')
            badFile2 = os.path.join(aResTree, u'Bäd2.sbs')
            fileWithRef = os.path.join(aResTree, 'Ref.sbs')
            open(badFile1, 'w').close()
            open(badFile2, 'w').close()

            sbsWithRef = sbsgenerator.createSBSDocument(aContext, fileWithRef, 'Graph')
            aGraph = sbsWithRef.getSBSGraph('Graph')
            aGraph.createCompInstanceNodeFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/Graph')
            sbsWithRef.writeDoc()

        def testSequence(interactiveMode):
            aContext = context.Context()
            rootTree = SBSImpactManagerTests.getTestResourceDir() + '3'
            with python_helpers.createTempFolders(rootTree):
                destFolderName = u'DestTreë'
                fileToMoveName = u'FiléToMove_errors.sbs'
                destTree = os.path.join(rootTree, destFolderName)
                resTree = os.path.join(rootTree, 'ResTree')
                fileToMove = os.path.join(rootTree, fileToMoveName)

                # Generate this tree:
                # ImpactPropag
                #    FileToMove.sbs
                #    ResTree
                #        Bad1.sbs (invalid file! )
                #        Bad2.sbs (invalid file! )
                #        Ref.sbs  (with a ref on ../FileToMove.sbs)
                #    DestTree
                createTestResourceTree(aContext,
                                       aResTree=resTree,
                                       aDestTree=destTree,
                                       aFileToMove=fileToMove)


                IM = sbsimpactmanager.SBSImpactManager()

                destFile = os.path.join(destTree, fileToMoveName)
                shutil.move(fileToMove, destFile)

                # Check bad path
                with self.assertRaises(SBSProcessInterruptedError):
                    IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode, stopOnException=True)
                self.assertEqual(len(IM.getUpdatedPackages()), 0)
                self.assertEqual(len(IM.getErrorPackages()), 1)

                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode, stopOnException=False)
                self.assertEqual(len(updatedSBS), 1)
                self.assertEqual(len(IM.getUpdatedPackages()), 1)
                self.assertEqual(len(IM.getErrorPackages()), 2)
                return True

        sbsimpactmanager.imRawInput = SBSImpactManagerTests.mock_raw_input_True
        self.assertTrue(testSequence(interactiveMode=True))
        self.assertTrue(testSequence(interactiveMode=False))


    def test_BigTree(self):
        """
        This test checks the processing a big amount of files
        """
        def createTestResourceTree(aContext, aResTree, aDestTree, aFileToMove, aNbFiles):
            """
            Create the Folders and Substances needed for this test
            """
            def createSubstanceWithRef(aDir, aSbsName):
                sbsWithRef = sbsgenerator.createSBSDocument(aContext, os.path.join(aDir, aSbsName), 'Graph')
                aGraph = sbsWithRef.getSBSGraph('Graph')
                aGraph.createCompInstanceNodeFromPath(sbsWithRef, sbsToMove.mFileAbsPath + '/Graph')
                sbsWithRef.writeDoc()

            os.makedirs(aResTree)
            os.makedirs(aDestTree)
            sbsToMove  = sbsgenerator.createSBSDocument(aContext, aFileToMove, 'Graph')
            sbsToMove.writeDoc()

            for i in range(aNbFiles):
                createSubstanceWithRef(aResTree, 'Ref_'+str(i)+'.sbs')
                subDir = os.path.join(aResTree, 'SubDir_'+str(i))
                os.makedirs(subDir)
                for j in range(aNbFiles):
                    createSubstanceWithRef(subDir, 'Ref_' + str(j) + '.sbs')

        def checkResult(aContext, aFileWithRef, aAbsFilePath, aRelFilePath):
            """
            Check the resulting dependency
            """
            docWithRef = substance.SBSDocument(aContext, aFileWithRef)
            docWithRef.parseDoc()
            depList = docWithRef.getSBSDependencyList()
            self.assertEqual(len(depList), 1)
            self.assertEqual(depList[0].mFileAbsPath, os.path.normpath(aAbsFilePath))
            self.assertEqual(depList[0].mFilename, aRelFilePath)

        def testSequence(interactiveMode):
            aContext = context.Context()
            rootTree = SBSImpactManagerTests.getTestResourceDir() + '4'
            with python_helpers.createTempFolders(rootTree):
                destFolderName =   u'DestTreë'
                fileToMoveName = u'FiléToMove_bigTree.sbs'
                destTree = os.path.join(rootTree, destFolderName)
                resTree = os.path.join(rootTree, 'ResTree')
                fileToMove = os.path.join(rootTree, fileToMoveName)
                nbFiles = 10

                #Generate this tree:
                #ImpactPropag
                #    FileToMove.sbs
                #    ResTree
                #       SubDir_0
                #           Ref_0.sbs (with a ref on ../FileToMove.sbs
                #           ...
                #           Ref_99.sbs (with a ref on ../FileToMove.sbs
                #       ...
                #       SubDir_99
                #           Ref_0.sbs (with a ref on ../FileToMove.sbs
                #           ...
                #           Ref_99.sbs (with a ref on ../FileToMove.sbs
                #    DestTree
                createTestResourceTree(aContext,
                                       aResTree     = resTree,
                                       aDestTree    = destTree,
                                       aFileToMove  = fileToMove,
                                       aNbFiles     = nbFiles)

                IM = sbsimpactmanager.SBSImpactManager()

                destFile = os.path.join(destTree, fileToMoveName)
                shutil.move(fileToMove, destFile)

                # Check getting referencing sbs
                referencingSBS = IM.getAllSubstancesWithDependencyOn(aContext, substancePath=fileToMove, withinTree=resTree)
                self.assertEqual(len(referencingSBS), nbFiles * (nbFiles + 1))

                # Update all references
                updatedSBS = IM.declareSBSMoved(aContext, oldPath=fileToMove, newPath=destFile, withinTree=resTree, interactiveMode=interactiveMode)
                self.assertEqual(len(updatedSBS), nbFiles*(nbFiles+1))

                # Check result
                fileWithRef = os.path.join(resTree, 'Ref_0.sbs')
                checkResult(aContext, fileWithRef, aAbsFilePath=destFile, aRelFilePath='../'+destFolderName+'/'+fileToMoveName)

                fileWithRef = os.path.join(resTree, 'SubDir_3', 'Ref_3.sbs')
                checkResult(aContext, fileWithRef, aAbsFilePath=destFile, aRelFilePath='../../'+destFolderName+'/'+fileToMoveName)

                referencingSBS = IM.getAllSubstancesWithDependencyOn(aContext, substancePath=fileToMove, withinTree=resTree)
                self.assertEqual(len(referencingSBS), 0)

                return True

        self.assertTrue(testSequence(interactiveMode=False))
        sbsimpactmanager.imRawInput = SBSImpactManagerTests.mock_raw_input_True
        self.assertTrue(testSequence(interactiveMode=True))


if __name__ == '__main__':
    unittest.main()
