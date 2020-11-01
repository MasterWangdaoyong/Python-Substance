# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import xml.etree.ElementTree as ET
import sys

from pysbs import python_helpers
from pysbs import context
from pysbs import sbspreset
from pysbs import substance
from pysbs import sbsarchive
from pysbs.api_exceptions import SBSImpossibleActionError
testModule = sys.modules[__name__]


class SBSPresetTests(unittest.TestCase):
    """
    This test checks the parsing of a sbsprs file and basic sbsprs manipulation
    """
    @staticmethod
    def compareXML(aXMLPath1, aXMLPath2):
        def elements_equal(e1, e2):
            if e1.tag != e2.tag:
                log.error('Tag %s is not the same as %s' % (e1.tag, e2.tag))
                return False
            if e1.text != e2.text:
                log.error('Text %s is not the same as %s' % (e1.text, e2.text))
                return False
            if e1.tail != e2.tail:
                log.error('Tail %s is not the same as %s' % (e1.tail, e2.tail))
                return False
            if e1.attrib != e2.attrib:
                log.error('Tail %s is not the same as %s' % (e1.attrib, e2.attrib))
                return False
            if len(e1) != len(e2):
                log.error('Len %d is not the same as %d' % (len(e1), len(e2)))
                return False
            return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))
        treeRef = ET.parse(aXMLPath1)
        treeDest = ET.parse(aXMLPath2)
        return elements_equal(treeRef.getroot(), treeDest.getroot())

    def test_LoadSBSPRS(self):
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/presets.sbsprs')
        aContext = context.Context()

        doc = sbspreset.SBSPRSPresets(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())
        self.assertEqual(doc.getPresetCount(), 8)
        pr = doc.getPresetByLabel('TestPreset')
        self.assertIsNotNone(pr)
        self.assertIs(len(pr.getPresetInputs()), 6)
        self.assertEqual(pr.getUsertags(), 'banana;chocolate')
        self.assertIsNone(doc.getPresetByLabel('Non-existing'))
        with self.assertRaises(SBSImpossibleActionError):
            doc.addPreset(pr)
        inputs_to_test = {
            'dirt_level':.44,
            'dirt_color':[.44, .01, 1.0],
            'dirt_bool':1,
            'dirt_string':'dirt'
        }
        for i, v in inputs_to_test.items():
            sbsprs_input = pr.getPresetInputFromIdentifier(i)
            self.assertIsNotNone(sbsprs_input)
            self.assertEqual(sbsprs_input.getTypedValue(), v)
        sbsprs_input = pr.getPresetInputFromIdentifier('dirt_level')
        self.assertEqual(sbsprs_input.getUID(), 1884124251)
        self.assertEqual(sbsprs_input.getType(), sbspreset.SBSPRSTypes.FLOAT1)
        resultPath = python_helpers.getAbsPathFromModule(testModule, './resources/testPresets.sbsprs')
        doc.writeDoc(resultPath)
        self.assertTrue(SBSPresetTests.compareXML(fileAbsPath, resultPath))
        os.remove(resultPath)

    def test_CreateSBSPRS(self):
        """
        This test creates an sbsprs from scratch
        """
        aContext = context.Context()
        newDoc = python_helpers.getAbsPathFromModule(testModule, './resources/testCreatepresets.sbsprs')
        doc = sbspreset.SBSPRSPresets(aContext, aFileAbsPath=newDoc)
        newPreset = doc.createPreset(aDescription='A Test Preset',
                                     aLabel='test1',
                                     aUsertags='tag1;tag2',
                                     aPkgUrl='DummyGraph')
        newPreset.createPresetInput(aIdentifier='input1',
                                    aUID=1,
                                    aValue='1 2',
                                    aType=sbspreset.SBSPRSTypes.INTEGER2)
        with self.assertRaises(SBSImpossibleActionError):
            newPreset.addPresetInput(newPreset.createPresetInput(aIdentifier='input1',
                                                                 aUID=1,
                                                                 aValue='1',
                                                                 aType=sbspreset.SBSPRSTypes.INTEGER1))
        newPreset.createPresetInput(aIdentifier='input2',
                                    aUID=2,
                                    aValue='1',
                                    aType=sbspreset.SBSPRSTypes.INTEGER1)
        self.assertEqual(newPreset.getPresetInputCount(), 2)
        doc.writeDoc()
        self.assertEqual(doc.getPresetCount(), 1)
        refDoc = python_helpers.getAbsPathFromModule(testModule, './resources/refCreatepresets.sbsprs')
        self.assertTrue(SBSPresetTests.compareXML(refDoc, newDoc))
        os.remove(newDoc)

    def test_CreateSBSPRSFromGraph(self):
        """
        This test creates an sbsprs from scratch
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/presets_no_presets.sbs')
        prsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testNewPresets.sbsprs')
        aContext = context.Context()
        doc = substance.SBSDocument(aContext, fileAbsPath)
        doc.parseDoc()
        prsDoc = sbspreset.SBSPRSPresets(aContext, prsPath)
        graph = doc.getSBSGraphList()[0]
        preset = prsDoc.createPreset(aLabel='New Preset', aDescription='Test', aGraph=graph)
        for aInputParam in graph.getInputParameters():
            preset.createPresetInputFromSBSInput(aInputParam)
        for aInputParam in graph.getInputParameters():
            self.assertIsNotNone(preset.getPresetInput(aInputParam))
        refPrsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refNewPresets.sbsprs')
        prsDoc.writeDoc()
        SBSPresetTests.compareXML(refPrsPath, prsPath)
        os.remove(prsPath)

    def test_ExportPresetsFromSBS(self):
        """
        This test Exports presets from an sbs file
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/presets.sbs')
        aContext = context.Context()

        doc = substance.SBSDocument(aContext, fileAbsPath)
        doc.parseDoc()
        graph = doc.getSBSGraph('PresetGraph')
        outSbsprsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testExportpresets.sbsprs')
        presetDoc = sbspreset.SBSPRSPresets(aContext, outSbsprsPath)
        presetDoc.importAllPresetsFromGraph(graph)
        presetDoc.writeDoc()
        refPath = python_helpers.getAbsPathFromModule(testModule, './resources/refExportpresets.sbsprs')
        self.assertTrue(SBSPresetTests.compareXML(refPath, outSbsprsPath))
        os.remove(outSbsprsPath)

    def test_ImportPresetsFromSBSPRS(self):
        """
        This test Exports presets from an sbs file
        """
        # Note there are mismatching uid's and labels in this document to
        # cover some exceptional cases
        sbsprs = python_helpers.getAbsPathFromModule(testModule, './resources/presets_no_presets.sbsprs')
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/presets_no_presets.sbs')
        aContext = context.Context()

        presetDoc = sbspreset.SBSPRSPresets(aContext, sbsprs)
        presetDoc.parseDoc()
        doc = substance.SBSDocument(aContext, fileAbsPath)
        doc.parseDoc()

        presetDoc.insertAllPresetsInSBS(aDoc=doc)
        outputDocPath = python_helpers.getAbsPathFromModule(testModule, './resources/test_presets_no_presets.sbs')
        doc.writeDoc(outputDocPath)
        refDocPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/refPresets_no_presets.sbs')
        refDoc = substance.SBSDocument(context.Context(), aFileAbsPath=refDocPath)
        refDoc.parseDoc()
        doc = substance.SBSDocument(aContext, outputDocPath)
        doc.parseDoc()

        self.assertTrue(refDoc.equals(doc))
        os.remove(outputDocPath)

    def test_ReadPresetFromSBSAR(self):
        """
        This tests that we can access all the properties from the presets from an sbsar
        file. The assumption is presets.sbsar is cooked from presets.sbs so it should be re-cooked
        if presets.sbs changes
        """
        sbsar_path = python_helpers.getAbsPathFromModule(testModule, './resources/presets.sbsar')
        sbs_path = python_helpers.getAbsPathFromModule(testModule, './resources/presets.sbs')
        aContext = context.Context()
        doc = substance.SBSDocument(aContext, sbs_path)
        doc.parseDoc()

        sbsar = sbsarchive.SBSArchive(aContext, sbsar_path)
        sbsar.parseDoc()

        for sbsar_graph in sbsar.getSBSGraphList():
            sbs_graph = doc.getSBSGraph(sbsar_graph.mLabel)
            self.assertIsNotNone(sbs_graph)
            for sbsar_preset in sbsar_graph.mPresets:
                sbs_preset = sbs_graph.getPreset(sbsar_preset.mLabel)
                self.assertIsNotNone(sbs_preset)
                self.assertEqual(sbs_preset.mUsertags, sbsar_preset.mUsertags)
                self.assertEqual(len(sbs_preset.mPresetInputs), len(sbsar_preset.mPresetInputs))
                for sbsar_input in sbsar_preset.getPresetInputs():
                    sbs_input = sbs_preset.getPresetInputFromIdentifier(sbsar_input.mIdentifier)
                    self.assertIsNotNone(sbs_input)
                    # Skipping values for now, strings, floating points etc. makes it somewhat complicated
if __name__ == '__main__':
    log.info("Test SBSPreset")
    unittest.main()
