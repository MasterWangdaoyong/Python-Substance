# coding: utf-8
"""
Module **sbsfxmapnodes** provides the library of FxMap nodes and their definition (inputs, outputs, parameters):

    * fxmap_ITERATE
    * fxmap_QUADRANT
    * fxmap_SWITCH
"""

from __future__ import unicode_literals
import sys

from pysbs import sbsenum
from pysbs.api_decorators import doc_module_attributes
from .sbslibclasses import FxMapNodeDef,CompNodeOutput,CompNodeInput,CompNodeParam


fxmap_ITERATE = FxMapNodeDef(
    aIdentifier = 'addnode',
    aOutputs =     [CompNodeOutput(sbsenum.OutputEnum.OUTPUT0, sbsenum.ParamTypeEnum.ENTRY_PARAMETER),
                    CompNodeOutput(sbsenum.OutputEnum.OUTPUT1, sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aInputs =      [CompNodeInput(sbsenum.InputEnum.INPUT,     sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aParameters =  [CompNodeParam(sbsenum.CompNodeParamEnum.FX_ITERATIONS,       sbsenum.ParamTypeEnum.INTEGER1, '1' ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_SEED,      sbsenum.ParamTypeEnum.INTEGER1, '0' ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_INHERITED, sbsenum.ParamTypeEnum.BOOLEAN , '1' )])

fxmap_QUADRANT = FxMapNodeDef(
    aIdentifier = 'paramset',
    aOutputs =     [CompNodeOutput(sbsenum.OutputEnum.OUTPUT0, sbsenum.ParamTypeEnum.ENTRY_PARAMETER),
                    CompNodeOutput(sbsenum.OutputEnum.OUTPUT1, sbsenum.ParamTypeEnum.ENTRY_PARAMETER),
                    CompNodeOutput(sbsenum.OutputEnum.OUTPUT2, sbsenum.ParamTypeEnum.ENTRY_PARAMETER),
                    CompNodeOutput(sbsenum.OutputEnum.OUTPUT3, sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aInputs =      [CompNodeInput(sbsenum.InputEnum.INPUT,     sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aParameters =  [CompNodeParam(sbsenum.CompNodeParamEnum.FX_COLOR_LUM,         sbsenum.ParamTypeEnum.FLOAT_VARIANT, '1.0 1.0 1.0 1.0' ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_BRANCH_OFFSET,     sbsenum.ParamTypeEnum.FLOAT2       , '0.0 0.0'         ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_PATTERN_TYPE,      sbsenum.ParamTypeEnum.INTEGER1     , '0'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_PATTERN_OFFSET,    sbsenum.ParamTypeEnum.FLOAT2       , '0.0 0.0'         ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_PATTERN_SIZE,      sbsenum.ParamTypeEnum.FLOAT2       , '1.0 1.0'         ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_PATTERN_ROTATION,  sbsenum.ParamTypeEnum.FLOAT1       , '0.0'             ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_PATTERN_VARIATION, sbsenum.ParamTypeEnum.FLOAT1       , '0.0'             ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_BLENDING_MODE,     sbsenum.ParamTypeEnum.INTEGER1     , '0'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_SEED,       sbsenum.ParamTypeEnum.INTEGER1     , '0'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_INHERITED,  sbsenum.ParamTypeEnum.BOOLEAN      , '1'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_IMAGE_INDEX,       sbsenum.ParamTypeEnum.INTEGER1     , '0'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_IMAGE_ALPHA_PREMUL,sbsenum.ParamTypeEnum.BOOLEAN      , '0'               ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_IMAGE_FILTERING,   sbsenum.ParamTypeEnum.INTEGER1     , '0'               )])

fxmap_SWITCH = FxMapNodeDef(
    aIdentifier = 'markov2',
    aOutputs =     [CompNodeOutput(sbsenum.OutputEnum.OUTPUT0, sbsenum.ParamTypeEnum.ENTRY_PARAMETER),
                    CompNodeOutput(sbsenum.OutputEnum.OUTPUT1, sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aInputs =      [CompNodeInput(sbsenum.InputEnum.INPUT,     sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aParameters =  [CompNodeParam(sbsenum.CompNodeParamEnum.FX_SELECTOR,         sbsenum.ParamTypeEnum.BOOLEAN , '0' ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_SEED,      sbsenum.ParamTypeEnum.INTEGER1, '0' ),
                    CompNodeParam(sbsenum.CompNodeParamEnum.FX_RANDOM_INHERITED, sbsenum.ParamTypeEnum.BOOLEAN , '1' )])

fxmap_PASSTHROUGH = FxMapNodeDef(
    aIdentifier = 'passthrough',
    aOutputs =     [CompNodeOutput(sbsenum.OutputEnum.OUTPUT0, sbsenum.ParamTypeEnum.ENTRY_PARAMETER)],
    aInputs =      [CompNodeInput(sbsenum.InputEnum.INPUT,     sbsenum.ParamTypeEnum.ENTRY_PARAMETER)])


doc_module_attributes(sys.modules[__name__])
