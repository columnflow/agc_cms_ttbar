# coding: utf-8

"""
Campaign definitions and datasets published as part of the CMS OpenData 2015 initiative
as used by the Analysis Grand Challenge.
"""

from __future__ import annotations

import os
import json

from order import Campaign, DatasetInfo

import agc.config.processes as procs


#
# campaign
#

campaign_cms_opendata_2015_agc = cpn = Campaign(
    name="cms_opendata_2015_agc",
    id=1,
    ecm=13,
    aux={
        "tier": "NanoAOD",
        "year": 2015,
        "location": "https://xrootd-local.unl.edu:1094//store/user/AGC/nanoAOD",
        "wlcg_fs": "wlcg_fs_unl",
    },
)


#
# helpers for working with the agc file list
#

# load the agc file list
agc_files_path = "$AGC_SRC_BASE/analyses/cms-open-data-ttbar/nanoaod_inputs.json"
with open(os.path.expandvars(agc_files_path), "r") as f:
    agc_files = json.load(f)


def get_dataset_info(process: str, syst: str) -> dict[str, list[str] | int]:
    # interpret the dataset "key" as the fragment after "/store/user/AGC/nanoAOD" of the first file
    return {
        "keys": [agc_files[process][syst]["files"][0]["path"].split("/")[8]],
        "n_files": len(agc_files[process][syst]["files"]),
        "n_events": agc_files[process][syst]["nevts_total"],
    }


#
# datasets
# (ids are pretty random, they would normally refer to IDs used in central databases)
#

cpn.add_dataset(
    name="tt_powheg",
    id=1,
    processes=[procs.tt],
    info={
        "nominal": DatasetInfo(**get_dataset_info("ttbar", "nominal")),
        "scale_down": DatasetInfo(**get_dataset_info("ttbar", "scaledown")),
        "scale_up": DatasetInfo(**get_dataset_info("ttbar", "scaleup")),
        # TODO: ME, PS
    },
    aux={
        "agc_process": "ttbar",
        "agc_shifts": {
            "scale_down": "scaledown",
            "scale_up": "scaleup",
        },
    },
)

cpn.add_dataset(
    name="st_schannel_amcatnlo",
    id=2,
    processes=[procs.st_schannel],
    aux={
        "agc_process": "single_top_s_chan",
    },
    **get_dataset_info("single_top_s_chan", "nominal"),
)

cpn.add_dataset(
    name="st_tchannel_powheg",
    id=3,
    processes=[procs.st_tchannel],
    aux={
        "agc_process": "single_top_t_chan",
    },
    **get_dataset_info("single_top_t_chan", "nominal"),
)

cpn.add_dataset(
    name="st_twchannel_powheg",
    id=4,
    processes=[procs.st_twchannel],
    aux={
        "agc_process": "single_top_tW",
    },
    **get_dataset_info("single_top_tW", "nominal"),
)

cpn.add_dataset(
    name="wjets_amcatnlo",
    id=5,
    processes=[procs.w],
    aux={
        "agc_process": "wjets",
    },
    **get_dataset_info("wjets", "nominal"),
)
