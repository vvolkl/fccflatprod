
import sys

try:
  import heppy
  del sys.modules["heppy"]
  import FCCeeAnalyses
except:
  pass
try:
  import FCCeeAnalyses
  del sys.modules["FCCeeAnalyses"]
except:
  pass

print "replacing heppy with fccflatprod ...",
sys.modules["fccflatprod"] = __import__("fccflatprod")
sys.modules["heppy"] = __import__("fccflatprod")
sys.modules["FCCeeAnalyses"] = __import__("fccflatprod")
print "done"

import ROOT

#TODO: change library name
ROOT.gSystem.Load("fcc_ana_ZH_Zmumu_cxx")


if __name__ == "__main__":
  execfile(sys.argv[1])


global df
df = ROOT.RDataFrame("events", comp.files[0])
df = ROOT.initial_dataframe_convert(df)
print df

if False: 
  from ROOT import select_leptons_add_to_dataframe 
  from ROOT import initial_dataframe_convert
  df = select_leptons_add_to_dataframe(df, "muons", "muonITags", "selected_muons")
  print df
  df = recoil_add_to_dataframe(df, "muons",  "recoil")
  print df


for ana in sequence.the_sequence:
  print ana
  df = ana.doit(df)

print df.GetDefinedColumnNames()
