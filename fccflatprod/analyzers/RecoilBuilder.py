import ROOT
from ROOT import recoil_add_to_dataframe


class RecoilBuilder:
  def __init__(self, *args, **kwargs):
    self.output = kwargs["output"]
    self.sqrts = kwargs["sqrts"]
    self.to_remove = kwargs["to_remove"]
    pass
  def doit(self, dataframe):
    dataframe = recoil_add_to_dataframe(dataframe, self.to_remove, self.output, self.sqrts)
    return dataframe

    
