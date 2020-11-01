"""
Example of usage with SbsRenderOutputHandler (:ref:`ref-to-output_handlers`):

.. code-block:: python

    out = batchtools.sbsrender_render("output.sbsar", output_handler=True)
    # print results
    print("out.output", out.output)
    for graph in out.get_results():
        print("graph.identifier", graph.identifier)
        for output in graph.outputs:
            print("output.identifier", output.identifier, type(output.identifier))
            print("output.label", output.label, type(output.label))
            print("output.type", output.type, type(output.type))
            print("output.uid", output.uid, type(output.uid))
            print("output.usages", output.usages, type(output.usages))
            print("output.value", output.value, type(output.value))
    print("rendering Finish")


"""

class SbsRenderGraphStruct(object):
    def __init__(self, identifier='', outputs=None):
        """
        Structure that contains graph info and the list of outputs objects.

        :param identifier: graph's identifier
        :param outputs: outputs, list of :class:`.SbsRenderOutputStruct`
        """
        super(SbsRenderGraphStruct, self).__init__()
        self.identifier = identifier
        self.outputs = outputs or []


class SbsRenderOutputStruct(object):
    """
    Depend of :class:`.SbsRenderOutputHandler` .
    Simple structure of the graph's output.
    To get an object instead of a dict.

    :param identifier: output's identifier
    :param label: output's label
    :param type: output's type
    :param uid: output's uid
    :param usages: output's usages
    :param value: output's value can be string or int or float
    """
    def __init__(self, identifier='', label='', type='', uid=0, usages=None, value=None):
        super(SbsRenderOutputStruct, self).__init__()
        self.identifier = identifier
        self.label = label
        self.type = type
        self.uid = uid
        self.usages = usages or []
        self.value = value
