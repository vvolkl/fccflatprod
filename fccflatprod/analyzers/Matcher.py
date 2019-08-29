
import ROOT
from ROOT import noMatchJets_add_to_dataframe

class Matcher:
  def __init__(self, *args, **kwargs):
    self.delta_r = kwargs["delta_r"]
    self.match_particles = kwargs["match_particles"]
    self.particles = kwargs["particles"]

  def doit(self, dataframe):

    print "Matcher doit"
    #noMatchJets_add_to_dataframe(dataframe, self.particles, self.delta_r)
    return dataframe

