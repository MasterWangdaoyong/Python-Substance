"""
| Module **ag_types** defines a set of types for making it more convenient to write pixel processors, dynamic values and functions.
| It provides the definition of the classes:

    - :class:`.TypeInfo`
    - :class:`.Type`
    - :class:`.VectorType`
    - :class:`.FloatType`
    - :class:`.Float1`
    - :class:`.Float2`
    - :class:`.Float3`
    - :class:`.Float4`
    - :class:`.IntType`
    - :class:`.Int1`
    - :class:`.Int2`
    - :class:`.Int3`
    - :class:`.Int4`
    - :class:`.Boolean`
"""

from . import ag_helpers as helpers
from pysbs.sbsenum import BaseTypeEnum, FunctionEnum
from pysbs.api_exceptions import SBSTypeError


class TypeInfo:
    """
    Class representing type information
    """

    def __init__(self, base_type, vector_size=1):
        """
        :param base_type: The base type
        :type base_type: :class:`.BaseTypeEnum`
        :param vector_size: The number of elements in the type
        :type vector_size: int
        """
        self.base_type = base_type
        self.vector_size = vector_size

    def __str__(self):
        return 'BaseTypeEnum: %s, vector size: %s' % (self.type_to_string(self.base_type), self.vector_size)

    @staticmethod
    def type_to_string(a):
        name_strings = {BaseTypeEnum.FLOAT: 'FLOAT',
                        BaseTypeEnum.INT: 'INT',
                        BaseTypeEnum.BOOL: 'BOOL'}
        return name_strings[a]


class Type:
    """
    Base class for all sbs types
    """

    def __init__(self, new_node, fn_ctx, type_info):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function context this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        :param type_info: Type information for this type
        :type type_info: :class:`.TypeInfo`
        """
        self.fn_ctx = fn_ctx
        self.node = new_node
        self.type_info = type_info


class VectorType(Type):
    """
    Base class for scalar and vector arithmetic types (float, int)
    """

    def __init__(self, new_node, fn_ctx, type_info):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        :param type_info: Type information for this type
        :type type_info: :class:`.TypeInfo`
        """
        Type.__init__(self, new_node, fn_ctx, type_info)

    @helpers.auto_constify()
    def __add__(self, other):
        return helpers.create_binary_op(FunctionEnum.ADD, self, other)

    @helpers.auto_constify()
    def __radd__(self, other):
        return other.__add__(self)

    @helpers.auto_constify()
    def __sub__(self, other):
        return helpers.create_binary_op(FunctionEnum.SUB, self, other)

    @helpers.auto_constify()
    def __rsub__(self, other):
        return other.__sub__(self)

    @helpers.auto_constify()
    def __mul__(self, other):
        return helpers.create_binary_op(FunctionEnum.MUL, self, other)

    @helpers.auto_constify()
    def __rmul__(self, other):
        return other.__mul__(self)

    @helpers.auto_constify()
    def __div__(self, other):
        return helpers.create_binary_op(FunctionEnum.DIV, self, other)

    @helpers.auto_constify()
    def __rdiv__(self, other):
        return other.__div__(self)

    @helpers.auto_constify()
    def __truediv__(self, other):
        return helpers.create_binary_op(FunctionEnum.DIV, self, other)

    @helpers.auto_constify()
    def __rtruediv__(self, other):
        return other.__truediv__(self)

    @helpers.auto_constify()
    def __neg__(self):
        return helpers.create_unary_op(FunctionEnum.NEG, self)

    @helpers.auto_constify()
    def __mod__(self, other):
        return helpers.create_binary_op(FunctionEnum.MOD, self, other)

    @helpers.auto_constify()
    def __rmod__(self, other):
        return other.__mod__(self)


class FloatType(VectorType):
    """
    Base class for float scalar and vector arithmetic types
    """

    def __init__(self, new_node, fn_ctx, type_info):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        :param type_info: Type information for this type
        :type type_info: :class:`.TypeInfo`
        """
        VectorType.__init__(self, new_node, fn_ctx, type_info)

    @helpers.auto_constify()
    def __mul__(self, other):
        if helpers.check_type_identical(self, other):
            return helpers.create_binary_op(FunctionEnum.MUL, self, other)
        elif helpers.is_scalar(other) or helpers.is_scalar(self):
            return helpers.create_binary_op_scalar_vector(FunctionEnum.MUL_SCALAR, self, other)
        else:
            raise SBSTypeError('Scalar multiplication not supported for supplied types (%s), (%s)' %
                                (self.type_info, other.type_info))

    def __getitem__(self, key):
        return helpers.swizzle_vector([
            self.fn_ctx.swizzle_float1,
            self.fn_ctx.swizzle_float2,
            self.fn_ctx.swizzle_float3,
            self.fn_ctx.swizzle_float4],
            self, key)

    def __getattr__(self, name):
        if frozenset(name.lower()).issubset(frozenset("xyzwrgba")):
            return self.__getitem__(name)
        else:
            return Type.__getattr__(self, name)

class Float1(FloatType):
    """
    Scalar float node type
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        """
        FloatType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.FLOAT, 1))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_FLOAT, x, 1)
        return Float1(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_FLOAT1, name)
        return Float1(node, fn_ctx)

    @helpers.auto_constify()
    def __lt__(self, other):
        return helpers.create_binary_op(FunctionEnum.LOWER, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __gt__(self, other):
        return helpers.create_binary_op(FunctionEnum.GREATER, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __le__(self, other):
        return helpers.create_binary_op(FunctionEnum.LOWER_EQUAL, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __ge__(self, other):
        return helpers.create_binary_op(FunctionEnum.GREATER_EQUAL, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __eq__(self, other):
        return helpers.create_binary_op(FunctionEnum.EQ, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __ne__(self, other):
        return helpers.create_binary_op(FunctionEnum.NOT_EQ, self, other, output_type=Boolean)


class Float2(FloatType):
    """
    Float vector 2
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        """
        FloatType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.FLOAT, 2))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_FLOAT2, x, 2)
        return Float2(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_FLOAT2, name)
        return Float2(node, fn_ctx)


class Float3(FloatType):
    """
    Float vector 3
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        """
        FloatType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.FLOAT, 3))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_FLOAT3, x, 3)
        return Float3(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_FLOAT3, name)
        return Float3(node, fn_ctx)


class Float4(FloatType):
    """
    Float vector 4
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        """
        FloatType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.FLOAT, 4))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_FLOAT4, x, 4)
        return Float4(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_FLOAT4, name)
        return Float4(node, fn_ctx)


class IntType(VectorType):
    """
    Base class for int types
    """

    def __init__(self, new_node, fn_ctx, type_info):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or :class:`.SBSDynamicValue`
        """
        VectorType.__init__(self, new_node, fn_ctx, type_info)

    def __getitem__(self, key):
        return helpers.swizzle_vector([
            self.fn_ctx.swizzle_int1,
            self.fn_ctx.swizzle_int2,
            self.fn_ctx.swizzle_int3,
            self.fn_ctx.swizzle_int4],
            self, key)

    def __getattr__(self, name):
        if frozenset(name.lower()).issubset(frozenset("xyzwrgba")):
            return self.__getitem__(name)
        else:
            return Type.__getattr__(self, name)


class Int1(IntType):
    """
    Int scalar type
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or pysbs.graph.function.SBSDynamicValue
        """
        IntType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.INT, 1))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_INT, x, 1)
        return Int1(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_INTEGER1, name)
        return Int1(node, fn_ctx)

    @helpers.auto_constify()
    def __lt__(self, other):
        return helpers.create_binary_op(FunctionEnum.LOWER, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __gt__(self, other):
        return helpers.create_binary_op(FunctionEnum.GREATER, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __le__(self, other):
        return helpers.create_binary_op(FunctionEnum.LOWER_EQUAL, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __ge__(self, other):
        return helpers.create_binary_op(FunctionEnum.GREATER_EQUAL, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __eq__(self, other):
        return helpers.create_binary_op(FunctionEnum.EQ, self, other, output_type=Boolean)

    @helpers.auto_constify()
    def __ne__(self, other):
        return helpers.create_binary_op(FunctionEnum.NOT_EQ, self, other, output_type=Boolean)


class Int2(IntType):
    """
    Int vector 2 type
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or pysbs.graph.function.SBSDynamicValue
        """
        IntType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.INT, 2))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_INT2, x, 2)
        return Int2(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_INTEGER2, name)
        return Int2(node, fn_ctx)


class Int3(IntType):
    """
    Int vector 3 type
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or pysbs.graph.function.SBSDynamicValue
        """
        IntType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.INT, 3))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_INT3, x, 3)
        return Int3(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_INTEGER3, name)
        return Int3(node, fn_ctx)


class Int4(IntType):
    """
    Int vector 4 type
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or pysbs.graph.function.SBSDynamicValue
        """
        IntType.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.INT, 4))

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_INT4, x, 4)
        return Int4(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_INTEGER4, name)
        return Int4(node, fn_ctx)


class Boolean(Type):
    """
    Boolean type, always scalar
    """

    def __init__(self, new_node, fn_ctx):
        """
        :param new_node: The function node for the computation
        :type new_node: :class:`.SBSParamNode`
        :param fn_ctx: The function this node lives in
        :type fn_ctx: :class:`.SBSFunction` or pysbs.graph.function.SBSDynamicValue
        """
        Type.__init__(self, new_node, fn_ctx, TypeInfo(BaseTypeEnum.BOOL, 1))

    @helpers.auto_constify()
    def __or__(self, other):
        return helpers.create_binary_op(FunctionEnum.OR, self, other)

    @helpers.auto_constify()
    def __and__(self, other):
        return helpers.create_binary_op(FunctionEnum.AND, self, other)

    @helpers.auto_constify()
    def __invert__(self):
        return helpers.create_unary_op(FunctionEnum.NOT, self)

    @staticmethod
    def constant(x, fn_ctx):
        node = create_constant(fn_ctx.fn_node, FunctionEnum.CONST_BOOL, x, 1)
        return Boolean(node, fn_ctx)

    @staticmethod
    def variable(name, fn_ctx):
        node = create_variable(fn_ctx.fn_node, FunctionEnum.GET_BOOL, name)
        return Boolean(node, fn_ctx)


def create_constant(fn_node, type_enum, val, vector_size):
    """
    Creates a constant

    :param fn_node: The function to create the constant in
    :type fn_node: :class:`.SBSFunction`
    :param type_enum: The type of constant to create
    :type type_enum: :class:`.FunctionEnum`
    :param val: Constant value
    :type val: numeric type or list of numeric types
    :param vector_size: Size of vector
    :type vector_size: int
    :return: :class:`.Type`
    """
    if vector_size == 1:
        if not ((not hasattr(val, '__len__')) or len(val) == 1):
            raise SBSTypeError('Invalid constant %s for scalar' % str(val))
    else:
        if not len(val) == vector_size:
            raise SBSTypeError('Invalid constant %s for float vector size %d' % (str(val), vector_size))
    return fn_node.createFunctionNode(aFunction=type_enum, aParameters={type_enum: val})


def create_variable(fn_node, type_enum, name):
    """
    Creates a variable (i.e a named input reference)

    :param fn_node: The function to create the variable in in
    :type fn_node: :class:`.SBSFunction`
    :param type_enum: The type of variable to create
    :type type_enum: :class:`.FunctionEnum`
    :param name: Name of variable
    :type name: string
    :return: :class:`.Type`
    """
    node = fn_node.createFunctionNode(aFunction=type_enum,
                                      aParameters={type_enum: name})
    return node
