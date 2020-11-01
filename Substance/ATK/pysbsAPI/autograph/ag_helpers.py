from functools import wraps

from pysbs import python_helpers
from pysbs.api_exceptions import SBSTypeError
from pysbs.sbsenum import BaseTypeEnum


def check_type_identical(a, b):
    """
    Checks if two types are identical

    :param a: type to check
    :type a: :class:`.Type`
    :param b: type to check
    :type b: :class:`.Type`
    :return: boolean if the types are identical
    """
    return a.__class__ == b.__class__


def check_type_same_base(a, b):
    """
    Checks if two types have identical base types

    :param a: type to check
    :type a: :class:`.Type`
    :param b: type to check
    :type b: :class:`.Type`
    :return: boolean if the types have identical base type
    """
    return hasattr(a, 'type_info') and hasattr(b, 'type_info') and a.type_info.base_type == b.type_info.base_type


def auto_constify(*selector):
    """
    Decorator making sure all constant inputs are created as constants
    nodes in the graph before calling the function using the first
    available context

    :param selector: indices of to parameters to ignore when constifying
    :type selector: int
    :return: a decorated function
    """
    def decorator(f):

        @wraps(f)
        def caller(*args):
            # Don't look for arguments to wrap in functions with zero parameters
            if len(args) == 0:
                return f()

            fn_ctx = None
            if args[0].__class__.__name__ == 'FunctionContext':
                fn_ctx = args[0]

            # Mark indexes to constify
            if len(selector) != 0:
                constified_indexes = selector
            else:
                constified_indexes = [k for k in range(len(args))]

            # Find a function context to use to create constants
            if fn_ctx is None:
                for k in constified_indexes:
                    # The following line is a replacement of this check
                    #     if isinstance(args[k], types.Type):
                    # That replacement has been introduced to break circular dependencies
                    if hasattr(args[k], 'fn_ctx'):
                        fn_ctx = args[k].fn_ctx
                        break
            if fn_ctx is None:
                raise SBSTypeError("Autograph operations must receive at least one autograph type as argument.")

            # Constify
            new_args = list(args)
            for k in constified_indexes:
                arg = args[k]
                if python_helpers.isIntOrLong(arg) or \
                        isinstance(arg, float) or \
                        isinstance(arg, bool) or \
                        isinstance(arg, list) or \
                        isinstance(arg, tuple):
                    new_args[k] = fn_ctx.constant(arg)
            return f(*new_args)

        return caller

    return decorator


def create_binary_op(op, a, b, output_type=None, a_input='a', b_input='b'):
    """
    Creates a binary operation with identical inputs and connect the outputs of a and b as inputs

    :param op: Operation to generate
    :type op: :class:`.FunctionEnum`
    :param a: input parameter 1
    :type a: :class:`.Type`
    :param b: input parameter 2
    :type b: :class:`.Type`
    :param output_type: class for result of the operation, none means use the type of a
    :type output_type: subclass of Type
    :param a_input: name of input for parameter a in the generated operator
    :type a_input: string
    :param b_input: name of input for parameter b in the generated operator
    :type b_input: string
    :return: :class:`.Type`
    """
    if not check_type_identical(a, b):
        raise SBSTypeError('Incompatible types "%s", "%s" for operator %s'
                           % (a.type_info if hasattr(a, 'type_info') else str(type(a)),
                              b.type_info if hasattr(b, 'type_info') else str(type(b)), str(op)))
    node = a.fn_ctx.fn_node.createFunctionNode(aFunction=op)
    a.fn_ctx.fn_node.connectNodes(a.node, node, a_input)
    a.fn_ctx.fn_node.connectNodes(b.node, node, b_input)
    if output_type is None:
        return a.__class__(node, a.fn_ctx)
    else:
        return output_type(node, a.fn_ctx)


def create_unary_op(op, a, output_type=None, a_input='a'):
    """
    Creates a unary operation and connect the output of a as input

    :param op: Operation to generate
    :type op: sbsenum.FunctionEnum
    :param a: input parameter 1
    :type a: :class:`.Type`
    :param output_type: class for result of the operation, none means use the type of a
    :type output_type: subclass of Type
    :param a_input: name of input for parameter a in the generated operator
    :type a_input: string
    :return: :class:`.Type`
    """
    node = a.fn_ctx.fn_node.createFunctionNode(aFunction=op)
    a.fn_ctx.fn_node.connectNodes(a.node, node, a_input)
    if output_type is None:
        return a.__class__(node, a.fn_ctx)
    else:
        return output_type(node, a.fn_ctx)


def is_arithmetic(a):
    """
    Checks if a type are arithmetic (support +, -, etc.)

    :param a: type to check
    :type a: :class:`.Type`
    :return: boolean if a is arithmetic
    """
    return hasattr(a, 'type_info') and (
            a.type_info.base_type == BaseTypeEnum.FLOAT or a.type_info.base_type == BaseTypeEnum.INT)


def is_float(a):
    """
    Checks if a type is float (vector size not considered)

    :param a: type to check
    :type a: :class:`.Type`
    :return: boolean if a is float
    """
    return hasattr(a, 'type_info') and a.type_info.base_type == BaseTypeEnum.FLOAT


def is_int(a):
    """
    Checks if a type is int (vector size not considered)

    :param a: type to check
    :type a: :class:`.Type`
    :return: boolean if a is int
    """
    return hasattr(a, 'type_info') and a.type_info.base_type == BaseTypeEnum.INT


def is_bool(a):
    """
    Checks if a type is bool (vector size not considered)

    :param a: type to check
    :type a: :class:`.Type`
    :return: boolean if a is bool
    """
    return hasattr(a, 'type_info') and a.type_info.base_type == BaseTypeEnum.BOOL


def is_scalar(a):
    """
    Checks if a type is scalar (vector size is 1)

    :param a: type to check
    :type a: :class:`.Type`
    :return: boolean if a is scalar
    """
    return hasattr(a, 'type_info') and a.type_info.vector_size == 1


def get_type_info(a):
    if hasattr(a, 'type_info'):
        return a.type_info
    else:
        return type(a)


def create_binary_op_scalar_vector(op, a, b, a_input='a', scalar_input='scalar'):
    """
    Creates a binary operation with one vector and one scalar type as input
    It will identify the which one of the inputs is scalar and which one is vector

    :param op: Operation to generate
    :type op: sbsenum.FunctionEnum
    :param a: input parameter 1
    :type a: :class:`.Type`
    :param b: input parameter 2
    :type b: :class:`.Type`
    :param a_input: name of input for vector parameter in the generated operator
    :type a_input: string
    :param scalar_input: name of input for scalar parameter in the generated operator
    :type scalar_input: string
    :return: :class:`.Type`
    """
    if not check_type_same_base(a, b):
        raise SBSTypeError('Incompatible base type %s, %s for operator %s' % (a.type_info, b.type_info, str(op)))
    node = a.fn_ctx.fn_node.createFunctionNode(aFunction=op)
    vector = None
    scalar = None
    if a.type_info.vector_size == 1:
        scalar = a
        vector = b
    elif b.type_info.vector_size == 1:
        scalar = b
        vector = a
    vector.fn_ctx.fn_node.connectNodes(vector.node, node, a_input)
    vector.fn_ctx.fn_node.connectNodes(scalar.node, node, scalar_input)
    return vector.__class__(node, vector.fn_ctx)


def swizzle_vector(swizzle_functions, x, key):
    """
    Utility function that chooses the right swizzle function in order to get a set of values out of a string
    representing the parameters to get out of the vector

    :param swizzle_functions: Vector of swizzle functions representing for swizzling 1-4 elements as output
    :type swizzle_functions: list of :function:
    :param x: The parameter to swizzle
    :type x: :class:`.VectorType`
    :param key: string of ordered outputs expected
    :type key: string
    :return:
    """
    swizzle_indexes = []
    if type(key) == int:
        if not (0 <= key < x.type_info.vector_size):
            raise SBSTypeError("Invalid index %d" % key)
        swizzle_indexes = [key]
    elif type(key) == str:
        char_to_index = {'x': 0, 'y': 1, 'z': 2, 'w': 3, 'r': 0, 'g': 1, 'b': 2, 'a': 3}
        for character in key.lower():
            if character not in char_to_index:
                raise SBSTypeError("Don't know what index to attribute to character %d" % character)
            swizzle_indexes.append(char_to_index[character])
    elif type(key) == slice:
        if not {type(key.start), type(key.stop), type(key.step)}.issubset({int, type(None)}):
            raise SBSTypeError('Addressing vectors with range only works with integer indexes')
        if key.start > x.type_info.vector_size or key.start < 0:
            raise SBSTypeError('Invalid index %d' % key.start)
        if key.stop - 1 > x.type_info.vector_size or key.stop - 1 < 0:
            raise SBSTypeError('Invalid index %d' % key.stop)
        swizzle_indexes = list(range(*key.indices(x.type_info.vector_size)))
    else:
        raise SBSTypeError('Addressing vectors only works with constants or slices of constants at the moment')

    swizzle_size = len(swizzle_indexes)
    if swizzle_size == 0:
        raise SBSTypeError('Nothing to swizzle with an empty list of indexes')
    elif swizzle_size <= 4:
        return swizzle_functions[swizzle_size - 1](x, swizzle_indexes)
    else:
        raise SBSTypeError('Too many indexes to swizzle from : %s' % (str(swizzle_indexes),))
