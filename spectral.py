import math


def log2(v):
    return math.log(v) / math.log(2)


def zipwith(a, b, f):
    return [f(i, j) for (i, j) in zip(a, b)]


def diff(a, b):
    return a - b if a > b else b - a


WGM_EPSILON = 0.0001
NUM_WAVES = 7
# inversion matrix - not used atm
T_MATRIX_SMALL = [
    [
        0.004727862039458, 0.082644899379487, -0.322515894576622,
        -0.064320292139570, 1.064746457514018, 0.288869101686002,
        0.010454417702711
    ],
    [
        -0.004081870492374, -0.101308479809214, 0.320514309815141,
        0.720325047228787, 0.066431970334792, -0.028358642287937,
        -0.001135818542699
    ],
    [
        0.028683360043884, 1.054907349924059, 0.116111201474362,
        -0.084435897516297, -0.029621508810678, -0.002318568718824,
        -0.000070180490104
    ]
]

spectral_r_small = [
    .014976989831103, 0.015163469993149, 0.024828861915840,
    0.055372724024590, 0.311175941451513, 2.261540004074889,
    2.451861959778458
]

spectral_g_small = [
    0.060871084436057, 0.063645032450431, 0.344088900200936,
    1.235198096662594, 0.145221682434442, 0.101106655125270,
    0.099848117829856
]

spectral_b_small = [
    0.777465337464873, 0.899749264722067, 0.258544195013949,
    0.015623896354842, 0.004846585772726, 0.003989003708280,
    0.003962407615164
]

sums = [
    spectral_b_small[i] +
    spectral_r_small[i] +
    spectral_g_small[i] for i in range(NUM_WAVES)
]


def channel_spectrals(channel_value, channel_weights):
    spectrals = []
    for i in range(NUM_WAVES):
        spectrals.append(channel_value * channel_weights[i])
    return spectrals


def rgb_to_spectral(r, g, b):
    offset = 1.0 - WGM_EPSILON
    r = r * offset + WGM_EPSILON
    g = g * offset + WGM_EPSILON
    b = b * offset + WGM_EPSILON
    # upsample rgb to spectral primaries
    spec_r = channel_spectrals(r, spectral_r_small)
    spec_g = channel_spectrals(g, spectral_g_small)
    spec_b = channel_spectrals(b, spectral_b_small)

    spectrals = []
    # collapse into one spd
    for i in range(NUM_WAVES):
        spectrals.append(spec_r[i] + spec_g[i] + spec_b[i])
    return spectrals


def rgb_to_spectral_log(*rgb):
    return [log2(c) for c in rgb_to_spectral(*rgb)]
