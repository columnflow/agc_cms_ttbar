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

... to be continued
```

### Resources

#### Analysis Grand Challenge

- [agc](https://iris-hep.org/projects/agc.html)
- [agc reference implementation](https://github.com/iris-hep/analysis-grand-challenge/tree/main/analyses/cms-open-data-ttbar)

#### Columnflow and related tools

- [columnflow](https://github.com/uhh-cms/columnflow)
- [law](https://github.com/riga/law)
- [order](https://github.com/riga/order)
- [luigi](https://github.com/spotify/luigi)
