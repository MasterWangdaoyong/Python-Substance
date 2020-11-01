# coding: utf-8
"""
Module **mdldictionaries** provides the dictionaries that give the mapping between the enumerations in :mod:`.mdlenum`
and the corresponding string identifier used by Substance Designer.

    * **Dictionaries:**
        * __dict_MDLAnnotationPath: dictionary relative to :class:`.MDLAnnotationEnum`
        * __dict_MDLPredefTypes: dictionary of predefined MDL types, relative to :class:`.MDLPredefTypes`
        * __dict_MDLTypeDefKind: dictionary of MDL type kind, relative to :class:`.MDLTypeDefKindEnum`
        * __dict_MDLTypeModifierKind: dictionary of type modifier, relative to :class:`.MDLTypeModifierEnum`
        * __dict_MDLGraphTemplate: dictionary relative to :class:`.MDLGraphTemplateEnum`
"""

from __future__ import unicode_literals
import sys

from pysbs.api_decorators import doc_module_attributes, handle_exceptions, checkFirstParamIsAString
from . import mdlenum

# MDL Annotation dictionary
__dict_MDLAnnotationPath = {
    mdlenum.MDLAnnotationEnum.AUTHOR                  : 'mdl::anno::author(string)',
    mdlenum.MDLAnnotationEnum.CONTRIBUTOR             : 'mdl::anno::contributor(string)',
    mdlenum.MDLAnnotationEnum.COPYRIGHT               : 'mdl::anno::copyright_notice(string)',
    mdlenum.MDLAnnotationEnum.DESCRIPTION             : 'mdl::anno::description(string)',
    mdlenum.MDLAnnotationEnum.DISPLAY_NAME            : 'mdl::anno::display_name(string)',
    mdlenum.MDLAnnotationEnum.GAMMA_TYPE              : 'mdl::alg::base::annotations::gamma_type(mdl::tex::gamma_mode)',
    mdlenum.MDLAnnotationEnum.KEYWORDS                : 'mdl::anno::key_words(string[])',
    mdlenum.MDLAnnotationEnum.IN_GROUP                : 'mdl::anno::in_group(string,string,string)',
    mdlenum.MDLAnnotationEnum.HIDDEN                  : 'mdl::anno::hidden()',
    mdlenum.MDLAnnotationEnum.SAMPLER_USAGE           : 'mdl::anno::usage(string)',
    mdlenum.MDLAnnotationEnum.SOFT_RANGE              : 'mdl::anno::soft_range(float,float)',
    mdlenum.MDLAnnotationEnum.HARD_RANGE              : 'mdl::anno::hard_range(float,float)',
    mdlenum.MDLAnnotationEnum.VISIBLE_BY_DEFAULT      : 'mdl::alg::base::annotations::visible_by_default(bool)'
}

# MDL Predefined types dictionary
__dict_MDLPredefTypes = {
    mdlenum.MDLPredefTypes.CALL         : 'mdl::call',
    mdlenum.MDLPredefTypes.COLOR        : 'mdl::color',
    mdlenum.MDLPredefTypes.COLOR_LAYER  : 'mdl::color_layer',
    mdlenum.MDLPredefTypes.FLOAT        : 'mdl::float',
    mdlenum.MDLPredefTypes.FLOAT3       : 'mdl::float3',
    mdlenum.MDLPredefTypes.STRING       : 'mdl::string',
    mdlenum.MDLPredefTypes.MATERIAL     : 'mdl::material'
}

# MDL types kind dictionary
__dict_MDLTypeDefKind = {
    mdlenum.MDLTypeDefKindEnum.UNKNOWN              : 'unknown',
    mdlenum.MDLTypeDefKindEnum.ARRAY                : 'array',
    mdlenum.MDLTypeDefKindEnum.ATOMIC               : 'atomic',
    mdlenum.MDLTypeDefKindEnum.BSDF_MEASURE         : 'bsdf_measurement',
    mdlenum.MDLTypeDefKindEnum.CALL                 : 'call',
    mdlenum.MDLTypeDefKindEnum.COLOR                : 'color',
    mdlenum.MDLTypeDefKindEnum.ENUM                 : 'enum',
    mdlenum.MDLTypeDefKindEnum.LIGHT_PROFILE        : 'light_profile',
    mdlenum.MDLTypeDefKindEnum.MATRIX               : 'matrix',
    mdlenum.MDLTypeDefKindEnum.PARAM_REFERENCE      : 'param_reference',
    mdlenum.MDLTypeDefKindEnum.RESOURCE             : 'resource',
    mdlenum.MDLTypeDefKindEnum.REFERENCE            : 'reference',
    mdlenum.MDLTypeDefKindEnum.STRUCT               : 'struct',
    mdlenum.MDLTypeDefKindEnum.TEXTURE              : 'texture',
    mdlenum.MDLTypeDefKindEnum.VECTOR               : 'vector'
}

# MDL type modifiers dictionary
__dict_MDLTypeModifierKind = {
    mdlenum.MDLTypeModifierEnum.UNIFORM : 'uniform',
    mdlenum.MDLTypeModifierEnum.VARYING : 'varying',
    mdlenum.MDLTypeModifierEnum.AUTO    : 'auto'
}

# MDL Graph templates dictionary
__dict_MDLGraphTemplate = {
    mdlenum.MDLGraphTemplateEnum.AXF_2_PBR_METALLIC_ROUGHNESS   : 'sbs://../templates/mdl_axf_to_pbr_metallic_roughness.sbs/mdl_axf_to_pbr_metallic_roughness'        ,
    mdlenum.MDLGraphTemplateEnum.AXF_2_PBR_SPECULAR_GLOSSINESS  : 'sbs://../templates/mdl_axf_to_pbr_specular_glossiness.sbs/mdl_axf_to_pbr_specular_glossiness'      ,
    mdlenum.MDLGraphTemplateEnum.EMPTY                          : 'sbs://../templates/mdl_empty.sbs/empty_mdl_graph'                                                  ,
    mdlenum.MDLGraphTemplateEnum.DIELECTRIC                     : 'sbs://../templates/mdl_dielectric.sbs/dielectric_mdl_graph'                                        ,
    mdlenum.MDLGraphTemplateEnum.DIELECTRIC_IOR                 : 'sbs://../templates/mdl_dielectric_ior.sbs/dielectric_ior_mdl_graph'                                ,
    mdlenum.MDLGraphTemplateEnum.METALLIC                       : 'sbs://../templates/mdl_metallic.sbs/metallic_mdl_graph'                                            ,
    mdlenum.MDLGraphTemplateEnum.METALLIC_ANISOTROPIC           : 'sbs://../templates/mdl_metallic_anisotropic.sbs/metallic_anisotropic_mdl_graph'                    ,
    mdlenum.MDLGraphTemplateEnum.PHYSICALLY_METALLIC_ROUGHNESS  : 'sbs://../templates/mdl_physically_metallic_roughness.sbs/physically_metallic_roughness_mdl_graph'  ,
    mdlenum.MDLGraphTemplateEnum.PHYSICALLY_SPECULAR_GLOSSINESS : 'sbs://../templates/mdl_physically_specular_glossiness.sbs/physically_specular_glossiness_mdl_graph',
    mdlenum.MDLGraphTemplateEnum.TRANSLUCENT                    : 'sbs://../templates/mdl_translucent.sbs/translucent_mdl_graph'                                      ,
    mdlenum.MDLGraphTemplateEnum.TRANSPARENT                    : 'sbs://../templates/mdl_transparent.sbs/transparent_mdl_graph'
}


@handle_exceptions()
@checkFirstParamIsAString
def getAnnotationEnum(aAnnotationPath):
    """
    getAnnotationEnum(aAnnotationPath)
    Get the enum value of the given annotation

    :param aAnnotationPath: mdl path of the annotation to get
    :type aAnnotationPath: str
    :return: the annotation as a :class:`.MDLAnnotationEnum`
    """
    return next((key for key, value in __dict_MDLAnnotationPath.items() if value == aAnnotationPath), None)

@handle_exceptions()
def getAnnotationPath(aAnnotation):
    """
    getAnnotationPath(aAnnotation)
    Get the given annotation path

    :param aAnnotation: attribute identifier
    :type aAnnotation: :class:`.MDLAnnotationEnum`
    :return: the annotation path as a string
    """
    return __dict_MDLAnnotationPath[aAnnotation]

@handle_exceptions()
def getMDLPredefTypePath(aType):
    """
    getMDLPredefTypePath(aType)
    Get the mdl path of the given predefined mdl type

    :param aType: type identifier
    :type aType: :class:`.MDLPredefTypes`
    :return: the kind of type as a string
    """
    return __dict_MDLPredefTypes[aType]

@handle_exceptions()
def getMDLTypeDefKind(aType):
    """
    getMDLTypeDefKind(aType)
    Get the name of the given mdl type kind

    :param aType: type identifier
    :type aType: :class:`.MDLTypeDefKindEnum`
    :return: the kind of type as a string
    """
    return __dict_MDLTypeDefKind[aType]

@handle_exceptions()
@checkFirstParamIsAString
def getMDLTypeDefKindEnum(aTypeName):
    """
    getMDLTypeDefKindEnum(aTypeName)
    Get the enum value of the given mdl type kind name

    :param aTypeName: kind of type name
    :type aTypeName: str
    :return: the curve type as a :class:`.ResourceTypeEnum`
    """
    return next((key for key, value in __dict_MDLTypeDefKind.items() if value == aTypeName), None)

@handle_exceptions()
def getMDLGraphTemplatePath(aTemplateEnum):
    """
    getMDLGraphTemplatePath(aTemplateEnum)
    Get the path of the given MDL Graph template

    :param aTemplateEnum: MDL template
    :type aTemplateEnum: :class:`.MDLGraphTemplateEnum`
    :return: the path to the template as a string
    """
    return __dict_MDLGraphTemplate[aTemplateEnum]


doc_module_attributes(sys.modules[__name__])
