# Object selection and corrections



## Trigger flags
For each period trigger flags are requested for "SingleEle", "DoubleEle", "SingleMu", "DoubleMu". 
MC are required to pass at least one of the trigger, the Primary Dataset of data instead have their own flags.

### Run period
In order to apply specific Trigger SF and Leptons SF that are computed for each era, a run era (i.e. `run_period`) is assigned to each MC and data event.
A correctionlib map is used for data, assigning each run to the proper era.
For MC random run_periods are generated based on the integrated lumi of each era.


## MET filters
For each year a set of flags is required to pass the so called MET filters.

## Jet selection
Jets are selected from AK4CHS having a tightId, $p_{T} > 15.0\;\textrm{GeV}$ and $|\eta|<4.7$.

A loose puID is also required for Jets with $p_{T} < 50.0\;\textrm{GeV}$ with an appropriate bitshift that takes into account the bug in 2016.

# Lepton selection

Electron and Muon are merged into a single collection that has only $|pdgId| == 11 \lor |pdgId| == 13$.
Leptons are selected to pass at least the loose selection. Different tight selections are applied for each year.
Events are required to have at least two loose leptons.
Leptons are also filtered removing $p_{T} < 8.0\;\textrm{GeV}$.

## Jet cleaning
Jets that overlap with loose leptons that have a $p_{T} > 10.0\;\textrm{GeV}$ with a $\Delta R <0.3$ are removed.


### Prompt gen matching
The two leading leptons are required to be gen matched with prompt leptons

# Corrections

## Muon Scale
Rochester corrections are applied.

## PU Weight SF
Applied

## Trigger SF and EMTFbug veto
Applied

## Leptons SF
Applied


## Jets veto, HEM issue, JEC and JER
The HEM issue is fixed by removing jets that lie in the HEM window.

Jets are vetod with the jetsvetomap from the JME pog. 

L1L2L3Res JEC are applied to both MC and Data. 

We apply the Jet Energy Resolution only to jets that have $|\eta| < 2.5$.


## PUID SF
Applied

## B-tag SF
Applied

## L1PreFiring 
Applied

# Analysis Selections

The two leading leptons are required to be tight ID, same flavour and opposite charge.
They are divided into two categories, namely `ee` and `mm`.

Jets are taken with $p_{T} > 30\;\textrm{GeV}$.

## DY Gen Filters

For the Jet binned sample it's necessary to require that at LHE level the number of leptons is 2 and that $m_{ll} > 50\;\textrm{GeV}$.

Events where a prompt gen photon is produced with $p_{T} > 15\;\textrm{GeV}$ and $|\eta| < 2.6$ are removed.

Events in the DY datasets are split into Hard Jets and PU Jets.
The former is defined by requiring that the two leading jets are gen matched. PU Jets is the logical negation of hard Jets.


