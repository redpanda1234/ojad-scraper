v1_tags = set(["v1", "v1-s"])  # no idea why this v1-s class exists.

v5_tags = set(
    [
        "v5" + suffix
        for suffix in [
            "b",
            "g",
            "k",
            "m",
            "n",
            "r",
            "s",
            "t",
            "u",
        ]
    ]
)

v5_i_tags = set(
    [
        "v5" + suffix
        for suffix in [
            "aru",
            "k-s",  # Is this because of 行く te-form?
            "r-i",  # for -aru and stuff, where negative is irregular
            "u-s",  # Some special exceptions; I don't quite remember
        ]
    ]
)

vi_tags = set(
    [
        "vr",  # Aux verbs like たり
        "vk",  # kuru
        "vs",  # suru
        "vs-i",  # idk why this is a special category
        "vs-s",  # i also don't know why *this* is a special category
        #        "vn",  # Honestly I would put this in godan
        "vz",  # japanese is a fucked up language, hey?
    ]
)

all_valid_verb_tags = v1_tags | v5_tags | v5_i_tags | vi_tags
