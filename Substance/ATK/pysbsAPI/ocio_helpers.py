import os
import re


def getColorSpaces(ocio_config):
    """
    Parse the config.ocio file to get a list of available colorspaces.
    :param ocio_config: file path of config.ocio
    :type ocio_config: str
    :return: list<str> of colorspaces
    """
    colorspaces = []
    if not ocio_config or not os.path.isfile(ocio_config):
        return colorspaces
    pattern = re.compile(r"\-\ \!\<ColorSpace\>[\r\n]+([^\r\n]+)")
    with open(ocio_config, 'r') as ocio:
        raw_colorspaces = re.findall(pattern, ocio.read())
        for raw_colorspace in raw_colorspaces:
            colorspaces.append(raw_colorspace.split("name:")[-1].strip())
    return colorspaces

