from __future__ import unicode_literals, print_function
import logging
log = logging.getLogger(__name__)
import json
import subprocess
import sys
import re
from multiprocessing import Pool
import copy
import io

from pysbs.context import Context
from pysbs.sbsenum import BatchToolsEnum
from pysbs import python_helpers as helpers
from pysbs.batchtools.output_handlers import OutputProcessHandler, SbsRenderOutputHandler, SbsBakerInfoOutputHandler


def __load_command_info(aBatchTool):
    if aBatchTool not in __batchtools_commands_info:
        try:
            jsoninfo = json.loads(subprocess.check_output(
                [Context.getBatchToolExePath(aBatchTool), "--opt-descr"]
            ).decode("utf-8", errors="ignore"))
        except ValueError as e:
            log.error(e)
            raise e
        # Command with only a single subcommand will return the info of that subcommand, not a list of info.
        # Convert back that info into a list of info (with only that element)
        if type(jsoninfo) == dict:
            jsoninfo = [jsoninfo]
        __batchtools_commands_info[aBatchTool] = jsoninfo
    return __batchtools_commands_info[aBatchTool]


__batchtools_commands_info = {}  # Lazily loaded for each batchtools


def __dash(optname):
    return '--' + optname if len(optname) > 1 else '-' + optname


def __subcommand_info_for(cmd, subcmd):
    if cmd not in __batchtools_commands_info:
        return None
    for subcmd_info in __batchtools_commands_info[cmd]:
        if subcmd_info["name"] == subcmd:
            return subcmd_info
    return None


def __option_info_for(subcmd_info, opt):
    for opt_info in subcmd_info["options"]:
        if opt_info["name"] == opt \
                or ("alternate names" in opt_info and opt in opt_info["alternate names"]):
            return opt_info
    return None


def __check_option_value(name, typename, value):
    if typename == "invalid":
        raise TypeError("{0} expects an invalid type".format(name))
    elif typename == "bool" or typename == "flag":
        value = True if value == "true" else False if value == "false" else value
        if type(value) is not bool:
            raise TypeError("{0} expects a bool (received {1})".format(
                name, type(value)
            ))
    elif typename == "integer" or typename == "non-negative integer":
        if not helpers.isIntOrLong(value):
            raise TypeError("{0} expects an int (received {1})".format(
                name, type(value)
            ))
    elif typename == "non-negative integer":
        if not helpers.isIntOrLong(value):
            raise TypeError("{0} expects an int (received {1})".format(
                name, type(value)
            ))
        if value < 0:
            raise ValueError("{0} expects a non-negative integer (received {1})".format(
                name, value
            ))
    elif typename == "real":
        if type(value) != float:
            raise TypeError("{0} expects a float (received {1})".format(
                name, type(value)
            ))
    elif typename == "character":
        if not helpers.isStringOrUnicode(value):
            raise TypeError("{0} expects a string (received {1})".format(
                name, type(value)
            ))
        if len(value) != 1:
            raise ValueError("{0} expects a string of 1 character (received {1} characters)".format(
                name, len(value)
            ))
    elif typename == "string":
        if not helpers.isStringOrUnicode(value):
            raise TypeError("{0} expects a string (received {1})".format(
                name, type(value)
            ))
    elif typename == "string list":
        if not helpers.isSequence(value) and not helpers.isStringOrUnicode(value):
            raise TypeError("{0} expects a sequence of string or one string (received {1})".format(
                name, type(value)
            ))
        elif helpers.isSequence(value) and not all([helpers.isStringOrUnicode(subvalue) for subvalue in value]):
            raise ValueError("{0} expects a sequence of strings, but some of its items are not strings".format(
                name
            ))
    elif typename == "bytes":
        if type(value) != bytes:
            raise TypeError("{0} expects bytes (received {1})".format(
                name, type(value)
            ))
    elif typename == "url":
        if not helpers.isStringOrUnicode(value):
            raise TypeError("{0} expects a string (received {1})".format(
                name, type(value)
            ))
    elif typename == "integer,integer":
        if not helpers.isSequence(value):
            raise TypeError("{0} expects a sequence (received {1})".format(
                name, type(value)
            ))
        elif len(value) != 2:
            raise ValueError("{0} expects a sequence of exactly 2 elements (received {1} elements)".format(
                name, len(value)
            ))
        elif not helpers.isIntOrLong(value[0]):
            raise ValueError("{0} expects its first element to be an int (received {1})".format(
                name, type(value)
            ))
        elif not helpers.isIntOrLong(value[1]):
            raise ValueError("{0} expects its second element to be an int (received {1})".format(
                name, type(value)
            ))
    elif typename == "real,real":
        if not helpers.isSequence(value):
            raise TypeError("{0} expects a sequence (received {1})".format(
                name, type(value)
            ))
        elif len(value) != 2:
            raise TypeError("{0} expects a sequence of exactly 2 elements (received {1} elements)".format(
                name, len(value)
            ))
        elif type(value[0]) != float:
            raise ValueError("{0} expects its first element to be a float (received {1})".format(
                name, type(value)
            ))
        elif type(value[1]) != float:
            raise ValueError("{0} expects its second element to be a float (received {1})".format(
                name, type(value)
            ))
    elif typename == "user":
        pass
    elif typename == "unknown":
        raise TypeError("{0} expects an unknown type".format(name))


def __option_value_to_option_strings(option_name, typename, value):
    dashed_name = __dash(option_name)
    if typename == "string list":
        if helpers.isStringOrUnicode(value):
            return [dashed_name, helpers.castStr(value)]
        else:
            options = []
            for subvalue in value:
                options.append(dashed_name)
                options.append(helpers.castStr(subvalue))
            return options
    elif typename == "flag":
        return [dashed_name] if value else []
    elif typename == "bool":
        return [dashed_name, helpers.castStr(value).lower()]
    elif typename == "integer,integer" or typename == "real,real":
        return [dashed_name, "{0},{1}".format(*value)]
    else:
        return [dashed_name, helpers.castStr(value)]


def __sbscall(command_number, subcommand, *pargs, **kwargs):
    # initialize global info for this batchtools if needed
    # This is delayed so user has a chance to change default package path with Context.setDefaultPackagePath
    # This is done only for the called tool so the user can use some batchtools despise having some of them that fail.
    global __batchtools_commands_info
    __load_command_info(command_number)

    # check that command and subcommand are valid
    if command_number not in helpers.iterEnum(BatchToolsEnum):
        raise ValueError('Bad value for command, use a value defined in the enumeration sbsenum.BatchToolsEnum')

    subcommand_info = __subcommand_info_for(command_number, subcommand)
    if subcommand_info is None:
        raise ValueError('Bad value for subcommand, use {0} or an empty string'.format(
            ", ".join([info["name"] for info in subcommand_info[command_number] if info["name"] != ""])))

    # basic command line
    called_command = [Context.getBatchToolExePath(command_number)]
    if len(__batchtools_commands_info[command_number]) != 1:
        called_command.append(subcommand)
    called_command += pargs

    # select special option that must be passed to subprocess.Popen
    bufsize_default = 0 if sys.version_info < (3, 0) else -1
    bufsize = kwargs.pop("bufsize", bufsize_default)
    stdin = kwargs.pop("stdin", None)
    stdout = kwargs.pop("stdout", None)
    stderr = kwargs.pop("stderr", None)
    shell = kwargs.pop("shell", False)
    cwd = kwargs.pop("cwd", None)
    env = kwargs.pop("env", None)
    output_handler_obj = kwargs.pop("output_handler_obj", None)
    output_handler = kwargs.pop("output_handler", None)
    universal_newlines = kwargs.pop("universal_newlines", False)
    command_only = kwargs.pop('command_only', False)

    # check and add options for command and subcommand
    if output_handler_obj is None and output_handler:
        raise TypeError('"{command}" "{subcommand}" does not implement an OutputHandler yet,'
                        ' please remove output_handler=True argument.'.format(
            command=Context.getBatchToolExeName(command_number), subcommand=subcommand))
    for option, value in kwargs.items():
        option_name = option.replace("_", "-")
        info = __option_info_for(subcommand_info, option_name)
        if info is None:
            raise TypeError('{0} is not a valid named argument for call "{command}" "{subcommand}"'.format(
                option_name, command=Context.getBatchToolExeName(command_number), subcommand=subcommand))

        typename = info["type"]
        __check_option_value(option_name, typename, value)
        called_command += __option_value_to_option_strings(option_name, typename, value)

    # Print debug
    log.debug("Batchtools call called_command: %s" % called_command)
    log.debug("Batchtools call stdout: %s" % str(stdout))
    log.debug("Batchtools call stderr: %s" % str(stderr))
    log.debug("Batchtools call stdin: %s" % str(stdin))

    # command only
    if command_only:
        return ' '.join(helpers.encodeCommandForSubProcess(called_command))

    # do the call
    # if output_handler override stdout and stderr to be able to read the output from Popen
    if output_handler_obj and issubclass(output_handler_obj, OutputProcessHandler):
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    p = subprocess.Popen(helpers.encodeCommandForSubProcess(called_command),
                                bufsize=bufsize,
                                stdin=stdin,
                                stdout=stdout,
                                stderr=stderr,
                                shell=shell,
                                cwd=cwd,
                                env=env,
                                universal_newlines=universal_newlines)
    # return the OutputHandler object instead of Popen process
    if output_handler_obj and issubclass(output_handler_obj, OutputProcessHandler):
        return output_handler_obj(p)
    return p


def sbsmutator_edit(*pargs, **kwargs):
    """
    Launch process ``sbsmutator edit`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsmutator edit``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsmutator edit --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsmutator edit``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsmutator edit``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.MUTATOR, "edit", *pargs, **kwargs)


def sbsmutator_export(*pargs, **kwargs):
    """
    Launch process ``sbsmutator export`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsmutator export``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsmutator export --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsmutator export``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsmutator export``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.MUTATOR, "export", *pargs, **kwargs)


def sbsmutator_info(*pargs, **kwargs):
    """
    Launch process ``sbsmutator info`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsmutator info``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsmutator info --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsmutator info``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsmutator info``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.MUTATOR, "info", *pargs, **kwargs)


def sbsmutator_instantiate(*pargs, **kwargs):
    """
    Launch process ``sbsmutator instantiate`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsmutator instantiate``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsmutator instantiate --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsmutator instantiate``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsmutator instantiate``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.MUTATOR, "instantiate", *pargs, **kwargs)


def sbscooker(*pargs, **kwargs):
    """
    Launch process ``sbscooker`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbscooker``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbscooker --help-advanced`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbscooker``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbscooker``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.COOKER, "cook", *pargs, **kwargs)


def sbsupdater(*pargs, **kwargs):
    """
    Launch process ``sbsupdater`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsupdater``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsupdater --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsupdater``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsupdater``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.UPDATER, "update", *pargs, **kwargs)


def sbsbaker_ambient_occlusion(*pargs, **kwargs):
    """
    Launch process ``sbsbaker ambient-occlusion`` ..

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker ambient-occlusion``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker ambient-occlusion --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker ambient-occlusion``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker ambient-occlusion``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "ambient-occlusion", *pargs, **kwargs)


def sbsbaker_ambient_occlusion_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker ambient-occlusion-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to
    ``sbsbaker ambient-occlusion-from-mesh``, with dashes ``-`` replaced with underscores ``_`` and with the leading ``--``
    or ``-`` removed.
    Run ``sbsbaker ambient-occlusion-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker ambient-occlusion-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker ambient_occlusion-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "ambient-occlusion-from-mesh", *pargs, **kwargs)


def sbsbaker_bent_normal_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker bent-normal-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to
    ``sbsbaker bent-normal-from-mesh``, with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-``
    removed.
    Run ``sbsbaker bent-normal-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker bent-normal-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker bent-normal-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "bent-normal-from-mesh", *pargs, **kwargs)


def sbsbaker_color_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker color-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker color-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker color-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker color-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker color-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "color-from-mesh", *pargs, **kwargs)


def sbsbaker_curvature(*pargs, **kwargs):
    """
    Launch process ``sbsbaker curvature`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker curvature``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker curvature --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker curvature``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker curvature``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "curvature", *pargs, **kwargs)


def sbsbaker_curvature_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker curvature-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker curvature-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker curvature-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker curvature-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker curvature-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "curvature-from-mesh", *pargs, **kwargs)


def sbsbaker_height_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker height-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker height-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker height-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker height-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker height-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "height-from-mesh", *pargs, **kwargs)


def sbsbaker_normal_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker normal-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker normal-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker normal-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker normal-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker normal-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "normal-from-mesh", *pargs, **kwargs)


def sbsbaker_normal_world_space(*pargs, **kwargs):
    """
    Launch process ``sbsbaker normal-world-space`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker normal-world-space``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker normal-world-space --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker normal-world-space``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker normal-world-space``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "normal-world-space", *pargs, **kwargs)


def sbsbaker_opacity_mask_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker opacity-mask-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to
    ``sbsbaker opacity-mask-from-mesh``, with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-``
    removed.
    Run ``sbsbaker opacity-mask-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker opacity-mask-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker opacity_mask-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "opacity-mask-from-mesh", *pargs, **kwargs)


def sbsbaker_position(*pargs, **kwargs):
    """
    Launch process ``sbsbaker position`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker position``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker position --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker position``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker position``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "position", *pargs, **kwargs)


def sbsbaker_position_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker position-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker position-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker position-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker position-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker position-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "position-from-mesh", *pargs, **kwargs)


def sbsbaker_texture_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker texture-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker texture-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker texture-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker texture-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker texture-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "texture-from-mesh", *pargs, **kwargs)


def sbsbaker_thickness_from_mesh(*pargs, **kwargs):
    """
    Launch process ``sbsbaker thickness-from-mesh`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker thickness-from-mesh``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker thickness-from-mesh --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker thickness-from-mesh``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker thickness-from-mesh``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "thickness-from-mesh", *pargs, **kwargs)


def sbsbaker_uv_map(*pargs, **kwargs):
    """
    Launch process ``sbsbaker uv-map`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker uv-map``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker uv-map --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker uv-map``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker uv-map``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "uv-map", *pargs, **kwargs)


def sbsbaker_world_space_direction(*pargs, **kwargs):
    """
    Launch process ``sbsbaker world-space-direction`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to
    ``sbsbaker world-space-direction``, with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-``
    removed.
    Run ``sbsbaker world-space-direction --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker world-space-direction``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker world-space-direction``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "world-space-direction", *pargs, **kwargs)


def sbsbaker_run(*pargs, **kwargs):
    """
    Launch process ``sbsbaker run`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker run``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker run --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker run``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker run``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.BAKER, "run", *pargs, **kwargs)


def sbsbaker_info(*pargs, **kwargs):
    """
    Launch process ``sbsbaker info`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsbaker info``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsbaker info --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsbaker info``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsbaker info``
    :return: The popen object used to call the command
    """
    if kwargs.pop("output_handler", False):
        kwargs["output_handler_obj"] = SbsBakerInfoOutputHandler
    return __sbscall(BatchToolsEnum.BAKER, "info", *pargs, **kwargs)


def sbsrender_render(*pargs, **kwargs):
    """
    Launch process ``sbsrender render`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsrender render``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsrender render --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsrender render``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsrender render``
    :return: The popen object used to call the command
    """
    if kwargs.pop("output_handler", False):
        kwargs["output_handler_obj"] = SbsRenderOutputHandler
    return __sbscall(BatchToolsEnum.RENDER, "render", *pargs, **kwargs)


def sbsrender_info(*pargs, **kwargs):
    """
    Launch process ``sbsrender info`` with given positional arguments and options.

    The call is done by :class:`subprocess.Popen` from the standard library.
    This function accepts the same keyword arguments.
    The other possible keywords arguments correspond to the possible options to give to ``sbsrender info``,
    with dashes ``-`` replaced with underscores ``_`` and with the leading ``--`` or ``-`` removed.
    Run ``sbsrender info --help`` to see the list of possible options.


    :param pargs: the positional arguments to give to ``sbsrender info``
    :param kwargs: keyword arguments that can be given to :class:`subprocess.Popen` or that correspond to
                   options of ``sbsrender info``
    :return: The popen object used to call the command
    """
    return __sbscall(BatchToolsEnum.RENDER, "info", *pargs, **kwargs)


def sbsbaker_info_get_mesh_info(meshPath):
    """
    Get the list of materials, entities, and number of UV set of the given mesh and return them as a triplet.

    :param meshPath: Path of the mesh to inspect
    :type meshPath: str
    :return: A triplet: [materials],[entities],nb_of_uvset
    """
    sub_process = sbsbaker_info(meshPath, stdout=subprocess.PIPE, hide_bounding_box=True, hide_location=True)
    sub_process.wait()
    output = sub_process.stdout.read().decode()
    sub_process.stdout.close()
    entities = []
    materials = []
    uv_sets = []

    for l in output.split('\n'):
        if l.startswith('      Submesh '):
            material = l[14:-1].strip('"\r')
            if material not in materials:
                materials.append(material)
        elif l.startswith('      UV '):
            uv = l[9:].strip(':\r')
            if uv not in uv_sets:
                uv_sets.append(uv)
        elif l.startswith('  Entity '):
            entity = l[9:-1].strip('":\r')
            if entity not in entities:
                entities.append(entity)

    if not all(str(x) in uv_sets for x in range(len(uv_sets))):
        print('UV set are not as expected, there are UV set indices above the numbers of UV sets')

    return materials,entities,len(uv_sets)


def _run_render(data):
    p = sbsrender_render(data[0], **data[1])
    p.wait()
    return p.returncode


def sbsrender_render_animate(input_sbsar, start=0, end=100, output_name=None, fps=24, animated_parameters=[],
                             cmds_output_stream=None, multi_proc=0, **kwargs):
    """
    Renders an image sequence from an sbsar input using sbsrender.
    It takes a start frame, an end frame and frames per second.
    The sbsrender command line tool will be run once for each frame.

    By default the $time will be generated for each frame based on start, end and fps.
    It is possible to set sbsrender arguments as global frame parameters.

    The `animated_parameters` can be used to tweak other sbsar parameters than $time
    This argument allow to pass a list of pairs of parameter names and functions taking `frame` and `fps` as parameters.
    e.g: animated_parameters=[("input", compute_input)] the value named "input" will be set to the result of
    calling compute_input(frame, fps).
    A lambda can also be used be used, e.g: animated_parameters=[("input", lambda frame, fps: frame / fps)]
    Multiple values can be animated by supplying a list of parameters and functions,
    e.g: animated_parameters=[("input", lambda frame, fps: frame / fps), ("other", a_python_def(frame, fps))]

    If setting multi_proc to a non-zero value the rendering will be multi processed in the specified number
    of processes executing the rendering sequentially frame by frame.

    By providing a path to the argument `cmds_output_path` the sbsrender will not be executed but all
    command lines will be written in the file.
    So it possible for instance to dispatch theses command line through a render farm.

    :param input_sbsar: sbsar path file as input
    :type input_sbsar: str
    :param start: start frame
    :type start: int
    :param end: end frame
    :type end: int
    :param output_name: the name of the ouput files, it must contain a sequence pattern, e.g: ### or %3d for three digit.
    :type output_name: str
    :param fps: frame rate
    :type fps: int
    :param animated_parameters: a pair of parameter name and corresponding function to compute it or a list of such pairs.
    :type animated_parameters: (str, function(fram, fps) or [(str, function(fram, fps)]
    :param cmds_output_stream: stream to write commands to instead of executing them
    :type cmds_output_stream: io.TextIOBase
    :param multi_proc: if greater than 0 the rendering will be parallelize by the multi_proc value.
    :type multi_proc: int
    :param kwargs: other key arguments
    :return: bool, true if all frames succeeded, otherwise false
    """
    # map pool args
    cmds_args_pool = []

    # manage padding name
    re_padding = r"(#+|%[0-9]+d)"
    padding_match = re.search(re_padding, output_name)
    if not padding_match:
        raise TypeError("output path argument must contain a valid frame padding, i.e ### or %3d for three digit.")
    padding_orig = padding_match.groups()[0]
    if "#" in padding_orig:
        padding = "%0{0}d".format(len(padding_orig))
    else:
        padding = padding_orig.replace("%", "%0")
    output_name = output_name.replace(padding_orig, padding)

    # update kwargs cmd and kwargs
    kwargs_cmd = dict(set_value=[])
    if kwargs.get('set_value'):
        if isinstance(kwargs_cmd['set_value'], list):
            kwargs_cmd['set_value'].extend(kwargs_cmd['set_value'])
        else:
            kwargs_cmd['set_value'].append(kwargs_cmd['set_value'])
    try:
        del kwargs['set_value']
    except KeyError:
        pass
    kwargs_cmd.update(kwargs)

    success = True
    # iterate through frames
    for f in range(start, end+1):
        time_value = float(f) / fps
        # remove last $time@
        for i, s_value in enumerate(kwargs_cmd['set_value']):
            if s_value.startswith("$time@"):
                kwargs_cmd['set_value'].pop(i)
        kwargs_cmd['set_value'].append("$time@{0}".format(time_value))
        kwargs_cmd['output_name'] = output_name % (f,)
        animated_parameters = list(animated_parameters) if isinstance(animated_parameters, list) else [animated_parameters]
        for param_name, param_fn in animated_parameters:
            # remove previous value for animated parameter
            for i, s_value in enumerate(kwargs_cmd['set_value']):
                if s_value.startswith("{0}@".format(param_name)):
                    kwargs_cmd['set_value'].pop(i)
            kwargs_cmd['set_value'].append("{0}@{1}".format(param_name, param_fn(f, fps=fps)))
        if cmds_output_stream:
            cmds_output_stream.write(" ".join(sbsrender_render(input_sbsar, command_only=True, **kwargs_cmd)) + "\n")
            continue
        if multi_proc > 0:
            cmds_args_pool.append((input_sbsar, copy.deepcopy(kwargs_cmd)))
        else:
            p = sbsrender_render(input_sbsar, **kwargs_cmd)
            p.wait()
            if p.returncode != 0:
                log.error('Failure executing sbsrender for frame #{}'.format(f))
                success = False
    # multi thread pool
    if multi_proc > 0:
        pool = Pool(multi_proc)
        results = pool.map(_run_render, cmds_args_pool)
        success_results = map(lambda x : x == 0, results)
        success = all(success_results)
        if not success:
            log.error('Failure executing sbsrender for frame {} frames'.format(list(success_results).count(False)))

    return success

