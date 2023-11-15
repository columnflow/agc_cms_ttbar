# Analysis Grand Challenge with CMS OpenData using columnflow

### Installation

```shell
# clone
git clone --recursive git@github.com:columnflow/agc_cms_ttbar.git
cd agc_cms_ttbar

# setup (using a distinct setup name)
source setup.sh agc

# create a grid proxy
# if voms-proxy-init is not available to you, try /cvmfs/grid.cern.ch/centos7-umd4-ui-211021/usr/bin/voms-proxy-init
# also, requesting a specific voms is optional
voms-proxy-init -rfc -valid "196:00" [-voms cms]
```

### Create plots

```shell
# create plots locally with
#   - the limited config (just two input files per dataset)
#   - 4 local processes
# note: use "--view-cmd imgcat" only if available in your terminal for inline viewing
law run cf.PlotVariables1D \
    --config cms_opendata_2015_agc_limited \
    --categories ge4j_eq1b \
    --variables jet1_pt \
    --version dev1 \
    --view-cmd imgcat \
    --workers 4
```

### Create datacards

```shell
# create datacards locally with
#   - the limited config (just two input files per dataset)
#   - a reduced statistical model (dropped shape uncertainties)
#   - 4 local processes
law run cf.CreateDatacards \
    --config cms_opendata_2015_agc_limited \
    --inference-model ttbar_model_no_shapes \
    --version dev1 \
    --workers 4

# show task status recursively (down to dependency depth 4)
law run cf.CreateDatacards \
    --config cms_opendata_2015_agc_limited \
    --inference-model ttbar_model_no_shapes \
    --version dev1 \
    --print-status 4

# show the location of the created datacard
law run cf.CreateDatacards \
    --config cms_opendata_2015_agc_limited \
    --inference-model ttbar_model_no_shapes \
    --version dev1 \
    --print-output 0
```

Notice the same `--version` parameter as used for the plots above to reuse **intermediate results**.

### Resources

#### Analysis Grand Challenge

- [agc](https://iris-hep.org/projects/agc.html)
- [agc reference implementation](https://github.com/iris-hep/analysis-grand-challenge/tree/main/analyses/cms-open-data-ttbar)

#### Columnflow and related tools

- [columnflow](https://github.com/uhh-cms/columnflow)
- [law](https://github.com/riga/law)
- [order](https://github.com/riga/order)
- [luigi](https://github.com/spotify/luigi)
