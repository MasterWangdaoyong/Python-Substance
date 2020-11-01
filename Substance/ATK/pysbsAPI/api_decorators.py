# coding: utf-8
"""
Module api_decorators aims to provide useful functions/methods/class decorators
"""
from __future__ import unicode_literals
import inspect
import logging

log = logging.getLogger(__name__)
import re
import sys
from functools import wraps

from pysbs.api_exceptions import SBSLibraryError


def handle_exceptions(doRaise=True):
    """
    This decorator catches any exceptions thrown by the decorated function and print them indicating the kind of exception and
    the name of the function. By default the exception is re-raised so that the caller function catches the exception too.

    :param doRaise: Allows to specify if the decorator must re-raise the exception of not. True by default.
    :type doRaise: bool
    :return: A decorator that catches and print exceptions thrown by decorated functions, and re-raise these exceptions.
    """

    def getFullFunctionName(aFunction, callArgs):
        """
        Build a string corresponding to the full definition of the function:
         - moduleName.functionName for a global function
         - moduleName.className.functionName for a class method
        """
        # Module name & line number
        et, ei, tb = sys.exc_info()
        fullName = aFunction.__module__ + ', line ' + str(tb.tb_next.tb_lineno) + ": "

        # In case of a method bound to a class, retrieve the class name
        if 'self' in callArgs:
            fullName += callArgs['self'].__class__.__name__ + '.'

        fullName += aFunction.__name__ + '()'
        return fullName

    def decorator(function):
        def isALibraryModule(aMod):
            libModules = ['sbslibrary', 'sbsbakerslibrary', 'sbsdictionaries', 'sbsbakersdictionaries',
                          'mdldictionaries']
            subs = re.compile("|".join(libModules))
            return subs.search(aMod) is not None

        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)

            except (KeyError, TypeError) as error:
                callArgs = inspect.getcallargs(function, *args, **kwargs)
                fullName = getFullFunctionName(function, callArgs)

                # Exception coming from Library => raise a SBSLibraryError
                if isALibraryModule(function.__module__):
                    msg = str(error) + ' is not a valid '
                    if isinstance(error, KeyError):
                        msg += 'key'
                    else:
                        msg += 'type'
                    if len(callArgs) > 0:
                        aParamName = list(callArgs.items())[0][0]
                        msg += ' for attribute ' + aParamName
                    log.error('Exception of kind SBSLibraryError in %s: %s', fullName, msg)
                    if doRaise:
                        raise SBSLibraryError('Invalid key provided to sbslibrary: %s' % msg)

                else:
                    msg = 'Exception of kind ' + error.__class__.__name__ + ' in ' + fullName + ': ' + str(error)
                    if isinstance(error, KeyError):
                        msg += ' is not a valid key'
                    if doRaise:
                        raise

            except Exception as error:
                callArgs = inspect.getcallargs(function, *args, **kwargs)
                fullName = getFullFunctionName(function, callArgs)
                log.error('Exception of kind %s in %s', error.__class__.__name__, fullName)
                if doRaise:
                    raise
                else:
                    log.error(error)

        return wrapper

    return decorator


def checkFirstParamIsAString(aFunction):
    """
    This function decorator checks if the first parameter provided to the called function is a string,
    and raise a TypeError if this is not the case.

    :param aFunction: The decorated function
    :type aFunction: function
    """

    @wraps(aFunction)
    def wrapper(*args, **kwargs):
        if args:
            aArg = args[0]
        elif kwargs:
            aArg = list(kwargs.items())[0][1]
        else:
            raise TypeError('At least one string parameter should be provided')

        raiseStrError = True
        try:
            if isinstance(aArg, str) or isinstance(aArg, unicode):
                raiseStrError = False
        except:
            pass

        if raiseStrError:
            raise TypeError(str(aArg) + '(' + aArg.__class__.__name__ + ')')

        return aFunction(*args, **kwargs)

    return wrapper


def doc_inherit(aClass):
    """
    This class decorator allows to complete the docstring of member functions that are not defined with the docstring
    of the same member functions in the parent class if found.

    :param aClass: the class to decorate
    :type aClass: class
    :return: the class, with a modified __doc__ value for some of its member functions
    """
    try:
        methods = inspect.getmembers(aClass, predicate=inspect.ismethod or inspect.isfunction)
        classTree = inspect.getmro(aClass)
        parentMembers = {}
        # Get parent member functions on all the hierarchy tree
        for aParent in reversed(classTree[1:]):
            members = dict(inspect.getmembers(aParent, predicate=inspect.ismethod or inspect.isfunction))
            for aKey, aMember in list(members.items()):
                if aKey not in parentMembers or parentMembers[aKey].__doc__:
                    parentMembers[aKey] = aMember

        # Parse all methods of the input class
        for name, member in methods:
            if not name.startswith('_'):
                # Search for the same method in the parent class
                parentMember = parentMembers.get(name)
                if parentMember:
                    # Handle instancemethod and functions differently
                    if hasattr(member, '__func__') and member.__func__.__doc__ is None:
                        member.__func__.__doc__ = parentMember.__doc__
                    elif member.__doc__ is None:
                        member.__doc__ = parentMember.__doc__

    except Exception as error:
        log.error(error)
        log.error('[api_decorators.doc_inherit]Failed to complete the docstring of class %s', aClass.__name__)
    finally:
        return aClass


def doc_source_code(aFunction):
    """
    This decorator allows to complete the docstring of the given function by adding the entire code definition to it.

    :param aFunction: The function to decorate
    :type aFunction: function
    :return: the function, with a modified __doc__ value
    """
    try:
        # Get the current function docstring
        doc = aFunction.__doc__

        # If the function is decorated, retrieve the non-decorated code
        realFunction = aFunction
        try:
            if aFunction.func_closure:
                closure = aFunction.func_closure[-1]
                realFunction = closure.cell_contents
        except:
            pass

        # Get the source code as string
        code = inspect.getsource(realFunction)

        # Compute the indentation string
        match = re.search(r'[^\n\r]', doc)
        posNewLine = match.start()
        match = re.search(r'[^ \t]', doc[posNewLine:])
        sizeIndent = match.start()
        indent = doc[posNewLine:posNewLine + sizeIndent]

        # Get the code string
        posBeginDoc = code.find(doc)
        posEndDoc = posBeginDoc + len(doc)
        match = re.search('(""")', code[posEndDoc:], re.MULTILINE)
        posBeginCode = posEndDoc + match.start()
        match = re.search('\n', code[posBeginCode:])
        posBeginCode += match.start()
        docCode = code[posBeginCode:]

        # Include the code into the docstring, with the appropriate indentation
        intro = '\n' + indent + 'Here is the code of function ' + realFunction.__name__ + ':\n\n' + indent + '.. code-block:: python\n\n'
        codeIndent = indent + '    '
        intro += codeIndent
        docCode = intro + docCode.replace('\n', '\n' + codeIndent)

        aFunction.__doc__ += docCode

    except Exception as error:
        log.error(error)
        log.error('[api_decorators.doc_source_code]Failed to complete docstring with the code for function %s',
                  str(aFunction))
    finally:
        return aFunction


def doc_source_code_enum(aClass):
    """
    This decorator allows to complete the docstring of the given enum class by adding the entire code definition to it.

    :param aClass: The class to decorate
    :type aClass: class
    :return: the class, with a modified __doc__ value
    """
    try:
        # Get the current function docstring
        doc = aClass.__doc__

        # Get the current code as string
        code = inspect.getsource(aClass)

        # Compute the indentation string
        match = re.search(r'[^\n\r]', doc)
        posNewLine = match.start()
        match = re.search(r'[^ \t]', doc[posNewLine:])
        sizeIndent = match.start()
        indent = doc[posNewLine:posNewLine + sizeIndent]

        # Get the code string
        posBeginDoc = code.find(doc)
        posEndDoc = posBeginDoc + len(doc)
        match = re.search('(""")', code[posEndDoc:], re.MULTILINE)
        posBeginCode = posEndDoc + match.start()
        match = re.search('\n', code[posBeginCode:])
        posBeginCode += match.start()
        docCode = code[posBeginCode:]

        # For enums defined with range() function, document the real values
        docEnumValues = ''
        pattern = re.compile('(\n' + indent + ')[a-zA-Z0-9_]+')
        enumValue = re.search(pattern, docCode)
        while enumValue is not None:
            spaces = re.search('[ \t]*', docCode[enumValue.end():])
            endSpaces = enumValue.end() + spaces.end()

            enumLine = docCode[enumValue.start():endSpaces]
            matchEndLine = docCode.find('\n', endSpaces)
            if docCode[endSpaces] == '=':
                docEnumValues += enumLine + docCode[endSpaces:matchEndLine]
            else:
                enumName = docCode[enumValue.start() + len(indent) + 1:enumValue.end()]
                if enumName in aClass.__dict__:
                    docEnumValues += enumLine + '= ' + str(aClass.__dict__[enumName])

            docCode = docCode[matchEndLine:]
            enumValue = re.search(pattern, docCode)

        # Include the code into the docstring, with the appropriate indentation
        intro = '::\n'
        codeIndent = indent + '    '
        intro += codeIndent
        docEnumValues = intro + docEnumValues.replace('\n', '\n' + codeIndent)
        aClass.__doc__ += docEnumValues + '\n'

    except Exception as error:
        log.error(error)
        log.error('[api_decorators.doc_source_code_enum]Failed to complete docstring with the code for class %s',
                  str(aClass))
    finally:
        return aClass


def doc_private_members():
    """
    This decorator allows to complete the docstring of the given class by adding the code that defines a private member.
    The private member must be at least referenced in the docstring using a list, for instance:

        * The library of filters and their definitions:
            * __library_Filters: the library of Filters, identified by :class:`.FilterEnum`

    The code declaring the member __library_Filters will be added just after this line in the docstring.
    """

    def updateParenthesisStack(aCurrentStack, aLine):
        pattern = '[\{\}\(\)\[\]]'
        parenthesis = re.findall(pattern, aLine)
        for par in parenthesis:
            if (par == ')' and aCurrentStack[-1] == '(') or \
                    (par == '}' and aCurrentStack[-1] == '{') or \
                    (par == ']' and aCurrentStack[-1] == '['):
                aCurrentStack = aCurrentStack[0:-1]
            else:
                aCurrentStack += par

        return aCurrentStack

    def class_decorator(aClass):
        """
        :param aClass: The class to decorate
        :type aClass: class
        :return: the class, with a modified __doc__ value
        """
        try:
            # Get the current code as string
            code = inspect.getsource(aClass)

            # Find the line in the doc that contains the description a private member
            patternPM = '^[ \t-]*\*[ ]*_[_a-zA-Z0-9]+[ :]*'
            matchPM = re.search(patternPM, aClass.__doc__, re.MULTILINE)
            indexInDoc = 0

            while matchPM:
                # Compute the position where to insert the private member description in the docstring
                charIndexToInsertCodeDoc = indexInDoc + matchPM.end() + aClass.__doc__[
                                                                        indexInDoc + matchPM.end():].find('\n')

                # Compute the indentation string
                docLine = aClass.__doc__[indexInDoc + matchPM.start(): indexInDoc + matchPM.end()]
                match = re.search(r'[^ \t]', docLine)
                sizeIndent = match.start()
                indent = docLine[0:sizeIndent]

                # Begin the docCode string
                docCode = '::\n'
                codeIndent = indent + '    '
                docCode += codeIndent + '\n'

                # Compute the private member name
                match = re.search('_[_a-zA-Z0-9]+', docLine)
                member_name = docLine[match.start():match.end()]

                # Parse the code lines to retrieve the member definition
                pattern = '^[ \t]+' + member_name + '[ \t]*\='
                matchCode = re.search(pattern, code, re.MULTILINE)
                if matchCode:
                    indexLineCode = matchCode.start()

                    # Get all the lines in the code that define the member (check the parenthesis closure)
                    endLine = code[indexLineCode:].find('\n')
                    parenthesisStack = ''
                    while endLine >= 0:
                        aLine = code[indexLineCode:indexLineCode + endLine]
                        docCode += codeIndent + aLine + '\n'
                        parenthesisStack = updateParenthesisStack(parenthesisStack, aLine)
                        if len(parenthesisStack) == 0:
                            break
                        indexLineCode += endLine + 1
                        endLine = code[indexLineCode:].find('\n')

                    newDoc = aClass.__doc__[0:charIndexToInsertCodeDoc] + docCode + aClass.__doc__[
                                                                                    charIndexToInsertCodeDoc + 1:]
                    aClass.__doc__ = newDoc
                else:
                    log.warning('No code for %s', member_name)

                # Find next member to document
                indexInDoc = charIndexToInsertCodeDoc
                matchPM = re.search(patternPM, aClass.__doc__[indexInDoc:], re.MULTILINE)

        except Exception as error:
            log.error(error)
            log.error(
                '[api_decorators.doc_private_members]Failed to complete the docstring of class %s' % aClass.__name__)
        finally:
            return aClass

    return class_decorator


def doc_module_attributes(aModule):
    """
    This function allows to complete the docstring of the given module by adding the code that defines a member.
    The member must be at least referenced in the docstring using a list, for instance:

        * The library of filters and their definitions:
            * filter_BITMAP

    The code declaring the member filter_BITMAP will be added just after this line in the docstring.

    :param aModule: The module whose docstring must be completed
    :type aModule: module
    :return: nothing
    """

    def updateParenthesisStack(currentStack, line):
        parenthesis = re.findall('[\{\}\(\)\[\]]', line)
        for par in parenthesis:
            if (par == ')' and currentStack[-1] == '(') or \
                    (par == '}' and currentStack[-1] == '{') or \
                    (par == ']' and currentStack[-1] == '['):
                currentStack = currentStack[0:-1]
            else:
                currentStack += par

        return currentStack

    try:
        # Get the current code as string
        code = inspect.getsource(aModule)

        # Find the line in the doc that contains the description a member
        patternPM = '^[ \t-]*\*[ ]*[_a-zA-Z0-9]+[ :]*'
        matchPM = re.search(patternPM, aModule.__doc__, re.MULTILINE)
        indexInDoc = 0

        while matchPM:
            # Compute the position where to insert the member description in the docstring
            charIndexToInsertCodeDoc = indexInDoc + matchPM.end() + aModule.__doc__[indexInDoc + matchPM.end():].find(
                '\n')

            # Compute the indentation string
            docLine = aModule.__doc__[indexInDoc + matchPM.start(): indexInDoc + matchPM.end()]
            match = re.search(r'[^ \t]', docLine)
            sizeIndent = match.start()
            indent = docLine[0:sizeIndent]

            # Begin the docCode string
            docCode = '::\n'
            codeIndent = indent + '    '
            docCode += codeIndent + '\n'

            # Compute the private member name
            match = re.search('[_a-zA-Z0-9]+', docLine)
            member_name = docLine[match.start():match.end()]

            # Parse the code lines to retrieve the member definition
            pattern = '^[ \t]*' + member_name + '[ \t]*\='
            matchCode = re.search(pattern, code, re.MULTILINE)
            if matchCode:
                indexLineCode = matchCode.start()

                # Get all the lines in the code that define the member (check the parenthesis closure)
                endLine = code[indexLineCode:].find('\n')
                parenthesisStack = ''
                while endLine >= 0:
                    aLine = code[indexLineCode:indexLineCode + endLine]
                    docCode += codeIndent + aLine + '\n'
                    parenthesisStack = updateParenthesisStack(parenthesisStack, aLine)
                    if len(parenthesisStack) == 0:
                        break
                    indexLineCode += endLine + 1
                    endLine = code[indexLineCode:].find('\n')

                newDoc = aModule.__doc__[0:charIndexToInsertCodeDoc] + docCode + aModule.__doc__[
                                                                                 charIndexToInsertCodeDoc + 1:]
                aModule.__doc__ = newDoc
            else:
                log.warning("No code for %s", member_name)

            # Find next member to document
            indexInDoc = charIndexToInsertCodeDoc
            matchPM = re.search(patternPM, aModule.__doc__[indexInDoc:], re.MULTILINE)

    except Exception as error:
        log.error(error)
        log.error(
            '[api_decorators.doc_module_attributes]Failed to complete the docstring of module %s' % aModule.__name__)


_knownDeprecatedFunctions = set()


def deprecated(moduleName, since_version, reason, recommendedAction):
    """
    Decorator to attach to functions that are deprecated and eventually will be removed
    :param func: The function flagged as deprecated
    :type func: function
    :param recommendedAction: String with the recommended action to do to be up to standard
    :type recommendedAction: string
    """

    def deprecated_msg(func):
        def deprecated_function(*args, **kwargs):
            if func not in _knownDeprecatedFunctions:
                log.warning('Deprecated function %s in module %s since version %s. %s. %s.' % (func.__name__,
                                                                                               moduleName,
                                                                                               since_version,
                                                                                               reason,
                                                                                               recommendedAction))
                _knownDeprecatedFunctions.add(func)
            return func(*args, **kwargs)

        return deprecated_function

    return deprecated_msg
