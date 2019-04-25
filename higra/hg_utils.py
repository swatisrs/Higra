############################################################################
# Copyright ESIEE Paris (2018)                                             #
#                                                                          #
# Contributor(s) : Benjamin Perret                                         #
#                                                                          #
# Distributed under the terms of the CECILL-B License.                     #
#                                                                          #
# The full license is in the file LICENSE, distributed with this software. #
############################################################################

import higra as hg
import numpy as np


def extend_class(cls, method_name=None):
    """
    Add the decorated function to the specified class.
    If no name is specified the name of the function is used.
    """

    def decorate(funct):
        tmp = method_name
        if tmp is None:
            if hasattr(funct, "__name__"):
                tmp = funct.__name__
            else:
                raise RuntimeError("Name attribute cannot be found in " + str(funct))
        setattr(cls, tmp, funct)
        return funct

    return decorate


def normalize_shape(shape):
    """
    This function ensure that the given shape will be easily convertible
    in a c++ callback (ie. that it won't interfere badly in pybind11
    overload resolution algorithm)
    :param shape:
    :return:
    """
    return tuple(int(i) for i in shape)


@hg.argument_helper(hg.CptVertexWeightedGraph, ("graph", hg.CptGridGraph))
def linearize_vertex_weights(vertex_weights, graph=None, shape=None):
    if shape is None or graph.num_vertices() == vertex_weights.shape[0]:
        return vertex_weights

    v_shape = vertex_weights.shape
    if len(v_shape) < len(shape):
        raise Exception("Vertex weights shape " + str(v_shape) +
                        " is not compatible with graph shape " + str(shape) + ".")

    flag = True
    for i in range(len(shape)):
        if v_shape[i] != shape[i]:
            flag = False
            break

    if not flag:
        raise Exception("Vertex weights shape " + str(v_shape) +
                        " is not compatible with graph shape " + str(shape) + ".")

    return vertex_weights.reshape([graph.num_vertices()] + list(v_shape[len(shape):]))


@hg.argument_helper(hg.CptVertexWeightedGraph, ("graph", hg.CptGridGraph))
def delinearize_vertex_weights(vertex_weights, graph=None, shape=None):
    if shape is None:
        return vertex_weights

    v_shape = vertex_weights.shape

    if len(v_shape) >= len(shape):
        if shape == v_shape[:len(shape)]:
            return vertex_weights

    if v_shape[0] != graph.num_vertices():
        raise Exception("Vertex weights shape " + str(v_shape) +
                        " is not compatible with graph size " + str(graph.num_vertices()) + ".")

    return vertex_weights.reshape(list(shape) + list(v_shape[1:]))


def is_in_bijection(a, b):
    """
    Given two numpy arrays a and b returns true iif
        - a and b have same size
        - there exists a bijective function f such that, for all i a(i) = f(b(i))

    :param a:
    :param b:
    :return:
    """
    aa = a.flatten()
    bb = b.flatten()

    if aa.size != bb.size:
        return False

    equiv1 = {}
    equiv2 = {}

    for i in range(aa.size):
        v1 = aa[i]
        v2 = bb[i]

        if v1 in equiv1:
            if equiv1[v1] != v2:
                return False
        else:
            equiv1[v1] = v2

        if v2 in equiv2:
            if equiv2[v2] != v1:
                return False
        else:
            equiv2[v2] = v1

    return True


def mean_angle_mod_pi(angles1, angles2):
    """
    Compute the element wise mean of two arrays of angles (radian) handling a modulo pi wrapping

    eg: the modulo pi mean angle between 0 and 3.0 is roughly 3.07

    :param angles1: must be in [0; pi]
    :param angles2: must be in [0; pi]
    :return: average of angles1 and angles2 with correct wrapping in [0; pi]
    """
    min_angles = np.minimum(angles1, angles2)
    max_angles = np.maximum(angles1, angles2)
    differences = max_angles - min_angles

    # places where we should have wrapped
    problems = differences > np.pi / 2
    ok = np.logical_not(problems)

    # handle wrapping
    differences[problems] = (np.pi - differences[problems]) / 2 + max_angles[problems]
    differences[ok] = min_angles[ok] + differences[ok] / 2

    # modulo pi
    differences[differences > np.pi] -= np.pi
    return differences


def dtype_info(dtype):
    """
    Returns a `numpy.iinfo` object if given dtype is an integral type,
    and a `numpy.finfo` if given dtype os a float type.

    Raises an exception is dtype is a more complex type.

    :param dtype:
    :return:
    """
    int_types = (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64)
    float_types = (np.float32, np.float64)

    if dtype in int_types:
        return np.iinfo(dtype)
    elif dtype in float_types:
        return np.finfo(dtype)
    else:
        raise TypeError("Given dtype is not suported or invalid.")


__int8 = 'int8'
__int16 = 'int16'
__int32 = 'int32'
__int64 = 'int64'
__uint8 = 'uint8'
__uint16 = 'uint16'
__uint32 = 'uint32'
__uint64 = 'uint64'
__float32 = 'float32'
__float64 = 'float64'

__minimum_type_order = {
    __int8: {
        __int8: __int8,
        __uint8: __int16,
        __int16: __int16,
        __uint16: __int32,
        __int32: __int32,
        __uint32: __int64,
        __int64: __int64,
        __uint64: __int64,
        __float32: __float32,
        __float64: __float64
    },
    __uint8: {
        __int8: __int16,
        __uint8: __uint8,
        __int16: __int16,
        __uint16: __uint16,
        __int32: __int32,
        __uint32: __uint32,
        __int64: __int64,
        __uint64: __uint64,
        __float32: __float32,
        __float64: __float64
    },
    __int16: {
        __int8: __int16,
        __uint8: __int16,
        __int16: __int16,
        __uint16: __int32,
        __int32: __int32,
        __uint32: __int64,
        __int64: __int64,
        __uint64: __int64,
        __float32: __float32,
        __float64: __float64
    },
    __uint16: {
        __int8: __int32,
        __uint8: __uint16,
        __int16: __int32,
        __uint16: __uint16,
        __int32: __int32,
        __uint32: __uint32,
        __int64: __int64,
        __uint64: __uint64,
        __float32: __float32,
        __float64: __float64
    },
    __int32: {
        __int8: __int32,
        __uint8: __int32,
        __int16: __int32,
        __uint16: __int32,
        __int32: __int32,
        __uint32: __int64,
        __int64: __int64,
        __uint64: __int64,
        __float32: __float32,
        __float64: __float64
    },
    __uint32: {
        __int8: __int64,
        __uint8: __uint32,
        __int16: __int64,
        __uint16: __uint32,
        __int32: __int64,
        __uint32: __uint32,
        __int64: __int64,
        __uint64: __uint64,
        __float32: __float32,
        __float64: __float64
    },
    __int64: {
        __int8: __int64,
        __uint8: __int64,
        __int16: __int64,
        __uint16: __int64,
        __int32: __int64,
        __uint32: __int64,
        __int64: __int64,
        __uint64: __int64,
        __float32: __float32,
        __float64: __float64
    },
    __uint64: {
        __int8: __int64,
        __uint8: __uint64,
        __int16: __int64,
        __uint16: __uint64,
        __int32: __int64,
        __uint32: __uint64,
        __int64: __int64,
        __uint64: __uint64,
        __float32: __float32,
        __float64: __float64
    },
    __float32: {
        __int8: __float32,
        __uint8: __float32,
        __int16: __float32,
        __uint16: __float32,
        __int32: __float32,
        __uint32: __float32,
        __int64: __float32,
        __uint64: __float32,
        __float32: __float32,
        __float64: __float64
    },
    __float64: {
        __int8: __float64,
        __uint8: __float64,
        __int16: __float64,
        __uint16: __float64,
        __int32: __float64,
        __uint32: __float64,
        __int64: __float64,
        __uint64: __float64,
        __float32: __float64,
        __float64: __float64
    },
}


def common_type(*arrays, safety_level='minimum'):
    """
    Find a common type to a list of numpy arrays.

    If safety level is equal to 'minimum', then the result type is the smallest that ensures that all values in all
    arrays can be represented exactly in the given type (except for `np.uint64` which is allowed to fit in a `np.int64`!)
    In this case the function also guaranties that the result type is integral if all the arrays have integral types.

    If safety level is equal to 'overflow', the result type ensures a to have a type suitable to contain the result of common
    operations involving the input arrays (additions, divisions...). This relies on `numpy.common_type`: The return type will always
    be an inexact (i.e. floating point) scalar type, even if all the arrays are integer arrays. If one of the inputs is
    an integer array, the minimum precision type that is returned is a 64-bit floating point dtype.

    All input arrays except int64 and uint64 can be safely cast to the returned dtype without loss of information.

    :param arrays: a sequence of numpy arrays
    :param safety_level: either 'minimum' or 'overflow'
    :return: a numpy dtype
    """

    if safety_level == 'overflow':
        return np.common_type(*arrays)

    if safety_level != 'minimum':
        raise ValueError('Unknown safety level: should be "minimum" or "overflow"')

    ctype = str(arrays[0].dtype)
    for i in range(1, len(arrays)):
        ctype = __minimum_type_order[ctype][str(arrays[i].dtype)]

    return np.dtype(ctype)


def cast_to_common_type(*arrays, safety_level='minimum'):
    """
    Find a common type to a list of numpy arrays, cast all arrays that need to be cast to this type and returns the list of arrays (with some of them casted).

    see :func:`~higra.common_type`

    If safety level is equal to 'minimum', then the result type is the smallest that ensures that all values in all
    arrays can be represented exactly in the given type (except for `np.uint64` which is allowed to fit in a `np.int64`!)
    In this case the function also guaranties that the result type is integral if all the arrays have integral types.

    If safety level is equal to 'overflow', the result type ensures a to have a type suitable to contain the result of common
    operations involving the input arrays (additions, divisions...). This relies on `numpy.common_type`: The return type will always
    be an inexact (i.e. floating point) scalar type, even if all the arrays are integer arrays. If one of the inputs is
    an integer array, the minimum precision type that is returned is a 64-bit floating point dtype.

    All input arrays except int64 and uint64 can be safely cast to the returned dtype without loss of information.

    :param arrays: a sequence of numpy arrays
    :param safety_level: either 'minimum' or 'overflow'
    :return: a list of arrays
    """

    ctype = common_type(*arrays, safety_level=safety_level)

    return [a if a.dtype == ctype else a.astype(ctype) for a in arrays]


def cast_to_dtype(array, dtype):
    """
    Cast the given numpy array to the given dtype and returns the result.
    If the input array dtype is already equal to the given dtype, the input array is returned.

    :param array: a numpy array
    :param dtype: a numpy dtype
    :return: a numpy array
    """
    if array.dtype != dtype:
        array = array.astype(dtype)
    return array
