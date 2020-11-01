# coding: utf-8
import unittest
import logging
import platform

log = logging.getLogger(__name__)

from pysbs.sbsenum import ParamTypeEnum, UVTileFormat
from pysbs.api_helpers import formatValueForTypeStr, getInputsInVisibleIfExpression, formatUVTileToSBSFormat, \
    convertUVTileToFormat, getRelativeObjectPathFromFilePath, convertUVTileToUdimPattern


class SBSGeneratorTests(unittest.TestCase):

    def test_FormatValue(self):
        """
        This test checks the correct formatting of a string for .sbs format according to data type.
        """
        log.info("Test API Helpers: Format Value")
        # Check behavior with valid inputs
        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.BOOLEAN), '1')
        self.assertEqual(formatValueForTypeStr('0',             ParamTypeEnum.BOOLEAN), '0')
        self.assertEqual(formatValueForTypeStr(1,               ParamTypeEnum.BOOLEAN), '1')
        self.assertEqual(formatValueForTypeStr(0,               ParamTypeEnum.BOOLEAN), '0')
        self.assertEqual(formatValueForTypeStr(12.451,          ParamTypeEnum.BOOLEAN), '1')
        self.assertEqual(formatValueForTypeStr(-0.45,           ParamTypeEnum.BOOLEAN), '0')
        self.assertEqual(formatValueForTypeStr(True,            ParamTypeEnum.BOOLEAN), '1')
        self.assertEqual(formatValueForTypeStr(False,           ParamTypeEnum.BOOLEAN), '0')
        self.assertEqual(formatValueForTypeStr('True',          ParamTypeEnum.BOOLEAN), '1')
        self.assertEqual(formatValueForTypeStr('False',         ParamTypeEnum.BOOLEAN), '0')

        self.assertEqual(formatValueForTypeStr('.1',            ParamTypeEnum.FLOAT1), '0.1')
        self.assertEqual(formatValueForTypeStr('-0',            ParamTypeEnum.FLOAT1), '0')
        self.assertEqual(formatValueForTypeStr('0.01',          ParamTypeEnum.FLOAT1), '0.01')
        self.assertEqual(formatValueForTypeStr('0.010',         ParamTypeEnum.FLOAT1), '0.01')
        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('1.0',           ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('1.00',          ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('-10',           ParamTypeEnum.FLOAT1), '-10')
        self.assertEqual(formatValueForTypeStr('-1.2546',       ParamTypeEnum.FLOAT1), '-1.2546')
        self.assertEqual(formatValueForTypeStr(1,               ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr([1],             ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr(-10,             ParamTypeEnum.FLOAT1), '-10')
        self.assertEqual(formatValueForTypeStr(-1.2546,         ParamTypeEnum.FLOAT1), '-1.2546')
        self.assertEqual(formatValueForTypeStr([1,2,3,4],       ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('[1,2,3,4]',     ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('1,2,3,4',       ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('1 2 3 4',       ParamTypeEnum.FLOAT1), '1')
        self.assertEqual(formatValueForTypeStr('',              ParamTypeEnum.FLOAT1), '0')

        self.assertEqual(formatValueForTypeStr('.1',            ParamTypeEnum.FLOAT2), '0.1 0')
        self.assertEqual(formatValueForTypeStr('.1 .3',         ParamTypeEnum.FLOAT2), '0.1 0.3')
        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.FLOAT2), '1 0')
        self.assertEqual(formatValueForTypeStr('1 1',           ParamTypeEnum.FLOAT2), '1 1')
        self.assertEqual(formatValueForTypeStr('1.0 3.5',       ParamTypeEnum.FLOAT2), '1 3.5')
        self.assertEqual(formatValueForTypeStr('-1.2 -12',      ParamTypeEnum.FLOAT2), '-1.2 -12')
        self.assertEqual(formatValueForTypeStr([1.0,2],         ParamTypeEnum.FLOAT2), '1 2')
        self.assertEqual(formatValueForTypeStr([1,2,3,4],       ParamTypeEnum.FLOAT2), '1 2')
        self.assertEqual(formatValueForTypeStr('[1,2,3,4]',     ParamTypeEnum.FLOAT2), '1 2')
        self.assertEqual(formatValueForTypeStr('1,2,3,4',       ParamTypeEnum.FLOAT2), '1 2')
        self.assertEqual(formatValueForTypeStr('1 2 3 4',       ParamTypeEnum.FLOAT2), '1 2')

        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.FLOAT3), '1 0 0')
        self.assertEqual(formatValueForTypeStr('1 1',           ParamTypeEnum.FLOAT3), '1 1 0')
        self.assertEqual(formatValueForTypeStr('1 1 -1.5',      ParamTypeEnum.FLOAT3), '1 1 -1.5')
        self.assertEqual(formatValueForTypeStr([1.0,2],         ParamTypeEnum.FLOAT3), '1 2 0')
        self.assertEqual(formatValueForTypeStr([1,2,3,4],       ParamTypeEnum.FLOAT3), '1 2 3')

        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.FLOAT4), '1 0 0 0')
        self.assertEqual(formatValueForTypeStr('1 1 -1.5 .10',  ParamTypeEnum.FLOAT4), '1 1 -1.5 0.1')
        self.assertEqual(formatValueForTypeStr([1.0,2],         ParamTypeEnum.FLOAT4), '1 2 0 0')
        self.assertEqual(formatValueForTypeStr('[1,2,3,4]',     ParamTypeEnum.FLOAT4), '1 2 3 4')
        self.assertEqual(formatValueForTypeStr('1 2 3 4 5',     ParamTypeEnum.FLOAT4), '1 2 3 4')

        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.FLOAT_VARIANT), '1 1 1 1')
        self.assertEqual(formatValueForTypeStr('1 1 -1.5 .10',  ParamTypeEnum.FLOAT_VARIANT), '1 1 -1.5 0.1')
        self.assertEqual(formatValueForTypeStr([1.0,2],         ParamTypeEnum.FLOAT_VARIANT), '1 2 2 2')
        self.assertEqual(formatValueForTypeStr([1,2,3,4],       ParamTypeEnum.FLOAT_VARIANT), '1 2 3 4')
        self.assertEqual(formatValueForTypeStr('1  2,3;4,5',     ParamTypeEnum.FLOAT_VARIANT), '1 2 3 4')

        self.assertEqual(formatValueForTypeStr('.1',            ParamTypeEnum.INTEGER1), '0')
        self.assertEqual(formatValueForTypeStr('-0.01',         ParamTypeEnum.INTEGER1), '0')
        self.assertEqual(formatValueForTypeStr('0.01',          ParamTypeEnum.INTEGER1), '0')
        self.assertEqual(formatValueForTypeStr('0.010',         ParamTypeEnum.INTEGER1), '0')
        self.assertEqual(formatValueForTypeStr('1',             ParamTypeEnum.INTEGER1), '1')
        self.assertEqual(formatValueForTypeStr('1.0',           ParamTypeEnum.INTEGER1), '1')
        self.assertEqual(formatValueForTypeStr('1.00',          ParamTypeEnum.INTEGER1), '1')
        self.assertEqual(formatValueForTypeStr('-10',           ParamTypeEnum.INTEGER1), '-10')
        self.assertEqual(formatValueForTypeStr('-1.2546',       ParamTypeEnum.INTEGER1), '-1')
        self.assertEqual(formatValueForTypeStr(.1,              ParamTypeEnum.INTEGER1), '0')
        self.assertEqual(formatValueForTypeStr(-10,             ParamTypeEnum.INTEGER1), '-10')
        self.assertEqual(formatValueForTypeStr(-1.2546,         ParamTypeEnum.INTEGER1), '-1')
        self.assertEqual(formatValueForTypeStr([1,2,3,4],       ParamTypeEnum.INTEGER1), '1')

        self.assertEqual(formatValueForTypeStr('.1',            ParamTypeEnum.INTEGER2), '0 0')
        self.assertEqual(formatValueForTypeStr('1 1',           ParamTypeEnum.INTEGER2), '1 1')
        self.assertEqual(formatValueForTypeStr('-1.2 -12',      ParamTypeEnum.INTEGER2), '-1 -12')
        self.assertEqual(formatValueForTypeStr('[1,2,3,4]',     ParamTypeEnum.INTEGER2), '1 2')

        self.assertEqual(formatValueForTypeStr('1 1',           ParamTypeEnum.INTEGER3), '1 1 0')
        self.assertEqual(formatValueForTypeStr([1.0,2],         ParamTypeEnum.INTEGER3), '1 2 0')
        self.assertEqual(formatValueForTypeStr('1,2.0,3.1,4.12',ParamTypeEnum.INTEGER3), '1 2 3')

        self.assertEqual(formatValueForTypeStr('100.0120',      ParamTypeEnum.INTEGER4), '100 0 0 0')
        self.assertEqual(formatValueForTypeStr('1.0 -0.2 3 4.', ParamTypeEnum.INTEGER4), '1 0 3 4')

        self.assertEqual(formatValueForTypeStr('1.0 -0.2 3 4.', ParamTypeEnum.STRING), '1.0 -0.2 3 4.')
        self.assertEqual(formatValueForTypeStr('Valid',         ParamTypeEnum.STRING), 'Valid')
        self.assertEqual(formatValueForTypeStr('myPath://GreatPath.sbs', ParamTypeEnum.PATH), 'myPath://GreatPath.sbs')

        # Check behavior with invalid inputs
        self.assertEqual(formatValueForTypeStr(None,    ParamTypeEnum.BOOLEAN), '0')
        self.assertEqual(formatValueForTypeStr(None,    ParamTypeEnum.FLOAT1), '0')
        self.assertEqual(formatValueForTypeStr(None,    ParamTypeEnum.STRING), '')

        with self.assertRaises(ValueError): formatValueForTypeStr('Invalid',    ParamTypeEnum.BOOLEAN)
        with self.assertRaises(ValueError): formatValueForTypeStr('Invalid',    ParamTypeEnum.FLOAT1)
        with self.assertRaises(ValueError): formatValueForTypeStr('[foo, bar]', ParamTypeEnum.FLOAT2)

    def test_VisibleIfExpr(self):
        """
        This test checks the input detection in a visible if expression
        """
        self.assertEqual(getInputsInVisibleIfExpression('input["ShowInputImage"]'), ['ShowInputImage'])
        self.assertEqual(getInputsInVisibleIfExpression('input["ShowInputImage"]==true'), ['ShowInputImage'])
        self.assertEqual(getInputsInVisibleIfExpression("input['ShowInputImage']==true"), [])
        self.assertEqual(getInputsInVisibleIfExpression("input[ShowInputImage]==true"), [])
        self.assertEqual(getInputsInVisibleIfExpression('output["ShowInputImage"]'), [])
        self.assertEqual(getInputsInVisibleIfExpression('input[""]'), [])
        self.assertEqual(getInputsInVisibleIfExpression('input["ShowInputImage"]==true && input["ShowInput2"] == false'),
                         ['ShowInputImage', 'ShowInput2'])

    def test_FormatUVTile(self):
        """
        This test checks the conversion from different uv tiles format to .sbs format
        """
        self.assertEqual(formatUVTileToSBSFormat('all'), 'all')
        self.assertEqual(formatUVTileToSBSFormat((0,2)), '0x2')
        self.assertEqual(formatUVTileToSBSFormat([0,2]), '0x2')
        self.assertEqual(formatUVTileToSBSFormat('0x2'), '0x2')
        self.assertEqual(formatUVTileToSBSFormat('u0_v2'), '0x2')
        self.assertEqual(formatUVTileToSBSFormat('1021'), '0x2')
        self.assertEqual(formatUVTileToSBSFormat('1001'), '0x0')
        self.assertEqual(formatUVTileToSBSFormat('1002'), '1x0')
        self.assertEqual(formatUVTileToSBSFormat('1011'), '0x1')
        self.assertEqual(formatUVTileToSBSFormat('1027'), '6x2')
        self.assertEqual(formatUVTileToSBSFormat('2011'), '0x101')

        self.assertEqual(convertUVTileToFormat('all', UVTileFormat.UxV),        'all')
        self.assertEqual(convertUVTileToFormat('all', UVTileFormat.uU_vV),      'all')
        self.assertEqual(convertUVTileToFormat('all', UVTileFormat.UDIM),       'all')
        self.assertEqual(convertUVTileToFormat('all', UVTileFormat.UV_LIST),    'all')
        self.assertEqual(convertUVTileToFormat('all', UVTileFormat.UV_TUPLE),   'all')
        self.assertEqual(convertUVTileToFormat('0x2', UVTileFormat.uU_vV),      'u0_v2')
        self.assertEqual(convertUVTileToFormat('0x2', UVTileFormat.UV_LIST),    [0,2])
        self.assertEqual(convertUVTileToFormat('0x2', UVTileFormat.UV_TUPLE),   (0,2))
        self.assertEqual(convertUVTileToFormat('0x2', UVTileFormat.UxV),        '0x2')
        self.assertEqual(convertUVTileToFormat('0x2', UVTileFormat.UDIM),       '1021')
        self.assertEqual(convertUVTileToFormat('1x0', UVTileFormat.UDIM),       '1002')
        self.assertEqual(convertUVTileToFormat('6x2', UVTileFormat.UDIM),       '1027')

    def test_getRelativeObjectPathFromFilePath(self):
        """
        Test if differents path forms is correctly handle for dependencies.
        :return:
        """
        if platform.system() == "Windows":
            aTestPaths = {"a:/test/path/foo.sbs": ("a:/test/path/foo.sbs", "pkg:///foo"),
                          "a:/test/path/foo.sbs/my_graph": ("a:/test/path/foo.sbs", "pkg:///my_graph"),
                          "a:/test/path/foo.sbs/a_grp/my_graph": ("a:/test/path/foo.sbs", "pkg:///a_grp/my_graph"),
                          "file:///a:/test/path/foo.sbs": ("a:/test/path/foo.sbs", "pkg:///foo"),
                          "file:///a:/test/path/foo.sbs/my_graph": ("a:/test/path/foo.sbs", "pkg:///my_graph"),
                          "file:///a:/test/path/foo.sbs/a_grp/my_graph": ("a:/test/path/foo.sbs", "pkg:///a_grp/my_graph")
                          }
        else:
            aTestPaths = {"/a/test/path/foo.sbs": ("/a/test/path/foo.sbs", "pkg:///foo"),
                          "/a/test/path/foo.sbs/my_graph": ("/a/test/path/foo.sbs", "pkg:///my_graph"),
                          "/a/test/path/foo.sbs/a_grp/my_graph": ("/a/test/path/foo.sbs", "pkg:///a_grp/my_graph"),
                          "file:///a/test/path/foo.sbs": ("/a/test/path/foo.sbs", "pkg:///foo"),
                          "file:///a/test/path/foo.sbs/my_graph": ("/a/test/path/foo.sbs", "pkg:///my_graph"),
                          "file:///a/test/path/foo.sbs/a_grp/my_graph": ("/a/test/path/foo.sbs", "pkg:///a_grp/my_graph")
                          }
        for aPath, aResult in aTestPaths.items():
            aRet = getRelativeObjectPathFromFilePath(aPath)
            assert aResult == aRet

    def test_convertUdimToUdimPattern(self):
        somePath = ["/foo/bar/fou_1002_bar.png",
                    "/foo/bar/fou_bar.1002.png",
                    "C:\\foo\\bar\\fou_1002_bar.png",
                    "C:\\foo\\bar\\fou_bar.1002.png",
                    "/foo/bar/fou_u1v2_bar.png",
                    "C:\\foo\\bar\\fou_u1v2_bar.png"]
        someResultPath = ["/foo/bar/fou_$(udim)_bar.png",
                    "/foo/bar/fou_bar.$(udim).png",
                    "C:\\foo\\bar\\fou_$(udim)_bar.png",
                    "C:\\foo\\bar\\fou_bar.$(udim).png",
                    "/foo/bar/fou_$(u)$(v)_bar.png",
                    "C:\\foo\\bar\\fou_$(u)$(v)_bar.png"]
        for i, path in enumerate(somePath):
            res = convertUVTileToUdimPattern(path)
            self.assertEqual(res, someResultPath[i])


if __name__ == '__main__':
    unittest.main()
