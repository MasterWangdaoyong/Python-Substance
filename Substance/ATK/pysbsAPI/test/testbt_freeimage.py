# coding: utf-8
import unittest
import sys
import os
from pysbs import python_helpers as helpers
from pysbs import context
from pysbs import freeimagebindings as fi
from pysbs import sbsenum
from pysbs import sbsgenerator


testModule = sys.modules[__name__]

class FreeImageTest(unittest.TestCase):
    _testDir = helpers.getAbsPathFromModule(testModule, './resources/')
    _testFiles = [('test_0.jpg', (5, 7, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_1.tif', (7, 7, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_2.tif', (7, 6, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_4.png', (7, 7, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_5.jpg', (7, 7, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_6.tif', (6, 6, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_7.tif', (6, 6, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_8.jpg', (4, 6, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_9.tif', (5, 7, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_10.png', (6, 7, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_11.png', (7, 7, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_16BITS)),
                  ('test_12.jpg', (6, 5, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_13.png', (6, 7, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_8BITS)),
                  ('test_14.tif', (7, 7, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_16BITS)),
                  ('test_15.tif', (8, 8, sbsenum.ColorModeEnum.GRAYSCALE, sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT)),
                  ('test_16.tif', (8, 8, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT)),
                  ]
    def test_freeimage(self):
        """
        This test checks the global usage of the batchtools commands
        """
        # Skip testing on platforms where no freeimage dll is found
        sbsContext = context.Context()
        if helpers.isPython32Bit():
            self.assertFalse(fi.HasFreeImage(sbsContext))
        else:
            self.assertTrue(fi.HasFreeImage(sbsContext))
            with self.assertRaises(IOError):
                # Make sure the api throws exceptions if incorrect paths are provided
                fi.GetImageInformation('/This/is/a/non-existent/path', sbsContext)
            with self.assertRaises(IOError):
                # Make sure the api throws exceptions if loading non-images
                fi.GetImageInformation(os.path.join(self._testDir, 'refCleaner.sbs'), sbsContext)
            for f, expected in self._testFiles:
                self.assertEqual(fi.GetImageInformation(os.path.join(self._testDir, f), sbsContext), expected)

            # Test actually creating bitmap nodes and make sure the sizes are detected correctly
            destPath = helpers.getAbsPathFromModule(testModule, './resources/testBitmaps.sbs')

            sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath, 'BitmapTestGraph')
            aGraph = sbsDoc.getSBSGraph('BitmapTestGraph')

            for f, expected in self._testFiles:
                image_node = aGraph.createBitmapNode(aSBSDocument=sbsDoc,
                                                     aResourcePath=os.path.join(self._testDir, f))
                size = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE)
                color_mode = image_node.getParameterValue(sbsenum.CompNodeParamEnum.COLOR_MODE)
                out_format = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
                self.assertEqual(size, u'%d %d' % (expected[0], expected[1]))
                self.assertEqual(int(color_mode), expected[2])
                self.assertEqual(int(out_format), expected[3])

            # Make sure manually provided parameters are prioritized over autodetection
            f, expected = self._testFiles[0]
            image_node = aGraph.createBitmapNode(aSBSDocument=sbsDoc,
                                                 aResourcePath=os.path.join(self._testDir, f),
                                                 aParameters={sbsenum.CompNodeParamEnum.OUTPUT_SIZE : [10, 10]})
            size = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE)
            color_mode = image_node.getParameterValue(sbsenum.CompNodeParamEnum.COLOR_MODE)
            img_format = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
            self.assertEqual(size, u'%d %d' % (10, 10))
            self.assertEqual(int(color_mode), expected[2])
            self.assertEqual(int(img_format), expected[3])

            image_node = aGraph.createBitmapNode(aSBSDocument=sbsDoc,
                                                 aResourcePath=os.path.join(self._testDir, f),
                                                 aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE : sbsenum.ColorModeEnum.GRAYSCALE})
            size = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE)
            color_mode = image_node.getParameterValue(sbsenum.CompNodeParamEnum.COLOR_MODE)
            img_format = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
            self.assertEqual(size, u'%d %d' % (expected[0], expected[1]))
            self.assertEqual(int(color_mode), sbsenum.ColorModeEnum.GRAYSCALE)
            self.assertEqual(int(img_format), expected[3])

            image_node = aGraph.createBitmapNode(aSBSDocument=sbsDoc,
                                                 aResourcePath=os.path.join(self._testDir, f),
                                                 aParameters={sbsenum.CompNodeParamEnum.OUTPUT_FORMAT : sbsenum.OutputFormatEnum.FORMAT_16BITS_FLOAT})
            size = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE)
            color_mode = image_node.getParameterValue(sbsenum.CompNodeParamEnum.COLOR_MODE)
            img_format = image_node.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
            self.assertEqual(size, u'%d %d' % (expected[0], expected[1]))
            self.assertEqual(int(color_mode), expected[2])
            self.assertEqual(int(img_format), sbsenum.OutputFormatEnum.FORMAT_16BITS_FLOAT)

            sbsDoc.writeDoc()
            os.remove(sbsDoc.mFileAbsPath)
