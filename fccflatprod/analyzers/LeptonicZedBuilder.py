import ROOT
from ROOT import resonancebuilder_add_to_dataframe 

class LeptonicZedBuilder:
  def __init__(self, *args, **kwargs):
    self.output_column = kwargs["output"]
    self.input_column = kwargs["leptons"]
    self.resonance_pdgid = kwargs["pdgid"]
    self.resonance_mass = kwargs["resonance_mass_for_sort"]
    pass
  def doit(self, dataframe):
    dataframe = resonancebuilder_add_to_dataframe(dataframe, self.input_column, self.output_column, self.resonance_pdgid, self.resonance_mass) 
    print "LeptonicZedBuilder doit"
    return dataframe
