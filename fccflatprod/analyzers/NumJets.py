import ROOT
from ROOT import get_njets_add_to_dataframe


class NumJets:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.input_objects = kwargs["input_objects"]

  def doit(self, dataframe):
    return get_njets_add_to_dataframe(dataframe, self.input_objects, self.output)
    
    
