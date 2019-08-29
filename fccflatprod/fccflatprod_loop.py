
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
print "Load cxx analyzers ... ",
ROOT.gSystem.Load("fcc_ana_ZH_Zmumu_cxx")
print ""


print "Parsing config file " , sys.argv[1], " ... ",
if __name__ == "__main__":
  execfile(sys.argv[1])
print "done"


print "Create dataframe object from ", comp.files[0], " ... ", 
df = ROOT.RDataFrame("events", comp.files[0])
df = ROOT.initial_dataframe_convert(df)
print " done"


print "Running Sequence of Analyzers ...",
for ana in sequence.the_sequence:
  df = ana.doit(df)
print " done"

print "New Columns: ",
print df.GetDefinedColumnNames()
