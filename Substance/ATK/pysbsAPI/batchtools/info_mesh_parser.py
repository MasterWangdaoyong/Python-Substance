from pysbs import python_helpers

"""
Parser for mesh info stdout.
Exemple of use:
info = get_info_from_mesh("/home/colin/sandbox/R2D2/mesh/R2D2.fbx")
sub_meshes = extract_block(info, InfoBlockEnum.Submesh)
labels = [get_property_value(sub, InfoPropertyEnum.Label, InfoPropertyEnum.Color) for sub in sub_meshes]
>>> print(labels)
[{'Submesh "chrome"': {'Label': 'chrome', 'Color': '(86, 86, 86, 255)'}}, ...]
"""


class InfoBlockEnum:
    Entity,\
    BoundingBox,\
    Location,\
    Mesh,\
    UV,\
    Submesh = range(6)


InfoBlockValues = {InfoBlockEnum.Entity: "Entity",
                   InfoBlockEnum.BoundingBox: "Bounding box",
                   InfoBlockEnum.Location: "Location",
                   InfoBlockEnum.Mesh: "Mesh",
                   InfoBlockEnum.UV: "UV",
                   InfoBlockEnum.Submesh: "Submesh"}


InfoBlockToken = {InfoBlockEnum.Entity: 2*" ",
                   InfoBlockEnum.BoundingBox: 4*" ",
                   InfoBlockEnum.Location: 4*" ",
                   InfoBlockEnum.Mesh: 4*" ",
                   InfoBlockEnum.UV: 6*" ",
                   InfoBlockEnum.Submesh: 6*" "}


class InfoPropertyEnum:
    Label, \
    Color, \
    Triangles, \
    Vertices, \
    Name, \
    BoundingBox, \
    LocalTransform, \
    GlobalTransform, \
    Size, \
    Center, \
    MinimalPoint, \
    MaximalPoint, \
    Uv, \
    Udim, \
    NumberPoints, \
    ContainedUnitSquare, \
    Enabled = range(17)


InfoPropertyValues = {InfoPropertyEnum.Label: "Label",
                      InfoPropertyEnum.Color: "Color",
                      InfoPropertyEnum.Triangles: "Number of triangles",
                      InfoPropertyEnum.Vertices: "Number of vertices",
                      InfoPropertyEnum.Name: "Name",
                      InfoPropertyEnum.BoundingBox: "Bounding box",
                      InfoPropertyEnum.LocalTransform: "Local transformation",
                      InfoPropertyEnum.GlobalTransform: "Global transformation",
                      InfoPropertyEnum.Size: "Size",
                      InfoPropertyEnum.Center: "Center",
                      InfoPropertyEnum.MinimalPoint: "Minimal point",
                      InfoPropertyEnum.MaximalPoint: "Maximal point",
                      InfoPropertyEnum.Enabled: "Enabled",
                      InfoPropertyEnum.Uv: "UV tiles",
                      InfoPropertyEnum.Udim: "Udim tiles",
                      InfoPropertyEnum.NumberPoints: "Number of points",
                      InfoPropertyEnum.ContainedUnitSquare: "Contained within unit square",}


def leading_space(line):
    return len(line) - len(line.lstrip(' '))


def prepare_property_value(line):
    if ":" in line:
        return line.split(":")[1].strip()
    else:
        if len(line.split(" ")) > 1:
            return line.split(" ")[1].strip()
        else:
            return ""


def get_property_values(block, *properties_enum):
    """
    extract properties from a block
    :param block:
    :param properties_enum:
    :return:
    """
    if not block:
        return {}
    if isinstance(block, (list, tuple)):
        raise TypeError("First arg, block, must not be an iterator.")
    lead_name = list(block.keys())[0]
    lines = block[lead_name].split("\n")
    data = {lead_name: {}}
    while lines:
        line = lines.pop(0)
        for property_enum in properties_enum:
            property_name = InfoPropertyValues[property_enum]
            if line.strip().startswith(property_name):
                if data[lead_name].get(property_name):
                    data[lead_name][property_name].append(prepare_property_value(line.strip()))
                else:
                    data[lead_name][property_name] = [prepare_property_value(line.strip())]
                continue
    return data


def get_first_value(prop, name):
    if prop:
        if prop.values():
            if isinstance(name, int):
                name = InfoPropertyValues[name]
            if list(prop.values())[0].get(name):
                return list(prop.values())[0].get(name)[0]
    return None


def extract_block(text, token):
    """
    extract data block from a given token
    :param text: mesh info
    :param token: InfoBlockEnum
    :return:
    """
    if isinstance(text, dict):
        lead_name = list(text.keys())[0]
        text = text[lead_name]
    token_name = InfoBlockValues[token]
    token = InfoBlockToken[token]
    block = list()
    token_open = False
    lines = text.split("\n")
    data = list()
    lead_line = ''
    while lines:
        line = lines.pop(0)
        if line.strip().startswith(token_name) and not token_open:
            data.append(line)
            lead_line = line
            token_open = True
            continue
        if token_open:
            if len(token) >= leading_space(line) or len(lines) == 0:
                if len(lines) == 0:
                    data.append(line)
                if token_name in line:
                    lines.insert(0, line)
                block.append({lead_line.strip(): "\n".join(data)})
                token_open = False
                lead_line = ''
                data = list()
                continue
            data.append(line)
    return block
