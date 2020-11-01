from __future__ import unicode_literals, print_function
import sys
import json

from pysbs.batchtools.sbsrender_render_handlers import SbsRenderGraphStruct, SbsRenderOutputStruct
from pysbs.batchtools import info_mesh_parser
from pysbs.batchtools.sbsbaker_info_handlers import SbsBakerInfoEntityStruct, SbsBakerInfoMeshStruct,\
    SbsBakerInfoSubmeshStruct, SbsBakerInfoUvStruct, SbsBakerInfoLocStruct, SbsBakerInfoBboxStruct
from pysbs.api_decorators import doc_inherit


class OutputProcessHandlerPipeError(Exception):
    def __init__(self, msg):
        super(OutputProcessHandlerPipeError, self).__init__(msg)


@doc_inherit
class OutputProcessHandler(object):
    """
    Base class used by the different batchtool's OutputHandler object.
    It wrapped a Popen process and handle the output stream.
    It stop python interpreter during the time it takes for the process to finish, in same way that Popen.wait() function.
    the OutputProcessHandler but manage the Popen process itself (return of batchtool command).

    :param process: a Popen process, usually come from a batchtool call
    :type process: subprocess.Popen
    :param print_stdout: print the stdout stream
    :type print_stdout: bool
    :param print_stderr: print the stderr stream
    :type print_stderr: bool
    """
    def __init__(self, process, print_stdout=True, print_stderr=True):
        self.process = process
        if self.stdout is None or self.stderr is None:
            raise OutputProcessHandlerPipeError("Process's stdout and stderr are not set with subprocess.PIPE")
        self.raw_stderr = str(self.stderr.read().decode())
        self.raw_stdout = str(self.stdout.read().decode())
        self.print_stderr() if print_stderr else None
        self.print_stdout() if print_stdout else None
        self.stderr.close()
        self.stdout.close()
        self.process.wait()
        self.returncode = self.process.returncode

    def wait(self):
        """
        only here for future retro compatibility, if we move OutputHandler as default return result and avoid error.
        :return:
        """
        pass

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr

    @property
    def output(self):
        """
        return a list<dict> from the raw output data

        :return: dict
        """
        return self.raw_stdout

    def print_stderr(self):
        print(self.raw_stderr, file=sys.stderr)
        sys.stderr.flush()

    def print_stdout(self):
        print(self.raw_stdout, file=sys.stdout)
        sys.stdout.flush()

    def dump(self, iostream):
        """
        Dump the output in an iostream

        :param iostream:
        :return:
        """
        iostream.write(self.output)

    def get_results(self):
        return self.output


@doc_inherit
class SbsRenderOutputHandler(OutputProcessHandler):
    """
    SbsRenderOutputHandler handle the batchtools.sbsrender_render output. It can retrieve the different output data
    like a data formed list<dict> or a dedicated list<object> for each graph data: :class:`.SbsRenderOutputHandlerGraphStruct`

    :param args:
    :param kwargs:
    """
    def __init__(self, *args, **kwargs):
        super(SbsRenderOutputHandler, self).__init__(*args, **kwargs)

    def get_results_as_dict(self):
        """
        Parse output data and return a list of dict

        :return: list<dict>
        """
        return json.loads(self.output)

    def get_results(self):
        """
        Parse output data and return a correspondent objects list

        :return: list<:class:`.SbsRenderOutputHandlerGraphStruct` >
        """
        graphs = []
        for output_data in self.get_results_as_dict():
            graph_obj = SbsRenderGraphStruct(identifier=output_data.get('identifier', ''))
            for output in output_data.get("outputs", []):
                output_object = SbsRenderOutputStruct()
                output_object.__dict__.update(output)
                graph_obj.outputs.append(output_object)
            graphs.append(graph_obj)
        return graphs


@doc_inherit
class SbsBakerInfoOutputHandler(OutputProcessHandler):
    """
    SbsRenderOutputHandler handle the batchtools.sbsrender_render output. It can retrieve the different output data
    like a data formed list<dict> or a dedicated list<object> for each graph data: :class:`.SbsBakerInfoEntityStruct`

    :param args:
    :param kwargs:
    """
    def __init__(self, *args, **kwargs):
        super(SbsBakerInfoOutputHandler, self).__init__(*args, **kwargs)

    def get_results(self):
        """
        Parse output data and return a correspondent objects list

        :return: list<:class:`.SbsBakerInfoEntityStruct`>
        """
        entities = info_mesh_parser.extract_block(self.output, info_mesh_parser.InfoBlockEnum.Entity)
        entities_obj = []
        for entity in entities:
            label = info_mesh_parser.get_first_value(
                info_mesh_parser.get_property_values(entity, info_mesh_parser.InfoPropertyEnum.Label),
                info_mesh_parser.InfoPropertyEnum.Label)
            enabled = info_mesh_parser.get_first_value(
                info_mesh_parser.get_property_values(entity, info_mesh_parser.InfoPropertyEnum.Enabled),
                info_mesh_parser.InfoPropertyEnum.Enabled)
            entity_obj = SbsBakerInfoEntityStruct(label, enabled)
            # bbox
            bounding_box = info_mesh_parser.extract_block(entity, info_mesh_parser.InfoBlockEnum.BoundingBox) or None
            if bounding_box:
                minimal_point = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(bounding_box[0], info_mesh_parser.InfoPropertyEnum.MinimalPoint),
                    info_mesh_parser.InfoPropertyEnum.MinimalPoint)
                maximal_point = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(bounding_box[0], info_mesh_parser.InfoPropertyEnum.MaximalPoint),
                    info_mesh_parser.InfoPropertyEnum.MaximalPoint)
                center = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(bounding_box[0], info_mesh_parser.InfoPropertyEnum.Center),
                    info_mesh_parser.InfoPropertyEnum.Center)
                size = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(bounding_box[0], info_mesh_parser.InfoPropertyEnum.Size),
                    info_mesh_parser.InfoPropertyEnum.Size)
                bounding_box = SbsBakerInfoBboxStruct(minimal_point, maximal_point, center, size)
                entity_obj.bounding_box = bounding_box
            # loc
            loc = info_mesh_parser.extract_block(entity, info_mesh_parser.InfoBlockEnum.Location) or None
            if loc:
                local_transform = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(loc[0], info_mesh_parser.InfoPropertyEnum.LocalTransform),
                    info_mesh_parser.InfoPropertyEnum.LocalTransform)
                global_transform = info_mesh_parser.get_first_value(
                    info_mesh_parser.get_property_values(loc[0], info_mesh_parser.InfoPropertyEnum.GlobalTransform),
                    info_mesh_parser.InfoPropertyEnum.GlobalTransform)
                loc = SbsBakerInfoLocStruct(local_transform, global_transform)
                entity_obj.location = loc
            # mesh
            meshes = info_mesh_parser.extract_block(entity, info_mesh_parser.InfoBlockEnum.Mesh) # or None
            if meshes:
                for mesh in meshes:
                    mesh_label = info_mesh_parser.get_first_value(
                        info_mesh_parser.get_property_values(mesh, info_mesh_parser.InfoPropertyEnum.Name),
                        info_mesh_parser.InfoPropertyEnum.Name)
                    vertices_number = info_mesh_parser.get_first_value(
                        info_mesh_parser.get_property_values(mesh, info_mesh_parser.InfoPropertyEnum.Vertices),
                        info_mesh_parser.InfoPropertyEnum.Vertices)
                    mesh_obj = SbsBakerInfoMeshStruct(mesh_label, vertices_number)
                    # mesh.uv
                    uvs = info_mesh_parser.extract_block(mesh, info_mesh_parser.InfoBlockEnum.UV) or []
                    if uvs:
                        for uv in uvs:
                            in_square = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(uv, info_mesh_parser.InfoPropertyEnum.ContainedUnitSquare),
                                info_mesh_parser.InfoPropertyEnum.ContainedUnitSquare)
                            points_number = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(uv, info_mesh_parser.InfoPropertyEnum.NumberPoints),
                                info_mesh_parser.InfoPropertyEnum.NumberPoints)
                            uv_tiles = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(uv, info_mesh_parser.InfoPropertyEnum.Uv),
                                info_mesh_parser.InfoPropertyEnum.Uv)
                            udim_tiles = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(uv, info_mesh_parser.InfoPropertyEnum.Udim),
                                info_mesh_parser.InfoPropertyEnum.Udim)
                            uv_obj = SbsBakerInfoUvStruct(in_square, points_number, uv_tiles, udim_tiles)
                            mesh_obj.uvs.append(uv_obj)
                    # mesh.submesh
                    submeshes = info_mesh_parser.extract_block(mesh, info_mesh_parser.InfoBlockEnum.Submesh) or []
                    if submeshes:
                        for submesh in submeshes:
                            sub_label = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(submesh, info_mesh_parser.InfoPropertyEnum.Label),
                                info_mesh_parser.InfoPropertyEnum.Label)
                            color = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(submesh, info_mesh_parser.InfoPropertyEnum.Color),
                                info_mesh_parser.InfoPropertyEnum.Color)
                            triangles_number = info_mesh_parser.get_first_value(
                                info_mesh_parser.get_property_values(submesh, info_mesh_parser.InfoPropertyEnum.Triangles),
                                info_mesh_parser.InfoPropertyEnum.Triangles)
                            sub_mesh_obj = SbsBakerInfoSubmeshStruct(sub_label, color, triangles_number)
                            mesh_obj.submeshes.append(sub_mesh_obj)
                    entity_obj.meshes.append(mesh_obj)
            entities_obj.append(entity_obj)
        return entities_obj


