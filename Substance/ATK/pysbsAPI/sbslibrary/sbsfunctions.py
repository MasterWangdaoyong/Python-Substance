# coding: utf-8
"""
Module **sbsfunctions** provides the library of function nodes and their definition (inputs, outputs, parameters):

    * function_SEQUENCE
    * function_IF_ELSE
    * function_SET
    * function_GET_BOOL
    * function_GET_INTEGER1
    * function_GET_INTEGER2
    * function_GET_INTEGER3
    * function_GET_INTEGER4
    * function_GET_FLOAT1
    * function_GET_FLOAT2
    * function_GET_FLOAT3
    * function_GET_FLOAT4
    * function_GET_STRING
    * function_CONST_BOOL
    * function_CONST_INT
    * function_CONST_INT2
    * function_CONST_INT3
    * function_CONST_INT4
    * function_CONST_FLOAT
    * function_CONST_FLOAT2
    * function_CONST_FLOAT3
    * function_CONST_FLOAT4
    * function_CONST_STRING
    * function_INSTANCE
    * function_VECTOR2
    * function_VECTOR3
    * function_VECTOR4
    * function_SWIZZLE1
    * function_SWIZZLE2
    * function_SWIZZLE3
    * function_SWIZZLE4
    * function_VECTOR_INT2
    * function_VECTOR_INT3
    * function_VECTOR_INT4
    * function_SWIZZLE_INT1
    * function_SWIZZLE_INT2
    * function_SWIZZLE_INT3
    * function_SWIZZLE_INT4
    * function_TO_INT
    * function_TO_INT2
    * function_TO_INT3
    * function_TO_INT4
    * function_TO_FLOAT
    * function_TO_FLOAT2
    * function_TO_FLOAT3
    * function_TO_FLOAT4
    * function_ADD
    * function_SUB
    * function_MUL
    * function_MUL_SCALAR
    * function_DIV
    * function_NEG
    * function_MOD
    * function_DOT
    * function_CROSS
    * function_AND
    * function_OR
    * function_NOT
    * function_EQ
    * function_NOT_EQ
    * function_GREATER
    * function_GREATER_EQUAL
    * function_LOWER
    * function_LOWER_EQUAL
    * function_ABS
    * function_FLOOR
    * function_CEIL
    * function_COS
    * function_SIN
    * function_SQRT
    * function_LOG
    * function_LOG2
    * function_EXP
    * function_POW2
    * function_TAN
    * function_ATAN2
    * function_CARTESIAN
    * function_LERP
    * function_MIN
    * function_MAX
    * function_RAND
    * function_SAMPLE_LUM
    * function_SAMPLE_COL
    * function_PASSTHROUGH

"""

from __future__ import unicode_literals
import sys

from pysbs import sbsenum
from pysbs.api_decorators import doc_module_attributes
from .sbslibclasses import FunctionDef,FunctionInput,FunctionOutput,FunctionParam



function_SEQUENCE = FunctionDef(
    aIdentifier =    'sequence',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.SEQUENCE_IN,   sbsenum.TypeMasksEnum.FUNCTION_ALL ),
                      FunctionInput(sbsenum.FunctionInputEnum.SEQUENCE_LAST, sbsenum.ParamTypeEnum.TEMPLATE1    )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FUNCTION_ALL)

function_IF_ELSE = FunctionDef(
    aIdentifier =    'ifelse',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.CONDITION, sbsenum.ParamTypeEnum.BOOLEAN   ),
                      FunctionInput(sbsenum.FunctionInputEnum.IF_PATH,   sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.ELSE_PATH, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FUNCTION_ALL&~sbsenum.ParamTypeEnum.VOID_TYPE)

function_SET = FunctionDef(
    aIdentifier =    'set',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SET, sbsenum.ParamTypeEnum.STRING,   ''    )],
    aTemplate1 =     sbsenum.TypeMasksEnum.FUNCTION_ALL&~sbsenum.ParamTypeEnum.VOID_TYPE)

function_GET_BOOL = FunctionDef(
    aIdentifier =    'get_bool',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_BOOL, sbsenum.ParamTypeEnum.STRING,''  )])

function_GET_INTEGER1 = FunctionDef(
    aIdentifier =    'get_integer1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER1)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_INTEGER1, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_INTEGER2 = FunctionDef(
    aIdentifier =    'get_integer2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER2)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_INTEGER2, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_INTEGER3 = FunctionDef(
    aIdentifier =    'get_integer3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER3)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_INTEGER3, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_INTEGER4 = FunctionDef(
    aIdentifier =    'get_integer4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER4)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_INTEGER4, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_FLOAT1 = FunctionDef(
    aIdentifier =    'get_float1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_FLOAT1, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_FLOAT2 = FunctionDef(
    aIdentifier =    'get_float2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_FLOAT2, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_FLOAT3 = FunctionDef(
    aIdentifier =    'get_float3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT3)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_FLOAT3, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_FLOAT4 = FunctionDef(
    aIdentifier =    'get_float4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_FLOAT4, sbsenum.ParamTypeEnum.STRING, '')])

function_GET_STRING = FunctionDef(
    aIdentifier =    'get_string',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.STRING)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.GET_STRING, sbsenum.ParamTypeEnum.STRING, '')])

function_CONST_BOOL = FunctionDef(
    aIdentifier =    'const_bool',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_BOOL, sbsenum.ParamTypeEnum.BOOLEAN, '')])

function_CONST_INT = FunctionDef(
    aIdentifier =    'const_int1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER1)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_INT , sbsenum.ParamTypeEnum.INTEGER1, '')])

function_CONST_INT2 = FunctionDef(
    aIdentifier =    'const_int2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER2)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_INT2, sbsenum.ParamTypeEnum.INTEGER2, '')])

function_CONST_INT3 = FunctionDef(
    aIdentifier =    'const_int3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER3)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_INT3, sbsenum.ParamTypeEnum.INTEGER3, '')])

function_CONST_INT4 = FunctionDef(
    aIdentifier =    'const_int4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER4)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_INT4, sbsenum.ParamTypeEnum.INTEGER4, '')])

function_CONST_FLOAT = FunctionDef(
    aIdentifier =    'const_float1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_FLOAT, sbsenum.ParamTypeEnum.FLOAT1, '')])

function_CONST_FLOAT2 = FunctionDef(
    aIdentifier =    'const_float2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_FLOAT2, sbsenum.ParamTypeEnum.FLOAT2, '')])

function_CONST_FLOAT3 = FunctionDef(
    aIdentifier =    'const_float3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT3)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_FLOAT3, sbsenum.ParamTypeEnum.FLOAT3, '')])

function_CONST_FLOAT4 = FunctionDef(
    aIdentifier =    'const_float4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_FLOAT4, sbsenum.ParamTypeEnum.FLOAT4, '')])

function_CONST_STRING = FunctionDef(
    aIdentifier =    'const_string',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.STRING)],
    aInputs =        [],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.CONST_STRING, sbsenum.ParamTypeEnum.STRING, '')])

function_INSTANCE = FunctionDef(
    aIdentifier =    'instance',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.TypeMasksEnum.FUNCTION_ALL)],
    aInputs  =       [],
    aFunctionDatas=  [FunctionParam(sbsenum.FunctionEnum.INSTANCE, sbsenum.ParamTypeEnum.STRING, '')])

function_VECTOR2 = FunctionDef(
    aIdentifier =    'vector2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.FLOAT1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.FLOAT1 )],
    aFunctionDatas = [])

function_VECTOR3 = FunctionDef(
    aIdentifier =    'vector3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.FLOAT2 ),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.FLOAT2 )],
    aFunctionDatas = [])

function_VECTOR4 = FunctionDef(
    aIdentifier =    'vector4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.FLOAT2|sbsenum.ParamTypeEnum.FLOAT3 ),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.FLOAT2|sbsenum.ParamTypeEnum.FLOAT3 )],
    aFunctionDatas = [])

function_SWIZZLE1 = FunctionDef(
    aIdentifier =    'swizzle1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.FLOAT )],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE1, sbsenum.ParamTypeEnum.INTEGER1, '')])

function_SWIZZLE2 = FunctionDef(
    aIdentifier =    'swizzle2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.FLOAT)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE2, sbsenum.ParamTypeEnum.INTEGER2, '')])

function_SWIZZLE3 = FunctionDef(
    aIdentifier =    'swizzle3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.FLOAT)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE3, sbsenum.ParamTypeEnum.INTEGER3, '')])

function_SWIZZLE4 = FunctionDef(
    aIdentifier =    'swizzle4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.FLOAT)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE4, sbsenum.ParamTypeEnum.INTEGER4, '')])

function_VECTOR_INT2 = FunctionDef(
    aIdentifier =    'ivector2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.INTEGER1),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.INTEGER1)],
    aFunctionDatas = [])

function_VECTOR_INT3 = FunctionDef(
    aIdentifier =    'ivector3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.INTEGER1|sbsenum.ParamTypeEnum.INTEGER2 ),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.INTEGER1|sbsenum.ParamTypeEnum.INTEGER2 )],
    aFunctionDatas = [])

function_VECTOR_INT4 = FunctionDef(
    aIdentifier =    'ivector4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_IN,   sbsenum.ParamTypeEnum.INTEGER1|sbsenum.ParamTypeEnum.INTEGER2|sbsenum.ParamTypeEnum.INTEGER3 ),
                      FunctionInput(sbsenum.FunctionInputEnum.COMPONENTS_LAST, sbsenum.ParamTypeEnum.INTEGER1|sbsenum.ParamTypeEnum.INTEGER2|sbsenum.ParamTypeEnum.INTEGER3 )],
    aFunctionDatas = [])

function_SWIZZLE_INT1 = FunctionDef(
    aIdentifier =    'iswizzle1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.INTEGER)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE_INT1, sbsenum.ParamTypeEnum.INTEGER1, '')])

function_SWIZZLE_INT2 = FunctionDef(
    aIdentifier =    'iswizzle2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.INTEGER)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE_INT2, sbsenum.ParamTypeEnum.INTEGER2, '')])

function_SWIZZLE_INT3 = FunctionDef(
    aIdentifier =    'iswizzle3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.INTEGER)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE_INT3, sbsenum.ParamTypeEnum.INTEGER3, '')])

function_SWIZZLE_INT4 = FunctionDef(
    aIdentifier =    'iswizzle4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VECTOR, sbsenum.TypeMasksEnum.INTEGER)],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SWIZZLE_INT4, sbsenum.ParamTypeEnum.INTEGER4, '')])

function_TO_INT = FunctionDef(
    aIdentifier =    'toint1',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.FLOAT1)],
    aFunctionDatas = [])

function_TO_INT2 = FunctionDef(
    aIdentifier =    'toint2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.FLOAT2)],
    aFunctionDatas = [])

function_TO_INT3 = FunctionDef(
    aIdentifier =    'toint3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.FLOAT3)],
    aFunctionDatas = [])

function_TO_INT4 = FunctionDef(
    aIdentifier =    'toint4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.INTEGER4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.FLOAT4)],
    aFunctionDatas = [])

function_TO_FLOAT = FunctionDef(
    aIdentifier =    'tofloat',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.INTEGER1)],
    aFunctionDatas = [])

function_TO_FLOAT2 = FunctionDef(
    aIdentifier =    'tofloat2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.INTEGER2)],
    aFunctionDatas = [])

function_TO_FLOAT3 = FunctionDef(
    aIdentifier =    'tofloat3',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT3)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.INTEGER3)],
    aFunctionDatas = [])

function_TO_FLOAT4 = FunctionDef(
    aIdentifier =    'tofloat4',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.VALUE, sbsenum.ParamTypeEnum.INTEGER4)],
    aFunctionDatas = [])

function_ADD = FunctionDef(
    aIdentifier =    'add',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_SUB = FunctionDef(
    aIdentifier =    'sub',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_MUL = FunctionDef(
    aIdentifier =    'mul',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_MUL_SCALAR = FunctionDef(
    aIdentifier =    'mulscalar',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.SCALAR, sbsenum.ParamTypeEnum.FLOAT1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT2|sbsenum.ParamTypeEnum.FLOAT3|sbsenum.ParamTypeEnum.FLOAT4)


function_DIV = FunctionDef(
    aIdentifier =    'div',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_NEG = FunctionDef(
    aIdentifier =    'neg',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_MOD = FunctionDef(
    aIdentifier =    'mod',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)


function_DOT = FunctionDef(
    aIdentifier =    'dot',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT2|sbsenum.ParamTypeEnum.FLOAT3|sbsenum.ParamTypeEnum.FLOAT4)

function_CROSS = FunctionDef(
    aIdentifier =    'cross',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT2|sbsenum.ParamTypeEnum.FLOAT3|sbsenum.ParamTypeEnum.FLOAT4)

function_AND = FunctionDef(
    aIdentifier =    'and',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.BOOLEAN),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.BOOLEAN)],
    aFunctionDatas = [])

function_OR = FunctionDef(
    aIdentifier =    'or',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.BOOLEAN),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.BOOLEAN)],
    aFunctionDatas = [])

function_NOT = FunctionDef(
    aIdentifier =    'not',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.BOOLEAN)],
    aFunctionDatas = [])

function_EQ = FunctionDef(
    aIdentifier =    'eq',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_NOT_EQ = FunctionDef(
    aIdentifier =    'noteq',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_GREATER = FunctionDef(
    aIdentifier =    'gt',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_GREATER_EQUAL= FunctionDef(
    aIdentifier =    'gteq',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_LOWER = FunctionDef(
    aIdentifier =    'lr',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_LOWER_EQUAL = FunctionDef(
    aIdentifier =    'lreq',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.BOOLEAN)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.ParamTypeEnum.FLOAT1|sbsenum.ParamTypeEnum.INTEGER1)

function_ABS = FunctionDef(
    aIdentifier =    'abs',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_FLOOR = FunctionDef(
    aIdentifier =    'floor',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_CEIL = FunctionDef(
    aIdentifier =    'ceil',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =    sbsenum.TypeMasksEnum.FLOAT)

function_COS = FunctionDef(
    aIdentifier =    'cos',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =    sbsenum.TypeMasksEnum.FLOAT)

function_SIN = FunctionDef(
    aIdentifier =    'sin',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_SQRT = FunctionDef(
    aIdentifier =    'sqrt',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_LOG = FunctionDef(
    aIdentifier =    'log',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_LOG2 = FunctionDef(
    aIdentifier =    'log2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_EXP = FunctionDef(
    aIdentifier =    'exp',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_POW2 = FunctionDef(
    aIdentifier =    'pow2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_TAN = FunctionDef(
    aIdentifier =    'tan',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_ATAN2 = FunctionDef(
    aIdentifier =    'atan2',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.FLOAT2 )],
    aFunctionDatas = [])

function_CARTESIAN = FunctionDef(
    aIdentifier =    'cartesian',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT2)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.RHO,   sbsenum.ParamTypeEnum.FLOAT1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.THETA, sbsenum.ParamTypeEnum.FLOAT1 )],
    aFunctionDatas = [])

function_LERP = FunctionDef(
    aIdentifier =    'lerp',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.X, sbsenum.ParamTypeEnum.FLOAT1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT)

function_MIN = FunctionDef(
    aIdentifier =    'min',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_MAX = FunctionDef(
    aIdentifier =    'max',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.TEMPLATE1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.TEMPLATE1 ),
                      FunctionInput(sbsenum.FunctionInputEnum.B, sbsenum.ParamTypeEnum.TEMPLATE1 )],
    aFunctionDatas = [],
    aTemplate1 =     sbsenum.TypeMasksEnum.FLOAT|sbsenum.TypeMasksEnum.INTEGER)

function_RAND = FunctionDef(
    aIdentifier =    'rand',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.A, sbsenum.ParamTypeEnum.FLOAT1 )],
    aFunctionDatas = [])

function_SAMPLE_LUM = FunctionDef(
    aIdentifier =    'samplelum',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.POS, sbsenum.ParamTypeEnum.FLOAT2 )],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SAMPLE_LUM, sbsenum.ParamTypeEnum.INTEGER2, '0 0'  )])

function_SAMPLE_COL = FunctionDef(
    aIdentifier =    'samplecol',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT4)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.POS, sbsenum.ParamTypeEnum.FLOAT2 )],
    aFunctionDatas = [FunctionParam(sbsenum.FunctionEnum.SAMPLE_COL, sbsenum.ParamTypeEnum.INTEGER2, '0 0'  )])

function_PASSTHROUGH = FunctionDef(
    aIdentifier =    'passthrough',
    aOutputs =       [FunctionOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.DUMMY_TYPE)],
    aInputs =        [FunctionInput(sbsenum.FunctionInputEnum.INPUT, sbsenum.ParamTypeEnum.DUMMY_TYPE)])

doc_module_attributes(sys.modules[__name__])