# coding: utf-8

"""
Configuration of the analysis.
"""

from __future__ import annotations

import os
import re

import law
import order as od
from scinum import Number

from columnflow.util import DotDict
from columnflow.columnar_util import EMPTY_FLOAT
from columnflow.config_util import (
    get_root_processes_from_campaign, add_category, verify_config_processes, add_shift_aliases,
)


#
# the main analysis object
#

analysis_agc = ana = od.Analysis(
    name="analysis_agc",
    id=1,
)

# analysis-global versions
ana.x.versions = {}

# files of bash sandboxes that might be required by remote tasks
# (used in cf.HTCondorWorkflow)
ana.x.bash_sandboxes = [
    "$CF_BASE/sandboxes/cf_prod.sh",
    "$CF_BASE/sandboxes/venv_columnar.sh",
]

# files of cmssw sandboxes that might be required by remote tasks
# (used in cf.HTCondorWorkflow)
ana.x.cmssw_sandboxes = []

# clear the list when cmssw bundling is disabled
if not law.util.flag_to_bool(os.getenv("AGC_BUNDLE_CMSSW", "1")):
    del ana.x.cmssw_sandboxes[:]

# config groups for conveniently looping over certain configs
# (used in wrapper_factory)
ana.x.config_groups = {}


#
# setup configs
#

from agc.config.cms_open_data_2015 import campaign_cms_opendata_2015_agc, agc_files


def add_config(
    campaign: od.Campaign,
    config_name: str | None = None,
    config_id: int | None = None,
    limit_dataset_files: int | None = None,
) -> od.Config:
    """
    Factory function for creating a config.
    """
    # get all root processes
    procs = get_root_processes_from_campaign(campaign)

    # create a config by passing the campaign, so id and name will be identical
    cfg = ana.add_config(campaign, name=config_name, id=config_id)

    # add processes we are interested in
    process_names = [
        "tt",
        "st",
        "w",
    ]
    for process_name in process_names:
        cfg.add_process(procs.get(process_name))

    # add datasets we need to study
    dataset_names = [
        "tt_powheg",
        "st_schannel_amcatnlo",
        "st_tchannel_powheg",
        "st_twchannel_powheg",
        "wjets_amcatnlo",
    ]
    for dataset_name in dataset_names:
        dataset = cfg.add_dataset(campaign.get_dataset(dataset_name))

        # for testing purposes, limit the number of files to 2
        if limit_dataset_files:
            for info in dataset.info.values():
                info.n_files = min(info.n_files, limit_dataset_files)

    # verify that the root process of all datasets is part of any of the registered processes
    verify_config_processes(cfg, warn=True)

    # default objects, such as calibrator, selector, producer, ml model, inference model, etc
    cfg.x.default_calibrator = "default"
    cfg.x.default_selector = "default"
    cfg.x.default_producer = "default"
    cfg.x.default_ml_model = None
    cfg.x.default_inference_model = "ttbar_model"
    cfg.x.default_categories = ("preselection",)
    cfg.x.default_variables = ("n_jet", "jet1_pt", "e1_pt")

    # process groups for conveniently looping over certain processs
    # (used in wrapper_factory and during plotting)
    cfg.x.process_groups = {
        "default": ["tt", "st", "w"],
        "st_split": ["tt", "st_tchannel", "st_schannel", "st_twchannel", "w"],
    }

    # dataset groups for conveniently looping over certain datasets
    # (used in wrapper_factory and during plotting)
    cfg.x.dataset_groups = {}

    # category groups for conveniently looping over certain categories
    # (used during plotting)
    cfg.x.category_groups = {}

    # variable groups for conveniently looping over certain variables
    # (used during plotting)
    cfg.x.variable_groups = {}

    # shift groups for conveniently looping over certain shifts
    # (used during plotting)
    cfg.x.shift_groups = {}

    # selector step groups for conveniently looping over certain steps
    # (used in cutflow tasks)
    cfg.x.selector_step_groups = {
        "default": ["lepton", "jet", "btag"],
    }

    # lumi values in inverse pb
    cfg.x.luminosity = Number(3378.0, {f"lumi_{campaign.ecm}TeV": 0.03j})

    # register shifts
    cfg.add_shift(name="nominal", id=0)
    cfg.add_shift(name="scale_up", id=1, type="shape", tags={"disjoint_from_nominal"})
    cfg.add_shift(name="scale_down", id=2, type="shape", tags={"disjoint_from_nominal"})
    cfg.add_shift(name="jes_up", id=3, type="shape")
    cfg.add_shift(name="jes_down", id=4, type="shape")
    add_shift_aliases(cfg, "jes", {"Jet.pt": "Jet.pt_{name}"})
    cfg.add_shift(name="jer_up", id=5, type="shape")
    cfg.add_shift(name="jer_down", id=6, type="shape")
    add_shift_aliases(cfg, "jer", {"Jet.pt": "Jet.pt_{name}"})

    # external files
    # (none yet)
    cfg.x.external_files = DotDict()

    # target file size after MergeReducedEvents in MB
    cfg.x.reduced_file_size = 512.0

    # columns to keep after certain steps
    cfg.x.keep_columns = DotDict.wrap({
        "cf.ReduceEvents": {
            # general event info
            "run", "luminosityBlock", "event",
            # object info
            "Electron.pt", "Electron.eta", "Electron.phi", "Electron.mass",
            "Muon.pt", "Muon.eta", "Muon.phi", "Muon.mass",
            "Jet.pt", "Jet.eta", "Jet.phi", "Jet.mass", "Jet.btagCSVV2", "Jet.qgl",
            "BJet.pt", "BJet.eta", "BJet.phi", "BJet.mass", "BJet.btagCSVV2", "BJet.qgl",
            "MET.pt", "MET.phi",
            "PV.npvs",
            # columns added during selection
            "process_id", "mc_weight", "cutflow.*",
        },
        "cf.MergeSelectionMasks": {
            "normalization_weight", "process_id", "category_ids", "cutflow.*",
        },
        "cf.UniteColumns": {
            "*",
        },
    })

    # event weight columns as keys in an OrderedDict, mapped to shift instances they depend on
    # (none yet)
    cfg.x.event_weights = DotDict()

    # versions per task family and optionally also dataset and shift
    # None can be used as a key to define a default value
    cfg.x.versions = {
        # "cf.CalibrateEvents": "prod1",
        # ...
    }

    # customization of the lfn retrieval in GetDatasetLFNs to detect files in the agc file list
    def get_dataset_lfns(
        dataset_inst: od.Dataset,
        shift_inst: od.Shift,
        dataset_key: str,
    ) -> list[str]:
        # get process and systematic names as used by the agc
        agc_process = dataset_inst.x.agc_process
        agc_syst = dataset_inst.x("agc_shifts", {}).get(shift_inst.name, shift_inst.name)
        # retrieve and return data
        return [
            re.match("^https?://.*(/store/.+)$", data["path"]).group(1)
            for data in agc_files[agc_process][agc_syst]["files"]
        ]

    cfg.x.get_dataset_lfns = get_dataset_lfns
    cfg.x.get_dataset_lfns_sandbox = ""
    cfg.x.get_dataset_lfns_remote_fs = lambda dataset_inst: campaign.x.wlcg_fs

    # add categories using the "add_category" tool which adds auto-generated ids
    # the "selection" entries refer to names of selectors, e.g. in selection/example.py
    add_category(
        cfg,
        name="preselection",
        selection="cat_pre",
        label="Pre-selection",
    )
    add_category(
        cfg,
        name="ge4j_eq1b",
        selection="cat_ge4j_eq1b",
        label=r"$\geq 4$ jets, $1$ b-tag",
    )
    add_category(
        cfg,
        name="ge4j_ge2b",
        selection="cat_ge4j_ge2b",
        label=r"$\geq 4$ jets, $\geq 2$ b-tags",
    )

    # add variables
    # (the "event", "run" and "lumi" variables are required for some cutflow plotting task,
    # and also correspond to the minimal set of columns that coffea's nano scheme requires)
    cfg.add_variable(
        name="event",
        expression="event",
        binning=(1, 0.0, 1.0e9),
        x_title="Event number",
        discrete_x=True,
    )
    cfg.add_variable(
        name="n_jet",
        expression="n_jet",
        binning=(11, -0.5, 10.5),
        x_title="Number of jets",
        discrete_x=True,
    )
    cfg.add_variable(
        name="jet1_pt",
        expression="Jet.pt[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Jet 1 $p_{T}$",
    )
    cfg.add_variable(
        name="e1_pt",
        expression="Electron.pt[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Electron $p_{T}$",
    )
    cfg.add_variable(
        name="mu1_pt",
        expression="Muon.pt[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Muon $p_{T}$",
    )
    cfg.add_variable(
        name="ht",
        expression="ht",
        null_value=EMPTY_FLOAT,
        binning=(50, 100.0, 600.0),
        unit="GeV",
        x_title=r"$H_{T}$",
    )
    cfg.add_variable(
        name="trijet_mass",
        expression="trijet_mass",
        null_value=EMPTY_FLOAT,
        binning=(50, 50.0, 550.0),
        unit="GeV",
        x_title="Trijet mass",
    )
    # cutflow variables
    cfg.add_variable(
        name="cutflow_jet1_pt",
        expression="cutflow.jet1_pt",
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Jet 1 $p_{T}$",
    )


# default config
add_config(
    campaign=campaign_cms_opendata_2015_agc.copy(),
    config_name=campaign_cms_opendata_2015_agc.name,
    config_id=1,
)

# limited test config with just 2 files per dataset
add_config(
    campaign=campaign_cms_opendata_2015_agc.copy(),
    config_name=f"{campaign_cms_opendata_2015_agc.name}_limited",
    config_id=2,
    limit_dataset_files=2,
)
