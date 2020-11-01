# coding: utf-8
"""
Module **mdlenum** provides all the enumeration used in Pysbs related to MDL graphs.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_source_code_enum

@doc_source_code_enum
class MDLImplementationKindEnum:
    """
    Enumeration of the kind of MDL node implementation available for a :class:`.MDLImplementation`
    """
    CONSTANT           ,\
    SELECTOR           ,\
    MDL_INSTANCE       ,\
    MDL_GRAPH_INSTANCE ,\
    SBS_INSTANCE       ,\
    PASSTHROUGH        ,\
    = range(6)

@doc_source_code_enum
class MDLAnnotationEnum:
    """
    Enumeration of the annotations used in a MDL graph.
    """
    AUTHOR              ,\
    CONTRIBUTOR         ,\
    COPYRIGHT           ,\
    DESCRIPTION         ,\
    DISPLAY_NAME        ,\
    GAMMA_TYPE          ,\
    KEYWORDS            ,\
    IN_GROUP            ,\
    HIDDEN              ,\
    SAMPLER_USAGE       ,\
    SOFT_RANGE          ,\
    HARD_RANGE          ,\
    VISIBLE_BY_DEFAULT  ,\
    = range(13)

@doc_source_code_enum
class MDLTypeDefKindEnum:
    """
    Enumeration of the kind of mdl types
    """
    UNKNOWN         ,\
    ARRAY           ,\
    ATOMIC          ,\
    BSDF_MEASURE    ,\
    CALL            ,\
    COLOR           ,\
    ENUM            ,\
    LIGHT_PROFILE   ,\
    MATRIX          ,\
    PARAM_REFERENCE ,\
    RESOURCE        ,\
    REFERENCE       ,\
    STRUCT          ,\
    TEXTURE         ,\
    VECTOR          ,\
    = range(15)

@doc_source_code_enum
class MDLTypeModifierEnum:
    """
    Enumeration of the type modifier available
    """
    UNIFORM ,\
    VARYING ,\
    AUTO    ,\
    = range(3)

@doc_source_code_enum
class MDLPredefTypes:
    """
    Enumeration of some predefined mdl type
    """
    CALL        ,\
    COLOR       ,\
    COLOR_LAYER ,\
    FLOAT       ,\
    FLOAT3      ,\
    STRING      ,\
    MATERIAL    ,\
    = range(7)

@doc_source_code_enum
class MDLGraphTemplateEnum:
    """
    Enumeration of the MDL Graph templates available in Substance Designer
    """
    AXF_2_PBR_METALLIC_ROUGHNESS    ,\
    AXF_2_PBR_SPECULAR_GLOSSINESS   ,\
    DIELECTRIC                      ,\
    DIELECTRIC_IOR                  ,\
    EMPTY                           ,\
    METALLIC                        ,\
    METALLIC_ANISOTROPIC            ,\
    PHYSICALLY_METALLIC_ROUGHNESS   ,\
    PHYSICALLY_SPECULAR_GLOSSINESS  ,\
    TRANSLUCENT                     ,\
    TRANSPARENT                     ,\
    = range(11)
