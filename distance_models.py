# Copyright (C) 2019 by Jesper Lloyd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

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


def rgba_to_straight_spectral(*rgba):
    """Convert color channels to spectral, ignore alpha"""
    # I don't know why the tuple gets wrapped in another
    # tuple during when its parent is mapped over...
    return spectral.rgb_to_spectral(*(rgba[0][:3]))


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


def max_diff_abs(c1, c2):
    """Absolute difference of highest-deviation channel"""
    return max([abs(i - j) for i, j in zip(c1, c2)])


def max_diff_scaled(c1, c2):
    """Scaled difference of highest-deviation channel"""
    return max([abs(i - j) / k for i, j, k in zip(c1, c2, spectral.sums)])


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


def spectral_maxdiff_abs(*cols):
    return spectralize(max_diff_abs)(*cols)


def spectral_maxdiff_scaled(*cols):
    return spectralize(max_diff_scaled)(*cols)


distance_functions = [
    (spectral_accum_diff, "Lin. Accum. difference (Spectral)"),
    (spectral_accum_diff_log, "Lin. Accum. difference of log's (Spectral)"),
    (spectral_euclidean, "Euclidean distance (Spectral)"),
    (spectral_euclidean_log, "Euclidean distance of log's (Spectral)"),
    (spectral_maxdiff_abs, "Maximum absolute channel diff (Spectral)"),
    (spectral_maxdiff_scaled, "Maximum scaled channel diff (Spectral)"),
]
