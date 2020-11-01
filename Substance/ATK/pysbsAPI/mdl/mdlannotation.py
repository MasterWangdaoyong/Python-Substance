# coding: utf-8
"""
Module **mdlannotation** provides the definition of the class :class:`.MDLAnnotation`
"""

from __future__ import unicode_literals

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.common_interfaces import SBSObject

from . import MDLOperands


# =======================================================================
@doc_inherit
class MDLAnnotation(SBSObject):
    """
    Class that contains information on a MDL annotation node as defined in a .sbs file

    Members:
        * mPath     (string): path of the graph definition this instance refers to.
        * mOperands (list of :class:`.MDLOperands`, optional): list of parameters available on this node
    """
    def __init__(self,
                 aPath            = '',
                 aOperands        = None):
        super(MDLAnnotation, self).__init__()
        self.mPath     = aPath
        self.mOperands = aOperands

        self.mMembersForEquality = ['mPath',
                                    'mOperands']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPath = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'mdl_path' )
        self.mOperands = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_operands', MDLOperands)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPath, 'mdl_path'     )
        aSBSWriter.writeSBSNode(aXmlNode, self.mOperands,          'mdl_operands' )

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this annotation

        :return: The value of this annotation if defined, as a string or a list of string, None otherwise
        """
        values = self.mOperands.getAllOperandsValue()
        return values if len(values) > 1 else values[0] if values else None

    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue()
        Set the value of this annotation

        :param aValue: The value to set
        :type aValue: str or list of str
        """
        if isinstance(aValue, list):
            for i,item in enumerate(aValue):
                aOperand = self.mOperands.getOperandByIndex(i)
                if aOperand:
                    aOperand.setValue(item)
                else:
                    break
        else:
            aOperand = self.mOperands.getOperandByIndex(0)
            if aOperand:
                aOperand.setValue(aValue)
