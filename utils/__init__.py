# -*- coding: utf-8 -*-
import atexit
import re
import subprocess
import os
# import diaper for backward compatibility
import diaper

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'



def property_or_none(wrapped, *args, **kwargs):
    """property_or_none([fget[, fset[, fdel[, doc]]]])
    Property decorator that turns AttributeErrors into None returns

    Useful for chained attr lookups where some links in the chain are None

    Note:

        This delegates back to the :py:func:`property <python:property>` builtin and inherits
        its signature; thus it can be used interchangeably with ``property``.

    """
    def wrapper(store):
        try:
            return wrapped(store)
        except AttributeError:
            pass
    return property(wrapper, *args, **kwargs)


class _classproperty(property):
    """Subclass property to make classmethod properties possible"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def classproperty(f):
    """Enables properties for whole classes:

    Usage:

        >>> class Foo(object):
        ...     @classproperty
        ...     def bar(cls):
        ...         return "bar"
        ...
        >>> print(Foo.bar)
        baz
    """
    return _classproperty(classmethod(f))


def at_exit(f, *args, **kwargs):
    """Diaper-protected atexit handler registering. Same syntax as atexit.register()"""
    return atexit.register(lambda: diaper(f, *args, **kwargs))


def normalize_text(text):
    text = re.sub(r"[^a-z0-9 ]", "", text.strip().lower())
    return re.sub(r"\s+", " ", text)


def tries(num_tries, exceptions, f, *args, **kwargs):
    """ Tries to call the function multiple times if specific exceptions occur.

    Args:
        num_tries: How many times to try if exception is raised
        exceptions: Tuple (or just single one) of exceptions that should be treated as repeat.
        f: Callable to be called.
        *args: Arguments to be passed through to the callable
        **kwargs: Keyword arguments to be passed through to the callable

    Returns:
        What ``f`` returns.

    Raises:
        What ``f`` raises if the try count is exceeded.
    """
    tries = 0
    while tries < num_tries:
        tries += 1
        try:
            return f(*args, **kwargs)
        except exceptions as e:
            pass
    else:
        raise e


def read_env(file):
    """Given a py.path.Local file name, return a dict of exported shell vars and their values

    Note:

        This will only include shell variables that are exported from the file being parsed

    Returns a dict of varname: value pairs. If the file does not exist or bash could not parse
    the file, this dict will be empty.

    """
    env_vars = {}
    if file.check():
        with file.open() as f:
            content = f.read()

        # parse the file with bash, since it's pretty good at it, and dump the env
        command = ['bash', '-c', 'source {} && env'.format(file.strpath)]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1)

        # filter out vars not defined
        for line in iter(proc.stdout.readline, b''):
            try:
                key, value = line.split("=", 1)
            except ValueError:
                continue
            if '{}='.format(key) in content:
                env_vars[key] = value.strip()
        stdout, stderr = proc.communicate()
    return env_vars


def deferred_verpick(version_d):
    """This turns a dictionary for verpick to a class property.

    Useful for verpicked constants.
    """
    from utils.version import Version, pick as _version_pick

    @classproperty
    def getter(self):
        if on_rtd:
            if version_d:
                return version_d[sorted(version_d.keys(), key=Version)[-1]]
            else:
                raise Exception("Nothing to pick from")
        else:
            return _version_pick(version_d)
    return getter


def safe_string(o):
    """This will make string out of ANYTHING without having to worry about the stupid Unicode errors

    This function tries to make str/unicode out of ``o`` unless it already is one of those and then
    it processes it so in the end there is a harmless ascii string.

    Args:
        o: Anything.
    """
    if not isinstance(o, basestring):
        if hasattr(o, "__unicode__"):
            o = unicode(o)
        else:
            o = str(o)
    if isinstance(o, str):
        o = o.decode('utf-8', "ignore")
    if isinstance(o, unicode):
        o = o.encode("ascii", "xmlcharrefreplace")
    return o


def process_pytest_path(path):
    # Processes the path elements with regards to []
    path = path.lstrip("/")
    if len(path) == 0:
        return []
    try:
        seg_end = path.index("/")
    except ValueError:
        seg_end = None
    try:
        param_start = path.index("[")
    except ValueError:
        param_start = None
    try:
        param_end = path.index("]")
    except ValueError:
        param_end = None
    if seg_end is None:
        # Definitely a final segment
        return [path]
    else:
        if (param_start is not None and param_end is not None and seg_end > param_start
                and seg_end < param_end):
            # The / inside []
            segment = path[:param_end + 1]
            rest = path[param_end + 1:]
            return [segment] + process_pytest_path(rest)
        else:
            # The / that is not inside []
            segment = path[:seg_end]
            rest = path[seg_end + 1:]
            return [segment] + process_pytest_path(rest)


def process_shell_output(value):
    """This function allows you to unify the behaviour when you putput some values to stdout.

    You can check the code of the function how exactly does it behave for the particular types of
    variables. If no output is expected, it returns None.

    Args:
        value: Value to be outputted.

    Returns:
        A tuple consisting of returncode and the output to be printed.
    """
    result_lines = []
    exit = 0
    if isinstance(value, (list, tuple, set)):
        for entry in sorted(value):
            result_lines.append(entry)
    elif isinstance(value, dict):
        for key, value in value.iteritems():
            result_lines.append('{}={}'.format(key, value))
    elif isinstance(value, str):
        result_lines.append(value)
    elif isinstance(value, bool):
        # 'True' result becomes flipped exit 0, and vice versa for False
        exit = int(not value)
    else:
        # Unknown type, print it
        result_lines.append(str(value))

    return exit, '\n'.join(result_lines) if result_lines else None


def iterate_pairs(iterable):
    """Iterates over iterable, always taking two items at time.

    Eg. ``[1, 2, 3, 4, 5, 6]`` will yield ``(1, 2)``, then ``(3, 4)`` ...

    Must have even number of items.

    Args:
        iterable: An iterable with even number of items to be iterated over.
    """
    if len(iterable) % 2 != 0:
        raise ValueError('Iterable must have even number of items.')
    it = iter(iterable)
    for i in it:
        yield i, next(it)


def icastmap(t, i, *args, **kwargs):
    """Works like the map() but is made specially to map classes on iterables. A generator version.

    This function only applies the ``t`` to the item of ``i`` if it is not of that type.

    Args:
        t: The class that you want all the yielded items to be type of.
        i: Iterable with items to be cast.

    Returns:
        A generator.
    """
    for item in i:
        if isinstance(item, t):
            yield item
        else:
            yield t(item, *args, **kwargs)


def castmap(t, i, *args, **kwargs):
    """Works like the map() but is made specially to map classes on iterables.

    This function only applies the ``t`` to the item of ``i`` if it is not of that type.

    Args:
        t: The class that you want all theitems in the list to be type of.
        i: Iterable with items to be cast.

    Returns:
        A list.
    """
    return list(icastmap(t, i, *args, **kwargs))
