# coding: utf-8
from __future__ import print_function

import unittest
import os
import platform
import shutil
import sys
import subprocess
import json

from subprocess import PIPE
from pysbs import context, sbsgenerator, substance, sbsenum, batchtools
from pysbs import python_helpers as helpers

testModule = sys.modules[__name__]


def _getStdout(popen_object):
    popen_object.wait()
    output = popen_object.stdout.read().decode('utf-8')
    popen_object.stdout.close()
    return output


class SBSBatchtoolsTest(unittest.TestCase):
    _testDir = helpers.getAbsPathFromModule(testModule, './resources/_sbsbatchtoolstest')
    _dataDir = helpers.getAbsPathFromModule(testModule, './resources')

    def setUp(self):
        tree = SBSBatchtoolsTest._getResourceDir()
        if os.path.exists(tree):
            shutil.rmtree(tree)
        os.mkdir(SBSBatchtoolsTest._getResourceDir())

    def tearDown(self):
        shutil.rmtree(SBSBatchtoolsTest._getResourceDir())

    @staticmethod
    def _getResourceDir():
        return SBSBatchtoolsTest._testDir

    @staticmethod
    def _getResourcePath(aFileName):
        return os.path.join(SBSBatchtoolsTest._getResourceDir(), aFileName)

    @staticmethod
    def _getDataPath(aFileName):
        return os.path.join(SBSBatchtoolsTest._dataDir, aFileName)

    @staticmethod
    def _createImageWithSbsrender(aFileName):
        basename, extension = os.path.splitext(SBSBatchtoolsTest._getResourcePath(aFileName))
        directory, name = os.path.split(basename)
        sbsname = basename + ".sbs"
        sbsarname = basename + ".sbsar"
        extension = extension[1:]
        sbsContext = context.Context()
        sbsDoc = sbsgenerator.createSBSDocument(sbsContext,
                                                aFileAbsPath=sbsname,
                                                aGraphIdentifier='img_generator')
        graph = sbsDoc.getSBSGraph(aGraphIdentifier='img_generator')
        colorNode = graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM,
                                               aParameters={sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [0.8, 0.3, 0.6, 1]},
                                               aGUIPos=[0, 0, 0])
        outputNode = graph.createOutputNode(aIdentifier='BaseColor',
                                            aGUIPos=[48, 0, 0],
                                            aUsages={sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})
        graph.connectNodes(aLeftNode=colorNode, aRightNode=outputNode)
        sbsDoc.writeDoc()

        batchtools.sbscooker(sbsname, output_name=name, output_path=directory).wait()
        batchtools.sbsrender_render(sbsarname, output_name=name, output_format=extension, output_path=directory).wait()
        os.remove(sbsname)
        os.remove(sbsarname)
        return os.path.join(directory, name + "." + extension)

    @unittest.skipIf(platform.system() == 'Linux', 'sbsbaker cannot run on a machine without a graphic environment.')
    def test_batchtool_calls(self):
        """
        This test checks the global usage of the batchtools commands
        """
        # Create a simple sbs to be cooked
        sbsContext = context.Context()
        sbsDoc = sbsgenerator.createSBSDocument(sbsContext,
                                                aFileAbsPath=SBSBatchtoolsTest._getResourcePath("cookme.sbs"),
                                                aGraphIdentifier='SimpleMaterial')
        graph = sbsDoc.getSBSGraph(aGraphIdentifier='SimpleMaterial')
        colorNode = graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM,
                                               aParameters={sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [1, 0, 0, 1]},
                                               aGUIPos=[0, 0, 0])
        outputNode = graph.createOutputNode(aIdentifier='BaseColor',
                                            aGUIPos=[48, 0, 0],
                                            aUsages={sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})
        graph.connectNodes(aLeftNode=colorNode, aRightNode=outputNode)
        sbsDoc.writeDoc()

        # sbsmutator edit --version
        sbsmutator_edit_version_process = batchtools.sbsmutator_edit(version=True, stdout=PIPE)
        sbsmutator_edit_version_process.wait()
        self.assertIsNotNone(sbsmutator_edit_version_process)
        self.assertEqual(sbsmutator_edit_version_process.returncode, 0)
        sbsmutator_edit_version_process.stdout.close()

        # check all subcommand have the same version
        updater_version = _getStdout(batchtools.sbsupdater(version=True, stdout=PIPE))
        self.assertTrue(updater_version.startswith("version"))
        self.assertEqual(updater_version, _getStdout(batchtools.sbsbaker_info(version=True, stdout=PIPE)))
        self.assertEqual(updater_version, _getStdout(batchtools.sbscooker(version=True, stdout=PIPE)))
        self.assertEqual(updater_version, _getStdout(batchtools.sbsmutator_info(version=True, stdout=PIPE)))
        self.assertEqual(updater_version, _getStdout(batchtools.sbsrender_info(version=True, stdout=PIPE)))

        # sbsmutator edit --this-parameter-does-not-exists 1
        with self.assertRaises(TypeError): batchtools.sbsmutator_edit(this_parameter_does_not_exist=1)

        # sbscooker cookme.sbs --compression-mode "should be an integer"
        with self.assertRaises(TypeError): batchtools.sbscooker(sbsDoc.mFileAbsPath, compression_mode="should be an integer")

    def test_mutator(self):
        # Creating bitmap
        imagePath = SBSBatchtoolsTest._createImageWithSbsrender("uniform.png")

        # Create initial package
        sbsContext = context.Context()
        initialDoc = sbsgenerator.createSBSDocument(
            sbsContext,
            aFileAbsPath=SBSBatchtoolsTest._getResourcePath("sbsmutator-edit-connect-image-init.sbs"),
            aGraphIdentifier='gamma')
        initialGraph = initialDoc.getSBSGraph(aGraphIdentifier='gamma')
        theInitialBaseColorInputNode = initialGraph.createInputNode(aIdentifier='iBaseColor',
                                                                    aGUIPos=[0, 0, 0])
        theInitialBaseColorOutputNode = initialGraph.createOutputNode(
            aIdentifier='BaseColor',
            aGUIPos=[48, 0, 0],
            aUsages={sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})
        # TODO: Warning regression with GUIName and Mutator, mutator remove GUIName
        # theInitialBaseColorOutputNode.mGUIName = "Terminus"
        initialGraph.connectNodes(aLeftNode=theInitialBaseColorInputNode, aRightNode=theInitialBaseColorOutputNode)
        initialDoc.writeDoc()

        # Create result when replacing image with bitmap
        connectedDoc = sbsgenerator.createSBSDocument(
            sbsContext,
            aFileAbsPath=SBSBatchtoolsTest._getResourcePath("sbsmutator-edit-connect-image-target.sbs"),
            aGraphIdentifier='gamma')
        connectedGraph = connectedDoc.getSBSGraph(aGraphIdentifier='gamma')
        theconnectedImageResource = connectedDoc.createLinkedResource(
            imagePath,
            sbsenum.ResourceTypeEnum.BITMAP,
            aParentFolder="no_root",
        )
        connectedDoc.moveObjectUnderGroup(theconnectedImageResource, None)
        connectedDoc.writeDoc()

        connectedDoc.removeObject("pkg://no_root")
        theconnectedBaseColorInputNode = connectedGraph.createCompFilterNode(
            aFilter=sbsenum.FilterEnum.BITMAP,
            aParameters={
                sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH: theconnectedImageResource.getPkgResourcePath(),
                sbsenum.CompNodeParamEnum.OUTPUT_SIZE: [sbsenum.OutputSizeEnum.SIZE_256,
                                                        sbsenum.OutputSizeEnum.SIZE_256],
                sbsenum.CompNodeParamEnum.OUTPUT_FORMAT: sbsenum.OutputFormatEnum.FORMAT_8BITS},
            aInheritance={sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.ABSOLUTE,
                          sbsenum.CompNodeParamEnum.OUTPUT_FORMAT: sbsenum.ParamInheritanceEnum.ABSOLUTE},
            aGUIPos=[0, 0, 0])
        theconnectedTransformNode = connectedGraph.createCompFilterNode(
            aFilter=sbsenum.FilterEnum.TRANSFORMATION,
            aParameters={
                sbsenum.CompNodeParamEnum.TILING_MODE: sbsenum.TilingEnum.NO_TILING},
            aInheritance={sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.PARENT,
                          sbsenum.CompNodeParamEnum.TILING_MODE: sbsenum.ParamInheritanceEnum.ABSOLUTE},
            aGUIPos=[144, 0, 0],
        )
        theconnectedBaseColorOutputNode = connectedGraph.createOutputNode(
            aIdentifier='BaseColor',
            aGUIPos=[288, 0, 0],
            aUsages={sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})
        # TODO: Warning regression with GUIName and Mutator, mutator remove GUIName
        # theconnectedBaseColorOutputNode.mGUIName = "Terminus"

        connectedGraph.connectNodes(aLeftNode=theconnectedBaseColorInputNode,
                                    aRightNode=theconnectedTransformNode)
        connectedGraph.connectNodes(aLeftNode=theconnectedTransformNode,
                                    aRightNode=theconnectedBaseColorOutputNode)
        connectedGraph.sortNodesAsDAG()
        connectedDoc.writeDoc()

        # Replace input of initial image and load output with the batchtools
        connectImageJob = batchtools.sbsmutator_edit(
            SBSBatchtoolsTest._getResourcePath("sbsmutator-edit-connect-image-init.sbs"),
            connect_image=u"{0}@path@{1}".format(u"iBaseColor", imagePath),
            output_name="sbsmutator-edit-connect-image-result",
            output_path=SBSBatchtoolsTest._getResourceDir(),
            quiet=False,
            verbose=True,
            stdout=subprocess.PIPE
        )
        connectImageJob.wait()
        self.assertEqual(connectImageJob.returncode, 0)
        self.assertEqual(_getStdout(connectImageJob), str(""))

        # Read the sbsmutator result and reorder nodes for comparison
        mutatorConnectedDoc = substance.SBSDocument(sbsContext,
                                                    SBSBatchtoolsTest._getResourcePath(
                                                        "sbsmutator-edit-connect-image-result.sbs"))
        mutatorConnectedDoc.parseDoc()
        mutatorConnectedGraph = mutatorConnectedDoc.getSBSGraph(aGraphIdentifier='gamma')
        mutatorConnectedGraph.sortNodesAsDAG()

        # Assert that the mutated sbs is the intended hand-made sbs.
        self.assertTrue(mutatorConnectedDoc.equals(connectedDoc))

    def test_cooker(self):
        # Find substance to cook
        pathSBS = SBSBatchtoolsTest._getDataPath("sample_value_node.sbs")
        self.assertIsNotNone(pathSBS)

        processSBSCooker = batchtools.sbscooker(
            pathSBS,
            includes=context.Context.getDefaultPackagePath(),
            enable_icons=True,
            output_path=SBSBatchtoolsTest._getResourceDir(),
            quiet=False,
            verbose=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        processSBSCooker.wait()
        out = _getStdout(processSBSCooker)
        for line in out.split('\n'):
            print('test_cooker [stdout]: {}'.format(line.encode('utf-8')))
            self.assertNotIn('[ERROR]', line)
        self.assertEqual(processSBSCooker.returncode, 0)

    @unittest.skipIf(platform.system() == 'Linux', 'sbsbaker cannot run on a machine without a graphic environment.')
    def test_sbsbaker_opt_types(self):
        some_opt_baker = [{
            "cmd": "color-from-mesh",
            "opt": [
                {"name": "color-source", "type": "integer", "values": [1, "1"], "wrong_values": ["1.0t"]},
                {"name": "output-size", "type": "integer,integer", "values": [[10, 10], ["10", "10"]],
                 "wrong_values": [["10.0t", "10.0t"]]}
            ]
        },
            {
                "cmd": "ambient-occlusion-from-mesh",
                "opt": [
                    {"name": "use-lowdef-as-highdef", "type": "bool", "values": [True, "true"],
                     "wrong_values": ["True", "0"]}
                ]
            }]
        getattr(batchtools, "__load_command_info")(batchtools.BatchToolsEnum.BAKER)
        for t in some_opt_baker:
            attr = getattr(batchtools, "__subcommand_info_for")  # it seems there is an interference with unittest and _
            subcommand_info = attr(batchtools.BatchToolsEnum.BAKER, t["cmd"])
            for opt in t["opt"]:
                attr = getattr(batchtools, "__option_info_for")  # it seems there is an interference with unittest and _
                info = attr(subcommand_info, opt["name"])
                typename = info["type"]
                self.assertEqual(typename, opt["type"])
                for value in opt["values"]:
                    attr = getattr(batchtools, "__check_option_value")
                    attr(opt["name"], typename, value)
                for wrong_value in opt["wrong_values"]:
                    attr = getattr(batchtools, "__check_option_value")
                    with self.assertRaises((TypeError, ValueError)) as e:
                        attr(opt["name"], typename, wrong_value)


    def test_sbsrender_render_animate(self):
        sbsarname = helpers.getAbsPathFromModule(testModule, './resources/noise.sbsar')
        outputs = helpers.getAbsPathFromModule(testModule, './resources/animate_outputs')
        cmds_list_path = helpers.getAbsPathFromModule(testModule, './resources/cmds_list.txt')
        try:
            os.mkdir(outputs)
        except:
            pass
        # Test 11 frames single threaded
        self.assertTrue(batchtools.sbsrender_render_animate(sbsarname,
                                                            start=0,
                                                            end=10,
                                                            fps=24,
                                                            output_path="{inputPath}/animate_outputs",
                                                            output_name="animate_frame_####",
                                                            input_graph_output="output",
                                                            animated_parameters=[
                                                                ("input", lambda frame, fps: frame / fps)]))
        # Test 51 frames multithreaded
        self.assertTrue(batchtools.sbsrender_render_animate(sbsarname,
                                                            start=0,
                                                            end=50,
                                                            fps=24,
                                                            output_path="{inputPath}/animate_outputs",
                                                            output_name="animate_frame_####",
                                                            input_graph_output="output",
                                                            animated_parameters=[
                                                                ("input", lambda frame, fps: frame / fps)],
                                                            multi_proc=0))
        # Test two frames single threaded with an incorrect engine to trigger an error
        self.assertFalse(batchtools.sbsrender_render_animate(sbsarname,
                                                             start=0,
                                                             end=1,
                                                             fps=24,
                                                             output_path="{inputPath}/animate_outputs",
                                                             output_name="animate_frame_####",
                                                             input_graph_output="output",
                                                             engine='banana',
                                                             animated_parameters=[
                                                                 ("input", lambda frame, fps: frame / fps)]))
        # Test 11 frames multithreaded with an incorrect engine to trigger an error
        self.assertFalse(batchtools.sbsrender_render_animate(sbsarname,
                                                             start=0,
                                                             end=10,
                                                             fps=24,
                                                             output_path="{inputPath}/animate_outputs",
                                                             output_name="animate_frame_####",
                                                             input_graph_output="output",
                                                             engine='banana',
                                                             animated_parameters=[
                                                                 ("input", lambda frame, fps: frame / fps)],
                                                             multi_proc=0))

        self.assertEqual(len(os.listdir(outputs)), 51)
        shutil.rmtree(outputs)
        with open(cmds_list_path, "wt") as cmds_list_stream:
            self.assertTrue(batchtools.sbsrender_render_animate(sbsarname,
                                                                start=0,
                                                                end=50,
                                                                fps=24,
                                                                output_path="{inputPath}/animate_outputs",
                                                                output_name="animate_frame_####",
                                                                input_graph_output="output",
                                                                animated_parameters=(
                                                                "input", lambda frame, fps: frame / fps),
                                                                cmds_output_stream=cmds_list_stream))

        with open(cmds_list_path, 'r') as f:
            self.assertEqual(len(f.readlines()), 51)
        os.remove(cmds_list_path)

    def test_sbsbaker_info_handlers(self):
        # with fbx
        mesh_fbx = helpers.getAbsPathFromModule(testModule, './resources/test_info.fbx')
        out = batchtools.sbsbaker_info(mesh_fbx, output_handler=True).get_results()
        print(out)
        self.assertEqual(out[0].label, "m41_low")
        self.assertEqual(out[0]._enabled, True)
        self.assertEqual(out[0].meshes[0].vertices_number, 4998)
        self.assertEqual(out[0].meshes[0].uvs[0].is_in_unit_square, False)

        # with obj
        mesh_obj = helpers.getAbsPathFromModule(testModule, './resources/test_info.obj')
        out = batchtools.sbsbaker_info(mesh_obj, output_handler=True).get_results()
        self.assertEqual(out[0].label, "m41_low_Untitled")
        self.assertEqual(out[0]._enabled, True)
        self.assertEqual(out[0].meshes[0].vertices_number, 4967)
        self.assertEqual(out[0].meshes[0].uvs[0].is_in_unit_square, False)

    def test_sbsrender_render_handlers(self):
        sbsar = helpers.getAbsPathFromModule(testModule, './resources/output.sbsar')
        out = batchtools.sbsrender_render(sbsar, output_path=helpers.getAbsPathFromModule(testModule, './resources'),
                                          output_handler=True).get_results()
        self.assertEqual(out[0].identifier, "New_Graph")
        self.assertEqual(out[0].outputs[0].identifier, "output")
        self.assertEqual(out[0].outputs[0].label, "output")
        self.assertEqual(out[0].outputs[0].uid, 841621995)
        self.assertEqual(out[0].outputs[0].usages, ["diffuse"])
        self.assertEqual(out[0].outputs[0].value.replace("\\", "/"), helpers.getAbsPathFromModule(testModule, './resources/output_New_Graph_output.png').replace("\\", "/"))
        self.assertEqual(out[0].outputs[1].identifier, "output_value")
        self.assertEqual(out[0].outputs[1].label, "output_value")
        self.assertEqual(out[0].outputs[1].uid, 841623423)
        self.assertEqual(out[0].outputs[1].usages, [])
        self.assertEqual(out[0].outputs[1].value, 0.4599749743938446)
        os.remove(helpers.getAbsPathFromModule(testModule, './resources/output_New_Graph_output.png'))

    def test_output_handlers_dump(self):
        # sbsrender
        test_file = helpers.getAbsPathFromModule(testModule, './resources/dump.json')
        sbsar = helpers.getAbsPathFromModule(testModule, './resources/output.sbsar')
        out = batchtools.sbsrender_render(sbsar, output_path=helpers.getAbsPathFromModule(testModule, './resources'),
                                          output_handler=True)
        with open(test_file, 'w') as f:
            out.dump(f)
        os.remove(helpers.getAbsPathFromModule(testModule, './resources/output_New_Graph_output.png'))
        os.remove(helpers.getAbsPathFromModule(testModule, './resources/dump.json'))

        # baker info
        test_file = helpers.getAbsPathFromModule(testModule, './resources/dump.txt')
        mesh_fbx = helpers.getAbsPathFromModule(testModule, './resources/test_info.fbx')
        out = batchtools.sbsbaker_info(mesh_fbx, output_handler=True)
        with open(test_file, 'w') as f:
            out.dump(f)
        os.remove(helpers.getAbsPathFromModule(testModule, './resources/dump.txt'))

    def test_raise_outputhandler_not_implemented(self):
        with self.assertRaises(TypeError):
            out = batchtools.sbsupdater(output_handler=True)
