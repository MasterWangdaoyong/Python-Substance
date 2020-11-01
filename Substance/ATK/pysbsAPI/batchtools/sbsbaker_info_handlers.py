"""
Example of usage with SbsBakerInfoOutputHandler (:ref:`ref-to-output_handlers`):

.. code-block:: python

    # call a sbsbaker_info with the kwarg output_handler=True to get an OutputHandler instead of Popen
    # the OutputHandler will stop the interpreter during the batchtool process exactly like Popen.wait()
    out = batchtools.sbsbaker_info('foo.fbx', output_handler=True)
    print(out)
    # <pysbs.batchtools.output_handlers.SbsBakerInfoOutputHandler object at 0x7f8808fe1c50>
    # to get the result use get_results, an OutputHandler's common method
    results = out.get_results()
    print(results)
    # [<pysbs.batchtools.sbsbaker_info_handlers.SbsBakerInfoEntityStruct object at 0x7f7757881c10>, <pysbs.batchtools.sbsbaker_info_handlers.SbsBakerInfoEntityStruct object at 0x7f7757881e10>]
    # SbsBakerInfoOutputHandler.get_results() return a list of SbsBakerInfoEntityStruct. Follow the doc to get more details of SbsBakerInfoEntityStruct
    # as mush as possible each member type is converted in a python type.
    for entity in results:
        # some examples of its different members
        print(entity.label)
        for mesh in entity.meshes:
            print(mesh.vertices_number)
            for uv in mesh.uvs:
                print(uv.udim_tiles)
            for subpart in mesh.submeshes:
                print(subpart.color)
    # it become easy to retrieve all the udims or uv tiles:
    all_udims = set([udim for entity in out for mesh in entity.meshes for uv in mesh.uvs for udim in uv.udim_tiles])

    # an other OutputHandler common method is dump() to write the output in a stream IO (file)
    with open("dumped_file.ext", 'w') as f:
        out.dump(f)

"""

from pysbs import python_helpers
from pysbs.api_decorators import doc_inherit

@doc_inherit
class SbsBakerInfoEntityStruct(object):
    """
    Entity is the higher structure of sbsbaker info.  It defined an object in the scene.
    SbsBakeInfoOutputHandler info return a list of SbsBakerInfoEntityStruct instance.
    Each arguments is accessible with attribute members.

    :param label: the name of the object
    :param enabled: if the object is enabled
    :param bounding_box: bounding box info handled by :class:`.SbsBakerInfoBboxStruct`.
    :param location: location info handled by :class:`.SbsBakerInfoLocStruct`.
    :param meshes: info of each attached object's mesh handled by :class:`.SbsBakerInfoMeshStruct`.
    """
    def __init__(self, label='', enabled=True, bounding_box=None, location=None, meshes=None):
        super(SbsBakerInfoEntityStruct, self).__init__()
        self.label = label
        self._enabled = False if enabled == '0' else True
        self.bounding_box = bounding_box
        self.location = location
        self.meshes = meshes or []

    @property
    def enabled(self):
        return self.enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = False if value == '0' else True


@doc_inherit
class SbsBakerInfoBboxStruct(object):
    """
    Bbox handles bounding box info of an object, member of :class:`.SbsBakerInfoEntityStruct`.

    :param minimal_point: the smallest point of the box
    :param maximal_point: the highest point of the box
    :param center: the center of the box
    :param size: the size of the box
    """
    def __init__(self, minimal_point=tuple(), maximal_point=tuple(), center=tuple(), size=tuple()):
        self.minimal_point = python_helpers.evalStr(minimal_point)
        self.maximal_point = python_helpers.evalStr(maximal_point)
        self.center = python_helpers.evalStr(center)
        self.size = python_helpers.evalStr(size)


@doc_inherit
class SbsBakerInfoLocStruct(object):
    """
    Loc handles location info of an object, member of :class:`.SbsBakerInfoEntityStruct`.
    Warning, the values is not relevant with obj format.

    :param local_transformation: local transformation matrix
    :param global_transformation: global transformation matrix
    """
    def __init__(self, local_transformation, global_transformation):
        self.local_transformation = self._convert_str_value(local_transformation)
        self.global_transformation = self._convert_str_value(global_transformation)

    @staticmethod
    def _convert_str_value(value):
        return tuple((python_helpers.evalStr("(" + v + ")") for v in value[1:-1].split(";")))


@doc_inherit
class SbsBakerInfoMeshStruct(object):
    """
    Mesh handles mesh info part of an object, member of :class:`.SbsBakerInfoEntityStruct`.

    :param label: the name of the mesh part
    :param vertices_number: mesh's vertices number
    :param uv_info: uv info handled by SbsBakerInfoUvStruct
    :param sub_meshes: sub part of a mesh, usually defined by a material assignation or a shader group
    """
    def __init__(self, label='', vertices_number=0, uvs=None, submeshes=None):
        super(SbsBakerInfoMeshStruct, self).__init__()
        self.label = label
        self.vertices_number = python_helpers.evalStr(vertices_number)
        self.uvs = uvs or []
        self.submeshes = submeshes or []


@doc_inherit
class SbsBakerInfoUvStruct(object):
    """
    Uv handles UV info for each mesh's uv sets, member of :class:`.SbsBakerInfoMeshStruct`.

    :param is_in_unit_square: if all the uvs is in the 0-1 space
    :param points_number: points number
    :param uv_tiles: uv tiles where points are present (could be several)
    :param udim_tiles: udim tiles where points are present (could be several)
    """
    def __init__(self, is_in_unit_square='1', points_number=0, uv_tiles='', udim_tiles=''):
        self.is_in_unit_square = False if is_in_unit_square == '0' else True
        self.points_number = points_number
        self._uv_tiles = uv_tiles.split(" ")
        self._udim_tiles = udim_tiles.split(" ")

    @property
    def uv_tiles(self):
        return self._uv_tiles

    @uv_tiles.setter
    def uv_tiles(self, value):
        self._uv_tiles = value.split(" ")

    @property
    def udim_tiles(self):
        return self._udim_tiles

    @udim_tiles.setter
    def udim_tiles(self, value):
        self._udim_tiles = value.split(" ")


@doc_inherit
class SbsBakerInfoSubmeshStruct(object):
    """
    Submesh handles submesh's material info for each mesh's submesh, member of :class:`.SbsBakerInfoMeshStruct`.

    :param label: material name
    :param color: color assignation
    :param triangles_number: triangles number present in this submesh
    """
    def __init__(self, label='', color='', triangles_number=0):
        super(SbsBakerInfoSubmeshStruct, self).__init__()
        self.label = label
        self.color = self._convert_str_value(color)
        self.triangles_number = triangles_number

    @staticmethod
    def _convert_str_value(value):
        if value:
            sp = value.split("(")
            if sp:
                value = "({0}".format(sp[1]).replace("nan", "0")
                return python_helpers.evalStr(value)


