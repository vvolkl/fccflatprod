import ROOT
from ROOT import selectParticlesPtIso_add_to_dataframe


class PtIsoSelector:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.input_objects =  kwargs["input_objects"]
    self.min_pt = kwargs["min_pt"]
    self.max_rel_iso = kwargs["max_rel_iso"]
    self.input_iTags = kwargs["input_iTags"]

  def doit(self, dataframe):
    return  selectParticlesPtIso_add_to_dataframe(dataframe, self.input_objects, self.input_iTags, self.output, self.min_pt, self.max_rel_iso )
    
    
