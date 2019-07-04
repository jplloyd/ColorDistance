import spectral
import math

SUMMED_WEIGHTS = sum(spectral.sums)
N = spectral.NUM_WAVES
EPS = spectral.WGM_EPSILON


def log_clamped(x):
    offs = 1.0 - EPS
    return spectral.log2(x * offs + EPS)


# Distance functions

def accum_diff(c1, c2):
    accum_diff = 0.0
    for i in range(N):
        accum_diff += abs(c1[i] - c2[i])
    return accum_diff


def euclidian(c1, c2):
    delta_sqrs = [abs(c1[i] - c2[i])**2 for i in range(N)]
    return math.sqrt(sum(delta_sqrs))


def accum_diff_log(c1, c2):
    c1 = list(map(log_clamped, c1))
    c2 = list(map(log_clamped, c2))
    return accum_diff(c1, c2)


def euclidian_log(c1, c2):
    c1 = list(map(log_clamped, c1))
    c2 = list(map(log_clamped, c2))
    return euclidian(c1, c2)


distance_functions = [
    (accum_diff, "Lin. Accum. difference"),
    (accum_diff_log, "Lin. Accum. difference of log's"),
    (euclidian, "Euclidian distance"),
    (euclidian_log, "Euclidian distance of log's")
]
