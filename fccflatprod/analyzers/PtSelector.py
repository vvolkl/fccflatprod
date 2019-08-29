import ROOT
from ROOT import selectParticlesPt_add_to_dataframe


class PtSelector:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.input_objects =  kwargs["input_objects"]
    self.min_pt = kwargs["min_pt"]

  def doit(self, dataframe):
    ##print "PtSelector doit"
    dataframe = selectParticlesPt_add_to_dataframe(dataframe, self.input_objects, self.output, self.min_pt)
    return dataframe
    
    
