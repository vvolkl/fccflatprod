import ROOT
from ROOT import selectJets_add_to_dataframe


class SelectJets:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.input_objects = kwargs["input_objects"]
    self.min_pt = kwargs["min_pt"]
    self.btag_must_be_zero = kwargs["btag_must_be_zero"]

  def doit(self, dataframe):
    return selectJets_add_to_dataframe(dataframe, self.input_objects, self.)
    
    
