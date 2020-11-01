import unittest
import logging
import random
import sys
log = logging.getLogger(__name__)


from pysbs import sbsgenerator
from pysbs import sbsenum
from pysbs import context
from pysbs.api_exceptions import SBSImpossibleActionError, SBSTypeError, SBSMissingDependencyError
from pysbs.python_helpers import getAbsPathFromModule
from pysbs import autograph as ag
import functools

testModule = sys.modules[__name__]


class sbsmathTest(unittest.TestCase):
    @staticmethod
    def createPPTestDoc(filePath):
        sbs_context = context.Context()
        # Create our target document
        doc = sbsgenerator.createSBSDocument(sbs_context,
                                             aFileAbsPath=filePath,
                                             aGraphIdentifier='TestMath')
        graph = doc.getSBSGraph(aGraphIdentifier='TestMath')
        # Create pixelprocessor
        pp_node = graph.createCompFilterNode(sbsenum.FilterEnum.PIXEL_PROCESSOR)
        uniform = graph.createCompFilterNode(sbsenum.FilterEnum.UNIFORM)

        return doc, pp_node, graph, uniform

    @staticmethod
    def createVPTestDoc(filePath):
        sbs_context = context.Context()
        # Create our target document
        doc = sbsgenerator.createSBSDocument(sbs_context,
                                             aFileAbsPath=filePath,
                                             aGraphIdentifier='TestMath')
        graph = doc.getSBSGraph(aGraphIdentifier='TestMath')
        # Create pixelprocessor
        vp_node = graph.createCompFilterNode(sbsenum.FilterEnum.VALUE_PROCESSOR)
        uniform = graph.createCompFilterNode(sbsenum.FilterEnum.UNIFORM)

        return doc, vp_node, graph, uniform

    def test_Node(self):
        def f1(fn):
            a = fn.input_parameter('a', widget_type=sbsenum.WidgetEnum.COLOR_FLOAT3)
            b = fn.input_parameter('b', widget_type=sbsenum.WidgetEnum.COLOR_FLOAT1)
            c = a * b
            return c

        def test_fun(fn):
            """
            Computes ambient lighting
            :param fn: The function context to create the function in
            :type fn: FunctionContext
            """
            fc = [fn.constant(1.0),
                  fn.constant([1.0, 2.0]),
                  fn.constant([1.0, 2.0, 3.0]),
                  fn.constant([1.0, 2.0, 3.0, 4.0])]
            ic = [fn.constant(1),
                  fn.constant([1, 2]),
                  fn.constant([1, 2, 3]),
                  fn.constant([1, 2, 3, 4])]
            bc = [fn.constant(False),
                  fn.constant(True)]
            fic = fc + ic
            print('Testing operations for int and floats')
            for i, f in enumerate(fic):
                binary_operations = [f.__add__,
                                     f.__sub__,
                                     f.__div__,
                                     f.__radd__,
                                     f.__mod__,
                                     f.__truediv__,
                                     functools.partial(fn.max_of, f),
                                     functools.partial(fn.min_of, f)
                                     ]
                for o in binary_operations:
                    res = o(f)
                    self.assertEqual(res.__class__, f.__class__)
                    with self.assertRaises(SBSTypeError):
                        o(fic[(i + 1) % len(fic)])
                unary_operations = [f.__neg__,
                                    functools.partial(fn.abs_of, f)
                                    ]
                for o in unary_operations:
                    res = o()
                    self.assertEqual(res.__class__, f.__class__)
            print('Testing float only operations')
            for i, f in enumerate(fc):
                unary_operations = [
                    fn.sqrt,
                    fn.log,
                    fn.exp,
                    fn.log2,
                    fn.pow2,
                    fn.floor,
                    fn.ceil,
                    fn.cos,
                    fn.sin,
                    fn.tan
                ]
                for o in unary_operations:
                    res = o(f)
                    self.assertEqual(res.__class__, f.__class__)
            print('Scalar multiplication')
            for i, f in enumerate(fc):
                res = fc[0] * f
                self.assertEqual(res.__class__, f.__class__)
                res = f * fc[0]
                self.assertEqual(res.__class__, f.__class__)

            print('Testing dot product')
            for i, f in enumerate(fc):
                if i == 0:
                    with self.assertRaises(SBSTypeError):
                        fn.dot(f, f)
                else:
                    res = fn.dot(f, f)
                    self.assertEqual(ag.Float1, res.__class__)
            print('Cartesian')
            for i, f in enumerate(fc):
                if i == 0:
                    res = fn.cartesian(f, f)
                    self.assertEqual(ag.Float2, res.__class__)
                else:
                    with self.assertRaises(SBSTypeError):
                        fn.cartesian(f, f)
            print('Atan2')
            for i, f in enumerate(fc):
                if i == 1:
                    res = fn.atan2(f)
                    self.assertEqual(ag.Float1, res.__class__)
                else:
                    with self.assertRaises(SBSTypeError):
                        fn.atan2(f)
            print('Lerp')
            for i, f in enumerate(fc):
                res = fn.lerp(f, f, fc[0])
                self.assertEqual(f.__class__, res.__class__)
                with self.assertRaises(SBSTypeError):
                    fn.lerp(f, f, fc[1])

            print('Clamp')
            for i, f in enumerate(fc):
                res = fn.clamp(f, f, f)
                self.assertEqual(f.__class__, res.__class__)
                with self.assertRaises(SBSTypeError):
                    fn.clamp(f, f, fc[(i + 1) % len(fc)])

            print('Samplers')
            faulty_filter = 93
            for i, f in enumerate(fc):
                for filter_mode in [sbsenum.FilteringEnum.NEAREST, sbsenum.FilteringEnum.NEAREST, faulty_filter]:
                    if i == 1 and filter_mode != faulty_filter:
                        res = fn.create_color_sampler(f, 0, filter_mode)
                        self.assertEqual(ag.Float4, res.__class__)
                        res = fn.create_gray_sampler(f, 0, filter_mode)
                        self.assertEqual(ag.Float1, res.__class__)
                    else:
                        with self.assertRaises(SBSTypeError):
                            fn.create_color_sampler(f, 0, filter_mode)
                        with self.assertRaises(SBSTypeError):
                            fn.create_gray_sampler(f, 0, filter_mode)

            print('Indexing')
            for i, f in enumerate(fc):
                for j in range(0, 5):
                    if j <= i:
                        res = f[j]
                        self.assertEqual(res.__class__, ag.Float1)
                    else:
                        with self.assertRaises(SBSTypeError):
                            f[j]
            for i, f in enumerate(ic):
                for j in range(-5, 5):
                    if 0 <= j <= i:
                        res = f[j]
                        self.assertEqual(res.__class__, ag.Int1)
                    else:
                        with self.assertRaises(SBSTypeError):
                            f[j]

            print('Swizzlers')
            swizzlers = [fn.swizzle_float1,
                         fn.swizzle_float2,
                         fn.swizzle_float3,
                         fn.swizzle_float4,
                         fn.swizzle_int1,
                         fn.swizzle_int2,
                         fn.swizzle_int3,
                         fn.swizzle_int4]

            for i, swizzler in enumerate(swizzlers):
                for j, c in enumerate(fic):
                    jj = j % 4
                    if not j == i:
                        with self.assertRaises(SBSTypeError):
                            swizzler(c, [0] * (jj + 1))
                    else:
                        res = swizzler(c, [0] * (jj + 1))
                        with self.assertRaises(SBSTypeError):
                            swizzler(c, [5] * (jj + 1))
            print('Key Swizzlers')
            valid_keys = [('x', 'r'), ('y', 'g'), ('z', 'b'), ('w', 'a')]
            for i, v in enumerate(fc):
                ii = i + 1
                for j in range(1, 5):
                    if ii >= j:
                       key = ''.join([random.choice(random.choice(valid_keys[0:ii])) for _ in range(0, ii)])
                       a = v[key]
                    else:
                        with self.assertRaises(SBSTypeError):
                            key = ''.join([random.choice(random.choice(valid_keys[ii:])) for _ in range(0, ii)])
                            a = v[key]

            print('Expansion')
            expanders_f = [fn.expand_to_float2,
                           fn.expand_to_float3,
                           fn.expand_to_float4]
            expanders_i = [fn.expand_to_int2,
                           fn.expand_to_int3,
                           fn.expand_to_int4]

            for i, expander in enumerate(expanders_f):
                # Make sure correct arguments don't fail
                e = expander(fc[0], fc[i])
                self.assertIsInstance(e, fc[i + 1].__class__)

                # Make sure too wide vectors fails
                with self.assertRaises(SBSTypeError):
                    expander(fc[0], fc[i+1])

                # Make sure mixing float and int fails
                with self.assertRaises(SBSTypeError):
                    expander(fc[0], ic[i])

            for i, expander in enumerate(expanders_i):
                # Make sure correct arguments don't fail
                e = expander(ic[0], ic[i])
                self.assertIsInstance(e, ic[i + 1].__class__)

                # Make sure too wide vectors fails
                with self.assertRaises(SBSTypeError):
                    expander(ic[0], ic[i+1])

                # Make sure mixing float and int fails
                with self.assertRaises(SBSTypeError):
                    expander(ic[0], fc[i])

            for i, a in enumerate(fc):
                for j, b in enumerate(fc):
                    expected_vector_size = i + j + 2
                    if expected_vector_size > 4:
                        with self.assertRaises(SBSTypeError):
                            fn.expand(a, b)
                    else:
                        e = fn.expand(a, b)
                        self.assertIsInstance(e, fc[expected_vector_size - 1].__class__)

            # Auto const
            print('Auto Const')
            for i in range(0,4):
                fv = 1.0 if i == 0 else [1.0] * (i + 1)
                iv = 1 if i == 0 else [1] * (i + 1)
                fc[i] + fv
                fv + fc[i]
                ic[i] + iv
                iv + ic[i]

            print('Conditionals')
            for i, f in enumerate(fc):
                a = fn.if_else(bc[0], f, f)
                self.assertIsInstance(a, f.__class__)
                with self.assertRaises(SBSTypeError):
                    fn.if_else(bc[0], f, fc[(i + 1) % len(fc)])

            for i, f in enumerate(ic):
                a = fn.if_else(bc[0], f, f)
                self.assertIsInstance(a, f.__class__)
                with self.assertRaises(SBSTypeError):
                    fn.if_else(bc[0], f, ic[(i + 1) % len(ic)])

            print('Rand')
            a = fn.rand(fc[0])
            self.assertIsInstance(a, fc[0].__class__)
            with self.assertRaises(SBSTypeError):
                fn.rand(fc[1])


            f1 = fn.import_local_function('f1')
            with self.assertRaises(SBSImpossibleActionError):
                f2 = fn.import_local_function('f2')
                f2(fc[2], fc[0])
            res = f1(fc[2], fc[0])
            self.assertEqual(res.__class__, ag.Float3)
            with self.assertRaises(SBSTypeError):
                f1(fc[0], fc[0])
            with self.assertRaises(SBSTypeError):
                f1(fc[2])
            with self.assertRaises(SBSTypeError):
                f1(fc[2], fc[0], fc[3])

            fn_pi = fn.import_external_function('sbs://functions.sbs/Functions/Math/Pi')
            #res = fn_pi()
            #self.assertEqual(res.__class__, ag.Float1)

            with self.assertRaises(SBSMissingDependencyError):
                fn_pi2 = fn.import_external_function('sbs://functions.sbs/Functions/Math/Pidasdsa')
                fn_pi2()
            return fn.generate(res)

        # Want to make sure all random numbers are deterministic in the test
        random.seed(0xc0ff3)
        # Make sure pixel processor generates properly
        file_path = getAbsPathFromModule(testModule, './resources/ppDummy.sbs')
        doc, pp_node, graph, uniform = sbsmathTest.createPPTestDoc(file_path)
        pp_fun = ag.generate_function(f1, doc, name='f1')
        pp_fun = ag.generate_function(test_fun, doc, name='test', layout_nodes=True, remove_unused_nodes=False)
        pp_fun = ag.generate_function(test_fun, doc, fn_node=pp_node.getPixProcFunction())
        dynamic_value = uniform.setDynamicParameter('outputcolor', aRelativeTo=sbsenum.ParamInheritanceEnum.INPUT)
        pp_fun = ag.generate_function(test_fun, doc, fn_node=dynamic_value, layout_nodes=True,
                                      remove_unused_nodes=False)
        #doc.writeDoc()

        # Make sure value processor generates properly
        file_path = getAbsPathFromModule(testModule, './resources/vpDummy.sbs')
        doc, vp_node, graph, uniform = sbsmathTest.createVPTestDoc(file_path)
        vp_fun = ag.generate_function(f1, doc, name='f1')
        vp_fun = ag.generate_function(test_fun, doc, name='test', layout_nodes=True, remove_unused_nodes=False)
        vp_fun = ag.generate_function(test_fun, doc, fn_node=vp_node.getValProcFunction())
        dynamic_value = uniform.setDynamicParameter('outputcolor', aRelativeTo=sbsenum.ParamInheritanceEnum.INPUT)
        vp_fun = ag.generate_function(test_fun, doc, fn_node=dynamic_value, layout_nodes=True,
                                      remove_unused_nodes=False)
        #doc.writeDoc()

    def test_widgets_as_variable(self):
        _sbs_widget_to_class = {
            sbsenum.WidgetEnum.SLIDER_INT1: 16,
            sbsenum.WidgetEnum.SLIDER_INT2: 32,
            sbsenum.WidgetEnum.SLIDER_INT3: 64,
            sbsenum.WidgetEnum.SLIDER_INT4: 128,
            sbsenum.WidgetEnum.SLIDER_FLOAT1: 256,
            sbsenum.WidgetEnum.SLIDER_FLOAT2: 512,
            sbsenum.WidgetEnum.SLIDER_FLOAT3: 1024,
            sbsenum.WidgetEnum.SLIDER_FLOAT4: 2048,
            sbsenum.WidgetEnum.ANGLE_FLOAT1: 256,
            sbsenum.WidgetEnum.COLOR_FLOAT1: 256,
            sbsenum.WidgetEnum.COLOR_FLOAT3: 1024,
            sbsenum.WidgetEnum.COLOR_FLOAT4: 2048,
            sbsenum.WidgetEnum.BUTTON_BOOL: 4,
            sbsenum.WidgetEnum.DROPDOWN_INT1: 16,
            sbsenum.WidgetEnum.SIZE_POW2_INT2: 32,
            sbsenum.WidgetEnum.MATRIX_INVERSE_FLOAT4: 2048,
            sbsenum.WidgetEnum.MATRIX_FORWARD_FLOAT4: 2048,
            sbsenum.WidgetEnum.POSITION_FLOAT2: 512,
            sbsenum.WidgetEnum.OFFSET_FLOAT2: 512,
        }
        sbs = sbsgenerator.createSBSDocument(context.Context(), '/tmp/foo.sbs')
        graph = sbs.createGraph('bar')
        node_pixelproc = graph.createCompFilterNode(sbsenum.FilterEnum.PIXEL_PROCESSOR)
        for key, values in _sbs_widget_to_class.items():
            input_foo = graph.addInputParameter(str(key), key)

            def _generate_function(ctx):
                node_variable = ctx.variable(input_foo.mIdentifier, key, )
                return ctx.generate(node_variable)

            function_pixelproc = ag.generate_function(_generate_function, sbs, fn_node=node_pixelproc.getPixProcFunction())
            self.assertEqual(node_pixelproc.getPixProcFunction().getNodeList()[0].getOutputType(), values)


if __name__ == '__main__':
    unittest.main()
