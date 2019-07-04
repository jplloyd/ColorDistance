import spectral
import math

SUMMED_WEIGHTS = sum(spectral.sums)
N = spectral.NUM_WAVES
EPS = spectral.WGM_EPSILON


def log_clamped(x):
    """Log2 rep. bound to a lower limit by EPS"""
    offs = 1.0 - EPS
    return spectral.log2(x * offs + EPS)


def rgba_to_straight_spectral(rgba):
    r, g, b, a = rgba
    """Convert color channels to spectral, ignore alpha"""
    spec = spectral.rgb_to_spectral(r, g, b)
    return spec


# Distance functions

def accum_diff_linear(c1, c2):
    """Sum of linear difference between channels"""
    return sum([abs(i - j) for i, j in zip(c1, c2)])


def euclidian(c1, c2):
    return math.sqrt(sum([abs(i - j)**2 for i, j in zip(c1, c2)]))


def accum_diff_linear_log(c1, c2):
    return accum_diff_linear(map(log_clamped, c1), map(log_clamped, c2))


def euclidian_log(c1, c2):
    return euclidian(map(log_clamped, c1), map(log_clamped, c2))


# Representation-agnostic functions

distance_functions = [
    (accum_diff_linear, "Lin. Accum. difference"),
    (accum_diff_linear_log, "Lin. Accum. difference of log's"),
    (euclidian, "Euclidian distance"),
    (euclidian_log, "Euclidian distance of log's")
]


# Convenience for switching between different representations

def concretize(func_pair):
    func, name = func_pair

    def converter(c1, c2):
        return func(*map(rgba_to_straight_spectral, [c1, c2]))

    return (converter, name)


# Representation-bound functions

distance_functions = list(map(concretize, distance_functions))
