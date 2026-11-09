import numpy as np
from pymatgen.core import Element
from singingmaterials.dos_stats import dos_stats_analysis

# Strudel's default drum names, ordered roughly from highest to lowest sound.
# The order is a judgement call (cymbals and noise don't have a clear pitch), so swap them around to taste.
DRUMS_HIGH_TO_LOW = [
    "hh",
    "oh",
    "rd",
    "cr",
    "cb",
    "rim",
    "cp",
    "sd",
    "ht",
    "mt",
    "lt",
    "bd",
]


def make_drum_map(
    *element_arrays, lightest="H", heaviest="Bi", drums=DRUMS_HIGH_TO_LOW
):
    """Map elements to drums, lightest -> highest drum, heaviest -> lowest drum.

    element_arrays : one or more numpy arrays of element symbols (e.g. one per material).
    lightest : element symbol setting the light end of the mapping (default "H").
        Pass None to use the lightest element in element_arrays instead.
    heaviest : element symbol setting the heavy end of the mapping (default "Bi").
        Pass None to use the heaviest element in element_arrays instead.

    Every element in the periodic table between the two boundary masses is sorted by atomic mass
    and split into len(drums) equal-sized groups. Returns {symbol: drum}.
    """
    symbols = np.unique(np.concatenate([np.asarray(a).ravel() for a in element_arrays]))
    masses = np.array([float(Element(s).atomic_mass) for s in symbols])

    m_min = masses.min() if lightest is None else float(Element(lightest).atomic_mass)
    m_max = masses.max() if heaviest is None else float(Element(heaviest).atomic_mass)
    if masses.max() > m_max:
        raise ValueError(
            f"{symbols[masses.argmax()]} is heavier than the heaviest boundary ({heaviest})"
        )
    if masses.min() < m_min:
        raise ValueError(
            f"{symbols[masses.argmin()]} is lighter than the lightest boundary ({lightest})"
        )

    table = [e for e in Element if m_min <= float(e.atomic_mass) <= m_max]
    table.sort(key=lambda e: float(e.atomic_mass))
    if len(table) < len(drums):
        raise ValueError(
            f"only {len(table)} elements in range, fewer than the {len(drums)} drums"
        )

    return {
        e.symbol: drum
        for drum, group in zip(
            drums, np.array_split(np.array(table, dtype=object), len(drums))
        )
        for e in group
    }


# Band centre is mapped to hits per cycle, on a log scale. The frequency range is fixed across all
# materials so that they can be compared; band centres outside it are clipped.
F_MIN, F_MAX = 0.5e12, 25e12  # Hz
HITS_MIN, HITS_MAX = 1, 16  # hits per cycle

# Temperature (K) for Bose-Einstein weighted band centres, or None for athermal.
# The dos_dict must be made with dos_stats_analysis(..., temp=TEMPERATURE) for this to work.
TEMPERATURE = None


def band_centre_to_hits(f):
    """log-map a band centre (Hz) to a whole number of hits per cycle."""
    x = np.clip(np.log(f / F_MIN) / np.log(F_MAX / F_MIN), 0, 1)
    return int(round(HITS_MIN * (HITS_MAX / HITS_MIN) ** x))


def select_stats(stats, temperature=TEMPERATURE):
    """Return the athermal stats if temperature is None, otherwise the thermal stats at that temperature."""
    if temperature is None:
        return stats["athermal"]
    try:
        return stats["thermal"][str(temperature)]
    except KeyError:
        raise KeyError(
            f"no thermal stats at {temperature} K; "
            f"call dos_stats_analysis(..., temp={temperature}) first"
        ) from None


def get_strudel_beats_string_from_dos_dict(dos_dict, temperature=TEMPERATURE):
    element_data = {
        el: {
            "band_centre": select_stats(d["stats"], temperature)["band_centre"],  # Hz
            "atomic_weight": float(Element(el).atomic_mass),  # amu
        }
        for el, d in dos_dict["element"].items()
    }

    mats = [
        np.array(list(dos_stats_analysis(mp_id=m)["element"]))
        for m in ["mp-6947", "mp-22862", "mp-66", "mp-22862"]
    ]
    drum_map = make_drum_map(*mats)  # lightest element given → Bi

    for el, info in element_data.items():
        info["drum"] = drum_map[el]

    for el, info in element_data.items():
        info["hits"] = band_centre_to_hits(info["band_centre"])

    layers = ", ".join(
        f"{info['drum']}*{info['hits']}" for info in element_data.values()
    )
    return f'setcpm(30)\ns("{layers}")'
