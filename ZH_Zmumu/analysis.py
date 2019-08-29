import os, sys
import copy
import heppy.framework.config as cfg
import logging

# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

sys.path.append('/afs/cern.ch/work/h/helsens/public/FCCDicts/')

comp = cfg.Component(
    'example',
     files = ["root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/fcc_v01/p8_ee_ZH_ecm240/events_067271769.root"]
)

from FCCee_heppySampleList_fcc_v01 import *

selectedComponents = [
                      p8_ee_ZH_ecm240,
                      p8_ee_ZZ_ecm240,
                      p8_ee_WW_ecm240
		      ]


comp=p8_ee_ZH_ecm240
#print comp

p8_ee_ZH_ecm240.splitFactor = 10
p8_ee_ZZ_ecm240.splitFactor = 10
p8_ee_WW_ecm240.splitFactor = 10

#selectedComponents = [comp]


from FCCeeAnalyses.analyzers.Reader import Reader

source = cfg.Analyzer(
    Reader,

    weights = 'mcEventWeights',

    gen_particles = 'skimmedGenParticles',
    
    muons = 'muons',
    muonITags = 'muonITags',
    muonsToMC = 'muonsToMC',

    pfjets = 'pfjets',
    pfbTags = 'pfbTags',
    pfcTags = 'pfcTags',

    photons = 'photons',
    
    pfphotons = 'pfphotons',
    pfcharged = 'pfcharged',
    pfneutrals = 'pfneutrals',

    met = 'met',

)

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events


#############################
##   Reco Level Analysis   ##
#############################


'''
####### ADVANCED ANALYSIS (double check workflow) ######################)

# select fsr photon candidates
from heppy.analyzers.Selector import Selector
sel_photons = cfg.Analyzer(
    Selector,
    'sel_photons',
    output = 'sel_photons',
    input_objects = 'photons',
    filter_func = lambda ptc: ptc.pt()>2
)

# produce particle collection to be used for fsr photon isolation
from heppy.analyzers.Merger import Merger
iso_candidates = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates', 
      inputs = ['pfphotons','pfcharged','pfneutrals'],
      output = 'iso_candidates'
)
# compute fsr photon isolation w/r other particles in the event.
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle

iso_photons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'photons',
    particles = 'iso_candidates',
    iso_area = EtaPhiCircle(0.3)
)

# select isolated photons
sel_iso_photons = cfg.Analyzer(
    Selector,
    'sel_iso_photons',
    output = 'sel_iso_photons',
    input_objects = 'sel_photons',
    filter_func = lambda ptc : ptc.iso.sumpt/ptc.pt()<1.0
)

# remove fsr photons from particle-flow photon collections
from heppy.analyzers.Subtractor import Subtractor
pfphotons_nofsr = cfg.Analyzer(
      Subtractor,
      instance_label = 'pfphotons_nofsr', 
      inputA = 'pfphotons',
      inputB = 'sel_iso_photons',
      output = 'pfphotons_nofsr'
)

# produce particle collection to be used for lepton isolation
iso_candidates_nofsr = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates_nofsr', 
      inputs = ['pfphotons_nofsr','pfcharged','pfneutrals'],
      output = 'iso_candidates_nofsr'
)

# select muons with pT > 10
from heppy.analyzers.Selector import Selector
sel_muons = cfg.Analyzer(
    Selector,
    'sel_muons',
    output = 'sel_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>10
)

# compute muon isolation 
iso_muons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'sel_muons',
    particles = 'iso_candidates_nofsr',
    iso_area = EtaPhiCircle(0.4)
)

# "dress" muons with fsr photons
from heppy.analyzers.LeptonFsrDresser import LeptonFsrDresser
dressed_muons = cfg.Analyzer(
    LeptonFsrDresser,
    output = 'dressed_muons',
    particles = 'sel_iso_photons',
    leptons = 'sel_iso_muons',
    area = EtaPhiCircle(0.3)
)
'''

######################## SIMPLE ANALYSIS #####################


from FCCeeAnalyses.analyzers.PtIsoSelector import PtIsoSelector

# select isolated muons
dressed_muons = cfg.Analyzer(
    PtIsoSelector,
    'dressed_muons',
    output = 'dressed_muons',
    input_objects = 'muons',
    input_iTags = 'muonITags',
    min_pt = 10,
    max_rel_iso = 0.4,
)

###############################################################




from FCCeeAnalyses.analyzers.SelectJetsMatchPtTag import SelectJetsMatchPtTag
# select lights with pT > 10 GeV and relIso < 0.4
selected_lights = cfg.Analyzer(
    SelectJetsMatchPtTag,
    'selected_lights',
    output = 'selected_lights',
    input_objects = 'pfjets',
    min_pt = 10,
    btags = "pfbTags",
    btag_must_be_zero = True,
    delta_r = 0.2,
    matchParticles = 'dressed_muons',
)

# select b's with pT > 10 GeV
selected_bs = cfg.Analyzer(
    SelectJetsMatchPtTag,
    'selected_bs',
    output = 'selected_bs',
    input_objects = 'pfjets',
    min_pt = 10,
    btags = "pfbTags",
    btag_must_be_zero = False,
    delta_r = 0.2,
    matchParticles = 'dressed_muons',
)

# create H boson candidates with bs
from FCCeeAnalyses.analyzers.LeptonicZedBuilder import LeptonicZedBuilder
zeds = cfg.Analyzer(
      LeptonicZedBuilder,
      output = 'zeds',
      leptons = 'muons',
      pdgid = 23,
      resonance_mass_for_sort = 91.1
)

from heppy.analyzers.RecoilBuilder import RecoilBuilder
recoil = cfg.Analyzer(
    RecoilBuilder,
    output = 'recoil',
    sqrts = 240.,
    to_remove = 'zeds'
) 

# apply event selection. Defined in "analyzers/examples/hmumu/selection.py"
from FCCeeAnalyses.ZH_Zmumu.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

# store interesting quantities into flat ROOT tree
from FCCeeAnalyses.ZH_Zmumu.TreeProducer import TreeProducer
reco_tree = cfg.Analyzer(
    TreeProducer,
    zeds = 'zeds',
    recoil = 'recoil',
)

from FCCeeAnalyses.analyzers.NumJets import NumJets
nbjets = cfg.Analyzer(
    NumJets,
    input_objects = "selected_bs",
    output = "nbjets",
    write_to_file = True,
)


from FCCeeAnalyses.analyzers.NumJets import NumJets
nljets = cfg.Analyzer(
    NumJets,
    input_objects = "selected_lights",
    output = "nljets",
    write_to_file = True
)

from FCCeeAnalyses.analyzers.GetPt import GetPt
zeds_pt = cfg.Analyzer(
    GetPt,
    input_objects = "zeds",
    output = "zeds_pt",
    write_to_file = True,
)

from FCCeeAnalyses.analyzers.GetPt import GetPt
recoil_pt = cfg.Analyzer(
    GetPt,
    input_objects = "recoil",
    output = "recoil_pt",
    write_to_file=True
)



# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    dressed_muons,
    selected_lights,
    selected_bs,
    nljets,
    nbjets,
    zeds,
    recoil,
    zeds_pt,
    recoil_pt,
    selection,
    reco_tree,
    ] )

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    def next():
        loop.process(loop.iEvent+1)

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    loop.process(6)
    print loop.event
