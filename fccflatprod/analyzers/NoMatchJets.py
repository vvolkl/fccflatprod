import ROOT
from ROOT import noMatchJets_add_to_dataframe


class NoMatchJets:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.delta_r = kwargs["delta_r"]
    self.match_particles = kwargs["match_particles"]
    self.particles = kwargs["particles"]

  def doit(self, dataframe):
    return noMatchJets_add_to_dataframe(dataframe, self.particles, self.match_particles, self.output, self.delta_r)
    
    
