"""
Module **ag_functions** provides the definition of the classes :class:`.FunctionContext`,
used for making it simpler to define functions using the :mod:`.ag_types` classes.
"""
from . import ag_types as types
from . import ag_helpers as helpers
from . import ag_layout
from pysbs import sbsenum
from pysbs import graph
from pysbs.api_exceptions import SBSImpossibleActionError, SBSTypeError

"""
Dictionary for converting a parameter type
to its corresponding type
"""
_sbs_type_to_class = {
    sbsenum.ParamTypeEnum.INTEGER1: types.Int1,
    sbsenum.ParamTypeEnum.INTEGER2: types.Int2,
    sbsenum.ParamTypeEnum.INTEGER3: types.Int3,
    sbsenum.ParamTypeEnum.INTEGER4: types.Int4,
    sbsenum.ParamTypeEnum.FLOAT1: types.Float1,
    sbsenum.ParamTypeEnum.FLOAT2: types.Float2,
    sbsenum.ParamTypeEnum.FLOAT3: types.Float3,
    sbsenum.ParamTypeEnum.FLOAT4: types.Float4,
    sbsenum.ParamTypeEnum.BOOLEAN: types.Boolean
}

"""
Dictionary for converting a parameter type
to its corresponding type
"""
_sbs_widget_to_class = {
    sbsenum.WidgetEnum.SLIDER_INT1: types.Int1,
    sbsenum.WidgetEnum.SLIDER_INT2: types.Int2,
    sbsenum.WidgetEnum.SLIDER_INT3: types.Int3,
    sbsenum.WidgetEnum.SLIDER_INT4: types.Int4,
    sbsenum.WidgetEnum.SLIDER_FLOAT1: types.Float1,
    sbsenum.WidgetEnum.SLIDER_FLOAT2: types.Float2,
    sbsenum.WidgetEnum.SLIDER_FLOAT3: types.Float3,
    sbsenum.WidgetEnum.SLIDER_FLOAT4: types.Float4,
    sbsenum.WidgetEnum.ANGLE_FLOAT1: types.Float1,
    sbsenum.WidgetEnum.COLOR_FLOAT1: types.Float1,
    sbsenum.WidgetEnum.COLOR_FLOAT3: types.Float3,
    sbsenum.WidgetEnum.COLOR_FLOAT4: types.Float4,
    sbsenum.WidgetEnum.BUTTON_BOOL: types.Boolean,
    sbsenum.WidgetEnum.DROPDOWN_INT1: types.Int1,
    sbsenum.WidgetEnum.SIZE_POW2_INT2: types.Int2,
    sbsenum.WidgetEnum.MATRIX_INVERSE_FLOAT4: types.Float4,
    sbsenum.WidgetEnum.MATRIX_FORWARD_FLOAT4: types.Float4,
    sbsenum.WidgetEnum.POSITION_FLOAT2: types.Float2,
    sbsenum.WidgetEnum.OFFSET_FLOAT2: types.Float2,
}

def _one_bool(vec):
    """
    Checks if the vector has only one element, of type bool.

    :param vec: vector with values
    :type vec: list
    :return: bool, True if there is only one bool in the list otherwise False
    """
    return len(vec) == 1 and isinstance(vec[0], bool)


def _all_int(vec):
    """
    Checks if all elements in a vector is of type int

    :param vec: vector with values
    :type vec: list
    :return: bool, True if there are only ints in the list otherwise False
    """
    return all(isinstance(item, int) for item in vec)


def _type_from_constant(constant):
    """
    Returns the appropriate type for a constant vector

    :param constant: A float or int vector constant
    :type constant: list of int or list of float
    :return: :class:`.VectorType`
    """
    dimension = len(constant)
    if _one_bool(constant):
        return types.Boolean
    elif _all_int(constant):
        if dimension == 1:
            return types.Int1
        elif dimension == 2:
            return types.Int2
        elif dimension == 3:
            return types.Int3
        elif dimension == 4:
            return types.Int4
    else:
        # Assume float, there are other error checks
        # later in case something crazy is passed in
        if dimension == 1:
            return types.Float1
        elif dimension == 2:
            return types.Float2
        elif dimension == 3:
            return types.Float3
        elif dimension == 4:
            return types.Float4
    raise (SBSTypeError('Invalid vector size for constant (%d)' % dimension))


def _get_function_caller(node, fn_ctx, *args):
    """
    Create a python function that correspond to a local call (in the current document)
    to a substance function

    :param node: Constructor for a node
    :type node: function
    :param fn_ctx: A function node in which the function should be imported
    :type fn_ctx: :class:`.SBSDynamicValue`
    :param *args: parameters for the function
    :type *args: :class:`.Type`
    :return: A function for creating instances of this function
    """
    definition = node.getDefinition()
    _type = _sbs_type_to_class[definition.mOutputs[0].mType]

    # fixme multiple call to the same returned caller should create that many instances
    if not (len(definition.mInputs) == len(args)):
        raise SBSTypeError("Invalid argument count for (%s) given (%d), expected (%d)" %
                           (node.getReferenceInternalPath(), len(args), len(definition.mInputs)))
    for i in range(0, len(args)):
        input_source = args[i]
        input_connector = definition.mInputs[i]
        if not (str(input_connector.mType) == input_source.node.mType):
            raise SBSTypeError('Invalid type for parameter %s' % input_connector.getIdentifier())
        fn_ctx.fn_node.connectNodes(input_source.node, node, input_connector.mIdentifier)

    return _type(node, fn_ctx)


class FunctionContext:
    """
    Class helping out generating functions by keeping track
    of the document and the root node in which the construction happens
    """

    def __init__(self, doc, fn_node=None, name=None, use_constant_cache=True, layout_nodes=True,
                 remove_unused_nodes=True):
        """
        Constructor

        :param doc: The document to create the network in
        :type doc: :class:`.SBSDocument`
        :param fn_node: A function node in which the function should be created, must be None if the name is not None
        :type fn_node: :class:`.SBSDynamicValue`
        :param name: Name of the function to be created. Must be None if fn_node is not None
        :type name: string
        :param use_constant_cache: Decides whether identical constants should be merged
        :type use_constant_cache: bool
        """
        if (fn_node is None and name is None) or (fn_node is not None and name is not None):
            raise SBSImpossibleActionError('Either fn_node or name but not both must be set')
        self.fn_node = fn_node
        self.doc = doc
        if fn_node is None:
            self.fn_node = doc.createFunction(aFunctionIdentifier=name)
        self.constant_cache = {}
        self.use_constant_cache = use_constant_cache
        self.layout_nodes = layout_nodes
        self.remove_unused_nodes = remove_unused_nodes

    def input_parameter(self, name, widget_type):
        """
        Creates an input parameter for the graph and returns the node
        for accessing it.

        :param name: The name of the input parameter
        :type name: string
        :param widget_type: The type with its visual representation
        :type widget_type: :class:`.WidgetEnum`
        :return: :class:`.Type`
        """
        self.fn_node.addInputParameter(name, aWidget=widget_type)
        p_node = _sbs_widget_to_class[widget_type].variable(name, self)
        return p_node

    def variable(self, name, widget_type):
        """
        Creates a reference to a variable in the graph and returns the node
        for accessing it.

        :param name: The name of the input parameter
        :type name: string
        :param widget_type: The type with its visual representation
        :type widget_type: :class:`.WidgetEnum`
        :return: :class:`.Type`
        """
        p_node = _sbs_widget_to_class[widget_type].variable(name, self)
        return p_node

    def constant(self, constant, t=None):
        """
        Creates a constant

        :param constant: The constant value
        :type constant: int, bool, float, [int], [float]
        :param t: Type constructor None means autodetect
        :type t: None or a class such as Float3
        :return: :class:`.Type`
        """
        # Make the constant always be a vector even if a scalar is passed in
        if isinstance(constant, int) or isinstance(constant, float) or isinstance(constant, bool):
            constant = [constant]
        dt = t if t is not None else _type_from_constant(constant)
        if self.use_constant_cache and (tuple(constant), dt) in self.constant_cache:
            return self.constant_cache[(tuple(constant), dt)]
        res = dt.constant(constant, self)
        if res is None:
            raise SBSTypeError('Failed to create constant for %s' % str(constant))
        if self.use_constant_cache:
            self.constant_cache[(tuple(constant), dt)] = res
        return res

    def import_external_function(self, path):
        """
        Imports a function from the same document as the function is created in

        :param path: Path to function to import
        :type path: string
        :return: :class:`.Type` the node representing the imported function
        """

        @helpers.auto_constify()
        def caller(*args):
            node = self.fn_node.createFunctionInstanceNodeFromPath(self.doc, path)
            return _get_function_caller(node, self, *args)

        return caller

    def import_local_function(self, name):
        """
        Imports a function from an external file

        :param name: Name of function to import
        :type name: string
        :return: :class:`.Type` the node representing the imported function
        """
        f = self.doc.getSBSFunction(name)
        if f is None:
            raise SBSImpossibleActionError('Failed to import local function %s' % name)

        @helpers.auto_constify()
        def caller(*args):
            node = self.fn_node.createFunctionInstanceNode(self.doc, f)
            return _get_function_caller(node, self, *args)

        return caller

    def generate(self, output_node):
        """
        Finalizes function generation.

        :param output_node: The node that is the return value
        :type output_node: :class:`.Type`
        :return: :class:`.Type` the output node
        """
        self.fn_node.setOutputNode(output_node.node)
        if self.layout_nodes:
            fn_graph = self.fn_node.getDynamicValue() if isinstance(self.fn_node, graph.SBSFunction) else self.fn_node
            if self.remove_unused_nodes:
                nodesToKeep = ag_layout.NodesToKeepEnum.KEEP_COMPUTED_NODES
            else:
                nodesToKeep = ag_layout.NodesToKeepEnum.KEEP_ALL_NODES
            ag_layout.layoutGraph(
                fn_graph,
                nodesToKeep=nodesToKeep,
                layoutAlignment=ag_layout.GraphLayoutAlignment.OUTPUTS,
                commentsToKeep=ag_layout.GUIElementsToKeepEnum.KEEP_NONE if self.remove_unused_nodes else ag_layout.GUIElementsToKeepEnum.KEEP_ALL,
                framesToKeep=ag_layout.GUIElementsToKeepEnum.KEEP_NON_EMPTY if self.remove_unused_nodes else ag_layout.GUIElementsToKeepEnum.KEEP_ALL,
                navigationPinsToKeep=ag_layout.GUIElementsToKeepEnum.KEEP_NONE if self.remove_unused_nodes else ag_layout.GUIElementsToKeepEnum.KEEP_ALL)
        return output_node

    @helpers.auto_constify()
    def dot(self, a, b):
        """
        dot(a, b)
        Dot product

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :param b: input parameter 2
        :type b: :class:`.FloatType`, float or list of float
        :return: :class:`.Float1`
        """
        if not (helpers.check_type_identical(a, b) and helpers.is_float(a) and (not helpers.is_scalar(a))):
            raise SBSTypeError("Invalid types for dot product (%s), (%s)" % (a.type_info, b.type_info))
        new_node = helpers.create_binary_op(sbsenum.FunctionEnum.DOT, a, b, output_type=types.Float1)
        return new_node

    @helpers.auto_constify()
    def sqrt(self, a):
        """
        sqrt(a)
        Sqrt

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.SQRT, a)
        return new_node

    @helpers.auto_constify()
    def atan2(self, a):
        """
        atan2(a)
        Atan2

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        if not (helpers.is_float(a) and (a.type_info.vector_size == 2)):
            raise SBSTypeError("Invalid type for atan2 (%s)" % a.type_info)
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.ATAN2, a, output_type=types.Float1)
        return new_node

    @helpers.auto_constify()
    def abs_of(self, a):
        """
        abs_of(a)
        Modulus, or Absolute value, of a.

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.ABS, a)
        return new_node

    @helpers.auto_constify()
    def log(self, a):
        """
        log(a)
        Log

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.LOG, a)
        return new_node

    @helpers.auto_constify()
    def exp(self, a):
        """
        exp(a)
        Exp

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.EXP, a)
        return new_node

    @helpers.auto_constify()
    def log2(self, a):
        """
        log2(a)
        Log2

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.LOG2, a)
        return new_node

    @helpers.auto_constify()
    def pow2(self, a):
        """
        pow2(a)
        Pow2

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.POW2, a)
        return new_node

    @helpers.auto_constify()
    def floor(self, a):
        """
        floor(a)
        Floor

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.FLOOR, a)
        return new_node

    @helpers.auto_constify()
    def ceil(self, a):
        """
        ceil(a)
        Ceil

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.CEIL, a)
        return new_node

    @helpers.auto_constify()
    def cos(self, a):
        """
        cos(a)
        Cos

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.COS, a)
        return new_node

    @helpers.auto_constify()
    def sin(self, a):
        """
        sin(a)
        Sin

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.SIN, a)
        return new_node

    @helpers.auto_constify()
    def tan(self, a):
        """
        tan(a)
        Tan

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.TAN, a)
        return new_node

    @helpers.auto_constify()
    def rand(self, a):
        """
        rand(a)
        Rand

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :return: :class:`.FloatType`
        """
        if not (helpers.is_float(a) and helpers.is_scalar(a)):
            raise SBSTypeError("Invalid type for rand (%s)" % a.type_info)
        new_node = helpers.create_unary_op(sbsenum.FunctionEnum.RAND, a)
        return new_node

    @helpers.auto_constify()
    def cartesian(self, a, b):
        """
        cartesian(a, b)
        Cartesian

        :param a: input parameter 1, float or list of float
        :type a: :class:`.FloatType`
        :param b: input parameter 2, float or list of float
        :type b: :class:`.FloatType`
        :return: :class:`.Float2`
        """
        if not (helpers.is_float(a) and helpers.is_scalar(a) and helpers.is_float(b) and helpers.is_scalar(b)):
            raise SBSTypeError("Invalid type for cartesian (%s, %s)" % (a.type_info, b.type_info))
        new_node = helpers.create_binary_op(
            sbsenum.FunctionEnum.CARTESIAN, a, b, output_type=types.Float2, a_input='rho', b_input='theta')
        return new_node

    @helpers.auto_constify()
    def max_of(self, a, b):
        """
        max_of(a, b)
        Maximum of a and b

        :param a: input parameter 1
        :type a: :class:`.VectorType`, int, float, list of float or list of int
        :param b: input parameter 2
        :type b: :class:`.VectorType`, int, float, list of float or list of int
        :return: :class:`.VectorType`
        """
        if not helpers.is_arithmetic(a):
            raise SBSTypeError("Invalid types for max (%s), (%s)" % (a.type_info, b.type_info))
        new_node = helpers.create_binary_op(sbsenum.FunctionEnum.MAX, a, b)
        return new_node

    @helpers.auto_constify()
    def maximum(self, *values):
        """
        maximum(*values)
        Maximum value of the values

        :param values: input values
        :type values: :class:`.VectorType`, int, float, list of float or list of int
        :return: :class:`.VectorType`
        """
        n = len(values)
        if n == 0:
            raise SBSTypeError("You must provide at least one value to take the maximum from.")
        elif n == 1:
            return values[0]
        else:
            return self.max_of(self.maximum(*values[:n // 2]), self.maximum(*values[n // 2:]))

    @helpers.auto_constify()
    def min_of(self, a, b):
        """
        min_of(a, b)
        Minimum of a and b

        :param a: input parameter 1
        :type a: :class:`.VectorType`, int, float, list of float or list of int
        :param b: input parameter 2
        :type b: :class:`.VectorType`, int, float, list of float or list of int
        :return: :class:`.VectorType`
        """
        if not helpers.is_arithmetic(a):
            raise SBSTypeError("Invalid types for min (%s), (%s)" % (a.type_info, b.type_info))
        new_node = helpers.create_binary_op(sbsenum.FunctionEnum.MIN, a, b)
        return new_node

    @helpers.auto_constify()
    def minimum(self, *values):
        """
        minimum(*values)
        Minimum value of the values

        :param values: input values
        :type values: :class:`.VectorType`, int, float, list of float or list of int
        :return: :class:`.VectorType`
        """
        n = len(values)
        if n == 0:
            raise SBSTypeError("You must provide at least one value to take the minimum from.")
        elif n == 1:
            return values[0]
        else:
            return self.min_of(self.minimum(*values[:n // 2]), self.minimum(*values[n // 2:]))

    @helpers.auto_constify()
    def clamp(self, a, b, x):
        """
        clamp(a, b, x)
        Clamp value x between a and b.

        :param a: min value of clamped x
        :type a: :class:`.VectorType`, int, float, list of float or list of int
        :param b: max value of clamped x
        :type b: :class:`.VectorType`, int, float, list of float or list of int
        :param x: value to clamp
        :type a: :class:`.VectorType`, int, float, list of float or list of int
        :return: :class:`.VectorType`
        """
        return self.max_of(self.min_of(x, b), a)

    @helpers.auto_constify()
    def lerp(self, a, b, x):
        """
        lerp(a, b, x)
        Lerp

        :param a: input parameter 1
        :type a: :class:`.FloatType`, float or list of float
        :param b: input parameter 2
        :type b: :class:`.FloatType`, float or list of float
        :param x: lerp position
        :type x: :class:`.Float1` or float
        :return: :class:`.FloatType`
        """
        if not (helpers.is_scalar(x) and helpers.is_float(x)
                and helpers.check_type_identical(a, b) and helpers.is_float(a)):
            raise SBSTypeError("Invalid types for lerp (%s), (%s), (%s)" % (a.type_info, b.type_info, x.type_info))
        node = self.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.LERP)
        try:
            self.fn_node.connectNodes(a.node, node, 'a')
            self.fn_node.connectNodes(b.node, node, 'b')
            self.fn_node.connectNodes(x.node, node, 'x')
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return a.__class__(node, self)

    @helpers.auto_constify(0)
    def swizzle_float1(self, src, out_vars):
        """
        swizzle_float1(src, out_vars)
        Swizzle Float1

        :param src: input parameter
        :param src: :class:`.FloatType`, float or list of float
        :param out_vars: Output variable index
        :type out_vars: list of int
        :return: :class:`.Float1`
        """
        if not (helpers.is_float(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 1):
            raise SBSTypeError("Invalid types for swizzle_float1 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE1,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE1: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float1(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_float2(self, src, out_vars):
        """
        swizzle_float2(src, out_vars)
        Swizzle Float2

        :param src: input parameter
        :param src: :class:`.FloatType`, float or list of float
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Float2`
        """
        if not (helpers.is_float(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 2):
            raise SBSTypeError("Invalid types for swizzle_float2 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE2,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE2: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float2(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_float3(self, src, out_vars):
        """
        swizzle_float3(src, out_vars)
        Swizzle Float3

        :param src: input parameter
        :param src: :class:`.FloatType`, float or list of float
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Float3`
        """
        if not (helpers.is_float(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 3):
            raise SBSTypeError("Invalid types for swizzle_float3 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE3,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE3: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float3(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_float4(self, src, out_vars):
        """
        swizzle_float4(src, out_vars)
        Swizzle Float4

        :param src: input parameter
        :param src: :class:`.FloatType`, float or list of float
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Float4`
        """
        if not (helpers.is_float(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 4):
            raise SBSTypeError("Invalid types for swizzle_float4 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE4,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE4: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)

        return types.Float4(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_int1(self, src, out_vars):
        """
        swizzle_int1(src, out_vars)
        Swizzle Int1

        :param src: input parameter
        :param src: :class:`.IntType`, int or list of int
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Int1`
        """
        if not (helpers.is_int(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 1):
            raise SBSTypeError("Invalid types for swizzle_int1 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE_INT1,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE_INT1: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int1(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_int2(self, src, out_vars):
        """
        swizzle_int2(src, out_vars)
        Swizzle Int2

        :param src: input parameter
        :param src: :class:`.IntType`, int or list of int
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Int2`
        """
        if not (helpers.is_int(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 2):
            raise SBSTypeError("Invalid types for swizzle_int2 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE_INT2,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE_INT2: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int2(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_int3(self, src, out_vars):
        """
        swizzle_int3(src, out_vars)
        Swizzle Int3

        :param src: input parameter
        :param src: :class:`.IntType`, int or list of int
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Int3`
        """
        if not (helpers.is_int(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 3):
            raise SBSTypeError("Invalid types for swizzle_int3 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE_INT3,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE_INT3: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int3(node, src.fn_ctx)

    @helpers.auto_constify(0)
    def swizzle_int4(self, src, out_vars):
        """
        swizzle_int4(src, out_vars)
        Swizzle Int4

        :param src: input parameter
        :param src: :class:`.IntType`, int or list of int
        :param out_vars: Output variable indices
        :type out_vars: list of int
        :return: :class:`.Int4`
        """
        if not (helpers.is_int(src) and max(out_vars) < src.type_info.vector_size and len(out_vars) == 4):
            raise SBSTypeError("Invalid types for swizzle_int4 (%s) (%s)" % (src.type_info, out_vars))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SWIZZLE_INT4,
                                                     aParameters={sbsenum.FunctionEnum.SWIZZLE_INT4: out_vars})
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.VECTOR)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int4(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_int2(self, src, fill):
        """
        expand_to_int2(src, fill)
        Expands a Int1 to Int2

        :param src: source vector
        :type src: :class:`.Int1` or int
        :param fill: What to fill the empty values with
        :type fill: :class:`.IntType`, int or list of int
        :return: :class:`.Int2`
        """
        if not (helpers.is_scalar(fill) and helpers.is_int(fill) and helpers.is_int(src)):
            raise SBSTypeError("Invalid types for expand_to_int2 (%s), (%s)" % (src.type_info, fill))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR_INT2)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int2(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_int3(self, src, fill):
        """
        expand_to_int3(src, fill)
        Expands a Int1 or Int2 to Int3

        :param src: source vector
        :type src: :class:`.IntType`, int or list of int
        :param fill: What to fill the empty values with
        :type fill: :class:`.IntType`, int or list of int
        :return: :class:`.Int3`
        """
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR_INT3)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int3(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_int4(self, src, fill):
        """
        expand_to_int4(src, fill)
        Expands a Int1, Int2 or Int3 to Int4

        :param src: source vector
        :type src: :class:`.IntType`, int or list of int
        :param fill: What to fill the empty values with
        :type fill: :class:`.IntType`, int or list of int
        :return: :class:`.Int4`
        """
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR_INT4)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int4(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_float2(self, src, fill):
        """
        expand_to_float2(src, fill)
        Expands a Float1 to Float2

        :param src: source vector
        :type src: :class:`.Float1` or float
        :param fill: What to fill the empty values with
        :type fill: :class:`.FloatType`, float or list of float
        :return: :class:`.Float2`
        """
        if not (helpers.is_scalar(fill) and helpers.is_float(fill) and helpers.is_float(src)):
            raise SBSTypeError("Invalid types for expand_to_float2 (%s), (%s)" % (src.type_info, fill))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR2)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float2(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_float3(self, src, fill):
        """
        expand_to_float3(src, fill)
        Expands a Float1 or Float2 to Float3

        :param src: source vector
        :type src: :class:`.FloatType`, float or list of float
        :param fill: What to fill the empty values with
        :type fill: :class:`.FloatType`, float or list of float
        :return: :class:`.Float3`
        """
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR3)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float3(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand_to_float4(self, src, fill):
        """
        expand_to_float4(src, fill)
        Expands a Float1, Float2 or Float3 to Float4

        :param src: source vector
        :type src: :class:`.FloatType`, float or list of float
        :param fill: What to fill the empty values with
        :type fill: :class:`.FloatType`, float or list of float
        :return: :class:`.Float4`
        """
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.VECTOR4)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node, sbsenum.FunctionInputEnum.COMPONENTS_IN)
            src.fn_ctx.fn_node.connectNodes(fill.node, node, sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float4(node, src.fn_ctx)

    @helpers.auto_constify()
    def expand(self, *vectors):
        """
        expand(*vectors)
        Expand two vector to a vector of the appropriate type and dimension.

        The sum of the dimension of the input vectors must not be larger than 4.
        Plus all input vectors must be integers or all input vectors must be float.

        :param vectors: vectors to concatenate
        :type vectors: :class:`.VectorType`, int, float, list of int, list of float
        :return: :class:`.VectorType`
        """
        if not all(map(helpers.is_arithmetic, vectors)):
            raise SBSTypeError("You must use arithmetic vectors.")

        total_size = sum([v.type_info.vector_size for v in vectors])
        if not 1 <= total_size <= 4:
            raise SBSTypeError("Size of final vector must have a dimension no larger than 4 and at least of 1 (is %d)."
                               % total_size)

        expand_to = {}
        if all(map(helpers.is_int, vectors)):
            expand_to[2] = self.expand_to_int2
            expand_to[3] = self.expand_to_int3
            expand_to[4] = self.expand_to_int4
        elif all(map(helpers.is_float, vectors)):
            expand_to[2] = self.expand_to_float2
            expand_to[3] = self.expand_to_float3
            expand_to[4] = self.expand_to_float4
        else:
            raise SBSTypeError("Cannot mix float and integer vectors types to be expanded.")

        if total_size == vectors[0].type_info.vector_size:
            assert len(vectors) == 1
            return vectors[0]
        else:
            assert len(vectors) > 1
            return expand_to[total_size](self.expand(*vectors[:-1]), vectors[-1])

    @helpers.auto_constify()
    def cast_to_float1(self, src):
        """
        cast_to_float1(src)
        Casts an Int1 to Float1

        :param src: source
        :type src: :class:`.Int1` or int
        :return: :class:`.Float1`
        """
        if not (helpers.is_int(src) and src.type_info.vector_size == 1):
            raise SBSTypeError("Invalid type for cast_to_float1 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_FLOAT)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float1(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_float2(self, src):
        """
        cast_to_float2(src)
        Casts an Int2 to Float2

        :param src: source
        :type src: :class:`.Int2` or list of int
        :return: :class:`.Float2`
        """
        if not (helpers.is_int(src) and src.type_info.vector_size == 2):
            raise SBSTypeError("Invalid type for cast_to_float2 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_FLOAT2)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float2(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_float3(self, src):
        """
        cast_to_float3(src)
        Casts an Int3 to Float3

        :param src: source
        :type src: :class:`.Int3` or list of int
        :return: :class:`.Float3`
        """
        if not (helpers.is_int(src) and src.type_info.vector_size == 3):
            raise SBSTypeError("Invalid type for cast_to_float3 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_FLOAT3)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float3(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_float4(self, src):
        """
        cast_to_float4(src)
        Casts an Int4 to Float4

        :param src: source
        :type src: :class:`.Int4` or list of int
        :return: :class:`.Float4`
        """
        if not (helpers.is_int(src) and src.type_info.vector_size == 4):
            raise SBSTypeError("Invalid type for cast_to_float4 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_FLOAT4)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float4(node, src.fn_ctx)

    @helpers.auto_constify()
    def auto_cast_to_float(self, src):
        """
        auto_cast_to_float(src)
        Casts a numeric vector to a float vector of the same dimension

        :param src: source vector
        :type src: :class:`.IntType`, int or list of int
        :return: :class:`.FloatType`
        """
        if helpers.is_float(src):
            return src
        elif helpers.is_int(src):
            size = src.type_info.vector_size
            if size == 1:
                return self.cast_to_float1(src)
            elif size == 2:
                return self.cast_to_float2(src)
            elif size == 3:
                return self.cast_to_float3(src)
            elif size == 4:
                return self.cast_to_float4(src)
        else:
            raise SBSTypeError("Invalid type for cast_to_int4 (%s)" % helpers.get_type_info(src))

    @helpers.auto_constify()
    def cast_to_int1(self, src):
        """
        cast_to_int1(src)
        Casts a Float1 to Int1

        :param src: source
        :type src: :class:`.Float1` or float
        :return: :class:`.Int1`
        """
        if not (helpers.is_float(src) and src.type_info.vector_size == 1):
            raise SBSTypeError("Invalid type for cast_to_int1 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_INT)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int1(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_int2(self, src):
        """
        cast_to_int2(src)
        Casts a Float2 to Int2

        :param src: source
        :type src: :class:`.Float2` or list of float
        :return: :class:`.Int2`
        """
        if not (helpers.is_float(src) and src.type_info.vector_size == 2):
            raise SBSTypeError("Invalid type for cast_to_int2 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_INT2)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int2(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_int3(self, src):
        """
        cast_to_int3(src)
        Casts a Float3 to Int3

        :param src: source
        :type src: :class:`.Float3` or list of float
        :return: :class:`.Int3`
        """
        if not (helpers.is_float(src) and src.type_info.vector_size == 3):
            raise SBSTypeError("Invalid type for cast_to_int3 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_INT3)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int3(node, src.fn_ctx)

    @helpers.auto_constify()
    def cast_to_int4(self, src):
        """
        cast_to_int4(src)
        Casts a Float4 to Int4

        :param src: source
        :type src: :class:`.Float4` or list of float
        :return: :class:`.Int4`
        """
        if not (helpers.is_float(src) and src.type_info.vector_size == 4):
            raise SBSTypeError("Invalid type for cast_to_int4 (%s)" % helpers.get_type_info(src))
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.TO_INT4)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Int4(node, src.fn_ctx)

    @helpers.auto_constify()
    def auto_cast_to_int(self, src):
        """
        auto_cast_to_int(src)
        Casts a numeric vector to an Int vector of the same dimension

        :param src: source vector
        :type src: :class:`.FloatType` float or list of float
        :return: :class:`.IntType`
        """
        if helpers.is_int(src):
            return src
        elif helpers.is_float(src):
            size = src.type_info.vector_size
            if size == 1:
                return self.cast_to_int1(src)
            elif size == 2:
                return self.cast_to_int2(src)
            elif size == 3:
                return self.cast_to_int3(src)
            elif size == 4:
                return self.cast_to_int4(src)
        else:
            raise SBSTypeError("Invalid type for cast_to_int4 (%s)" % helpers.get_type_info(src))

    @helpers.auto_constify()
    def if_else(self, condition, value_on_true, value_on_false):
        """
        if_else(condition, value_on_true, value_on_false)
        Choose one of two values based on a condition

        :param condition: The condition to select on
        :type condition: :class:`.Boolean` or bool
        :param value_on_true: Return value for true
        :type value_on_true: :class:`.VectorType`, float, int, list of float or list of int
        :param value_on_false: Return value for false
        :type value_on_false: :class:`.VectorType`, float, int, list of float or list of int
        :return: :class:`.VectorType`
        """
        if not (helpers.is_bool(condition) and helpers.check_type_identical(value_on_true, value_on_false)):
            raise SBSTypeError(
                "Invalid types for if (%s) (%s), (%s)" % (
                    condition.type_info, value_on_true.type_info, value_on_false.type_info))
        node = condition.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.IF_ELSE)
        try:
            condition.fn_ctx.fn_node.connectNodes(condition.node, node, 'condition')
            condition.fn_ctx.fn_node.connectNodes(value_on_true.node, node, sbsenum.FunctionInputEnum.IF_PATH)
            condition.fn_ctx.fn_node.connectNodes(value_on_false.node, node, sbsenum.FunctionInputEnum.ELSE_PATH)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return value_on_true.__class__(node, condition.fn_ctx)

    @helpers.auto_constify()
    def seq(self, a, b):
        """
        seq(a, b)
        Execute all nodes resulting in branch a then execute all nodes resulting in branch b.
        Outputs the output of branch b.

        :param a: input sequence 1
        :type a: :class:`.Type`
        :param b: input sequence 2
        :type b: :class:`.Type`
        :return: :class:`.Type`
        """
        node = self.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SEQUENCE)
        try:
            self.fn_node.connectNodes(a.node, node, 'seqin')
            self.fn_node.connectNodes(b.node, node, 'seqlast')
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return b.__class__(node, b.fn_ctx)

    @helpers.auto_constify()
    def sequence(self, *values):
        """
        sequence(*values)
        Execute all nodes in sequence and output the output of the last input.

        :param values: input sequences
        :type values: :class:`.Type`
        :return: :class:`.Type`
        """
        n = len(values)
        if n <= 0:
            raise SBSTypeError("You must provide at least one input to a sequence of commands.")
        elif n == 1:
            return values[0]
        else:
            return self.seq(self.sequence(*values[:-1]), values[-1])

    @helpers.auto_constify(0)
    def set_var(self, a, name):
        """
        set_var(a, name)
        Set a variable name to the give value.

        :param a: value to set
        :type a: :class:`.Type`, bool, int, float, list of int or list of float
        :param name: name of the set value
        :type name: str
        :return: :class:`.Type`
        """
        node = self.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SET,
                                               aParameters={sbsenum.FunctionEnum.SET: name})
        try:
            self.fn_node.connectNodes(a.node, node, 'value')
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return a.__class__(node, self)

    @helpers.auto_constify(0)
    def create_color_sampler(self, pos, input_index, filtering_mode=sbsenum.FilteringEnum.NEAREST):
        """
        create_color_sampler(pos, input_index)
        Creates a color sampler

        :param pos: Point to sample
        :type pos: :class:`.Float2` or list of float
        :param input_index: Index of input to sample from
        :type input_index: int
        :param filtering_mode: Filter to use for the sampler
        :type filtering_mode: :class:`.FilteringEnum`
        :return: :class:`.Float4`
        """
        if not (helpers.is_float(pos) and pos.type_info.vector_size == 2):
            raise SBSTypeError("Invalid type for create_color_sampler (%s)" % pos.type_info)
        if not type(input_index) == int:
            raise SBSTypeError("Input index must be a regular python int")
        if not filtering_mode in vars(sbsenum.FilteringEnum).values():
            raise SBSTypeError("filtering_mode must be a value in sbsenum.FilteringEnum")
        node = pos.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SAMPLE_COL,
                                                     aParameters={sbsenum.FunctionEnum.SAMPLE_COL:
                                                                      [input_index, filtering_mode]})
        try:
            pos.fn_ctx.fn_node.connectNodes(pos.node, node, 'pos')
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float4(node, pos.fn_ctx)

    @helpers.auto_constify(0)
    def create_gray_sampler(self, pos, input_index, filtering_mode=sbsenum.FilteringEnum.NEAREST):
        """
        create_gray_sampler(pos, input_index)
        Creates a gray scale sampler

        :param pos: Point to sample
        :type pos: :class:`.Float2` or list of float
        :param input_index: Index of input to sample from
        :type input_index: int
        :param filtering_mode: Filter to use for the sampler
        :type filtering_mode: :class:`.FilteringEnum`
        :return: :class:`.Float1`
        """
        if not (helpers.is_float(pos) and pos.type_info.vector_size == 2):
            raise SBSTypeError("Invalid type for create_color_sampler (%s)" % pos.type_info)
        if not type(input_index) == int:
            raise SBSTypeError("Input index must be a regular python int")
        if not filtering_mode in vars(sbsenum.FilteringEnum).values():
            raise SBSTypeError("filtering_mode must be a value in sbsenum.FilteringEnum")
        node = pos.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.SAMPLE_LUM,
                                                     aParameters={sbsenum.FunctionEnum.SAMPLE_LUM:
                                                                      [input_index, filtering_mode]})
        try:
            pos.fn_ctx.fn_node.connectNodes(pos.node, node, 'pos')
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return types.Float1(node, pos.fn_ctx)

    @helpers.auto_constify(0)
    def create_passthrough(self, src):
        """
        passthrough(src)
        Create a PassThrough (dot) node function

        :param src: source
        :type src: :class:`.Type`, any class that inherits Type
        :return: :class:`.SBSFunction`
        """
        node = src.fn_ctx.fn_node.createFunctionNode(aFunction=sbsenum.FunctionEnum.PASSTHROUGH)
        try:
            src.fn_ctx.fn_node.connectNodes(src.node, node)
        except SBSImpossibleActionError as e:
            raise SBSTypeError(e.message)
        return node

    # derived operations
    @helpers.auto_constify()
    def normalize(self, a):
        """
        normalize(a)
        Normalize a vector

        :param a: Vector to normalize
        :type a: :class:`.FloatType` or list of float
        :return: :class:`.FloatType`
        """
        if not (helpers.is_float(a) and (not helpers.is_scalar(a))):
            raise SBSTypeError("Invalid types for normalize (%s), (%s)" % a.type_info)
        one = types.Float1.constant(1.0, self)
        return a * (one / self.sqrt(self.dot(a, a)))


def generate_function(fn, doc, fn_node=None, name=None, layout_nodes=True, remove_unused_nodes=True):
    """
    Generates a function by calling back to the generator function

    :param fn: Function taking a FunctionContext as input that generates the actual operations
    :type fn: Python function, taking as unique parameter a :class:`.FunctionContext`
    :param doc: The document to create the network in
    :type doc: :class:`.SBSDocument`
    :param fn_node: A function node in which the function should be created, must be None if the name is not None
    :type fn_node: :class:`.SBSDynamicValue`
    :param name: Name of the function to be created. Must be None if fn_node is not None
    :type name: string
    :param layout_nodes: Whether the nodes should be laid out left to right
    :type layout_nodes: bool
    :param remove_unused_nodes: Whether nodes not connected to the output node should be removed.
           Only works if layout_nodes is true
    :type remove_unused_nodes: bool
    :return: function to call to create node
    """
    fn_gen = FunctionContext(doc, fn_node=fn_node, name=name, layout_nodes=layout_nodes,
                             remove_unused_nodes=remove_unused_nodes)
    return fn_gen.generate(fn(fn_gen))
