# coding: utf-8

"""
Definition of generic physics processes and constants.

In a perfect world, a file like this would be provided centrally, even across collaborations.
"""

__all__ = [
    "n_leps", "m_z", "br_w", "br_ww", "br_z", "br_h",
    "tt", "tt_sl", "tt_dl", "tt_fh",
    "st", "st_tchannel", "st_twchannel", "st_schannel",
    "w", "w_lnu",
]

from scinum import Number, Correlation
from order import Process

from columnflow.util import DotDict


#
# constants
#

# misc
n_leps = Number(3)

# masses
m_z = Number(91.1876, {"z_mass": 0.0021})

# branching ratios
br_w = DotDict()
br_w["had"] = Number(0.6741, {"br_w_had": 0.0027})
br_w["lep"] = 1 - br_w.had

br_ww = DotDict(
    fh=br_w.had ** 2,
    dl=br_w.lep ** 2,
    sl=2 * ((br_w.had * Correlation(br_w_had=-1)) * br_w.lep),
)

br_z = DotDict(
    qq=Number(0.69911, {"br_z_qq": 0.00056}),
    clep=Number(0.033658, {"br_z_clep": 0.000023}) * n_leps,
)

br_h = DotDict(
    ww=Number(0.2152, {"br_h_ww": (0.0153j, 0.0152j)}),
    zz=Number(0.02641, {"br_h_zz": (0.0153j, 0.0152j)}),
    gg=Number(0.002270, {"br_h_gg": (0.0205j, 0.0209j)}),
    bb=Number(0.5809, {"br_h_bb": (0.0124j, 0.0126j)}),
    tt=Number(0.06256, {"br_h_tt": (0.0165j, 0.0163j)}),
)


#
# processes
#

# ttbar
# https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO?rev=16#Top_quark_pair_cross_sections_at
# use mtop = 172.5 GeV, see
# https://twiki.cern.ch/twiki/bin/view/CMS/TopMonteCarloSystematics?rev=7#mtop
tt = Process(
    name="tt",
    id=1000,
    label=r"$t\bar{t}$ + Jets",
    color=(128, 76, 153),
    xsecs={
        13: Number(831.76, {
            "scale": (19.77, 29.20),
            "pdf": 35.06,
            "mtop": (23.18, 22.45),
        }),
    },
)
tt_sl = tt.add_process(
    name="tt_sl",
    id=1100,
    label=f"{tt.label}, SL",
    xsecs={
        13: tt.get_xsec(13) * br_ww.sl,
    },
)
tt_dl = tt.add_process(
    name="tt_dl",
    id=1200,
    label=f"{tt.label}, DL",
    xsecs={
        13: tt.get_xsec(13) * br_ww.dl,
    },
)
tt_fh = tt.add_process(
    name="tt_fh",
    id=1300,
    label=f"{tt.label}, FH",
    xsecs={
        13: tt.get_xsec(13) * br_ww.fh,
    },
)


# single-top
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SingleTopSigma?rev=12#Single_Top_Cross_sections_at_13
st = Process(
    name="st",
    id=2000,
    label=r"Single $t$/$\bar{t}$",
    color=(205, 0, 9),
)
st_tchannel = st.add_process(
    name="st_tchannel",
    id=2100,
    label=f"{st.label}, t-channel",
    color=(205, 0, 9),
    xsecs={
        13: Number(216.99, dict(
            scale=(6.62, 4.64),
            pdf=6.16,  # includes alpha_s
            mtop=1.81,
        )),
    },
)
st_twchannel = st.add_process(
    name="st_twchannel",
    id=2200,
    label=f"{st.label}, tW-channel",
    color=(235, 230, 10),
    xsecs={
        13: Number(71.7, dict(
            scale=1.8,
            pdf=3.4,
        )),
    },
)
st_schannel = st.add_process(
    name="st_schannel",
    id=2300,
    label=f"{st.label}, s-channel",
    color=(255, 153, 0),
    xsecs={
        13: Number(11.36, dict(
            scale=0.18,
            pdf=(0.40, 0.45),
        )),
    },
)

# define the combined single top cross section as the sum of the three channels
st.set_xsec(
    13,
    st_tchannel.get_xsec(13) + st_twchannel.get_xsec(13) + st_schannel.get_xsec(13),
)


# w+jets
w = Process(
    name="w",
    id=6000,
    label="W + Jets",
    color=(107, 182, 81),
)
# NNLO cross section
# https://twiki.cern.ch/twiki/bin/view/CMS/StandardModelCrossSectionsat13TeV?rev=27
w_lnu = w.add_process(
    name="w_lnu",
    id=6100,
    label=rf"{w.label} ($W \rightarrow l\nu$)",
    xsecs={
        13: n_leps * Number(20508.9, dict(
            scale=(165.7, 88.2),
            pdf=770.9,
        )),
    },
)

# assign the inclusive cross section based on the value in the lnu final state
w.set_xsec(13, w_lnu.get_xsec(13) / br_w.lep)
