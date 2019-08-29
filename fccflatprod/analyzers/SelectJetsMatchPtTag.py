import ROOT
from ROOT import selectJetsMatchPtTag_add_to_dataframe


class SelectJetsMatchPtTag:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.input_objects = kwargs["input_objects"]
    self.min_pt = kwargs["min_pt"]
    self.btag_must_be_zero = kwargs["btag_must_be_zero"]
    self.delta_r = kwargs['delta_r']
    self.matchParticles = kwargs["matchParticles"]
    self.btags = kwargs["btags"]

  def doit(self, dataframe):
    return selectJetsMatchPtTag_add_to_dataframe(dataframe, self.input_objects, self.btags, self.matchParticles, self.output, self.min_pt, self.delta_r, self.btag_must_be_zero)
    
    
