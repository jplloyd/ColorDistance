import spectral
import math

log2 = spectral.log2

N = spectral.NUM_WAVES
EPS = spectral.WGM_EPSILON

WEIGHTS_MAX = sum(spectral.sums)
LOG_WEIGHTS_MAX = sum([log2(w) - log2(EPS) for w in spectral.sums])
WEIGHTS_DISTANCE_MAX = math.sqrt(sum([w**2 for w in spectral.sums]))
LOG_WEIGHTS_DISTANCE_MAX = math.sqrt(
    sum([(log2(w) - log2(EPS))**2 for w in spectral.sums])
)


# Utility functions and conversion wrappers

def log_clamped(x):
    """Log2 rep. bound to a lower limit by EPS"""
    offs = 1.0 - EPS
    return log2(x * offs + EPS)


def rgba_to_straight_spectral(rgba):
    r, g, b, a = rgba
    """Convert color channels to spectral, ignore alpha"""
    spec = spectral.rgb_to_spectral(r, g, b)
    return spec


def loggify(f):
    """Wrap function to apply base-2 log on arguments"""
    def wrapper(*args):
        return f(*map(lambda a: map(log_clamped, a), args))
    return wrapper


def spectralize(f):
    """Wrap function to convert incoming rgba to spectrals"""
    def wrapper(*args):
        return f(*(map(rgba_to_straight_spectral, args)))
    return wrapper


# Generic distance functions

def accum_diff_linear(c1, c2):
    """Sum of linear difference between channels"""
    return sum([abs(i - j) for i, j in zip(c1, c2)])


def euclidean(c1, c2):
    """Euclidean distance of all channels"""
    return math.sqrt(sum([abs(i - j)**2 for i, j in zip(c1, c2)]))


# Normalized distance functions

def spectral_accum_diff(*cols):
    f = spectralize(accum_diff_linear)
    return f(*cols) / WEIGHTS_MAX


def spectral_accum_diff_log(*cols):
    f = spectralize(loggify(accum_diff_linear))
    return f(*cols) / LOG_WEIGHTS_MAX


def spectral_euclidean(*cols):
    f = spectralize(euclidean)
    return f(*cols) / WEIGHTS_DISTANCE_MAX


def spectral_euclidean_log(*cols):
    f = spectralize(loggify(euclidean))
    return f(*cols) / LOG_WEIGHTS_DISTANCE_MAX


distance_functions = [
    (spectral_accum_diff, "Lin. Accum. difference (Spectral)"),
    (spectral_accum_diff_log, "Lin. Accum. difference of log's (Spectral)"),
    (spectral_euclidean, "Euclidean distance (Spectral)"),
    (spectral_euclidean_log, "Euclidean distance of log's (Spectral)")
]
