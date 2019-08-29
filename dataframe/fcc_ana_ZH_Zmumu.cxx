
#include <ROOT/RDataFrame.hxx>
#include "TLorentzVector.h"
#include <TSystem.h>

// FCC event datamodel includes
#include "datamodel/ParticleData.h"
#include "datamodel/LorentzVector.h"
#include "datamodel/JetData.h"
#include "datamodel/FloatValueData.h"
#include "datamodel/TaggedParticleData.h"
#include "datamodel/TaggedJetData.h"


auto _m = fcc::ParticleData();

typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager, void>  dataframe_arg_type_initial;
typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RNodeBase,void> dataframe_arg_type;
typedef ROOT::RDF::RNode dataframe_return_type;


dataframe_return_type initial_dataframe_convert( dataframe_arg_type_initial df) {
  return df;
}


double deltaR(fcc::LorentzVector v1, fcc::LorentzVector v2) {
  TLorentzVector tv1;
  tv1.SetXYZM(v1.px, v1.py, v1.pz, v1.mass);

  TLorentzVector tv2;
  tv2.SetXYZM(v2.px, v2.py, v2.pz, v2.mass);

  double deltaPhi = M_PI - std::abs(std::abs(tv1.Phi() - tv2.Phi()) - M_PI);
  double deltaEta = std::abs(tv1.Eta() - tv2.Eta());
  double result = std::sqrt(deltaPhi * deltaPhi + deltaEta * deltaEta);
  return result;
}


struct recoil {
  recoil(float arg_sqrts) : m_sqrts(arg_sqrts) {};
  float m_sqrts = 240.0;
  std::vector<fcc::LorentzVector> operator() (std::vector<fcc::ParticleData> in) {
      std::vector<fcc::LorentzVector> result;
      auto recoil_p4 = TLorentzVector(0, 0, 0, m_sqrts);
      for (auto & v1: in) {
        TLorentzVector tv1;
        tv1.SetXYZM(v1.core.p4.px, v1.core.p4.py, v1.core.p4.pz, v1.core.p4.mass);
        recoil_p4 -= tv1;
      }
      auto recoil_fcc = fcc::LorentzVector();
      recoil_fcc.px = recoil_p4.Px();
      recoil_fcc.py = recoil_p4.Py();
      recoil_fcc.pz = recoil_p4.Pz();
      recoil_fcc.mass = recoil_p4.M();
      result.push_back(recoil_fcc);
      return result;
  }
};
dataframe_return_type recoil_add_to_dataframe( dataframe_arg_type df, std::string input_column, std::string output_column, float sqrts=240.0) {
  return df.Define(output_column, recoil(sqrts), {input_column});
}

struct selectLeptons {
  selectLeptons(float arg_min_pt, float arg_max_iso) : m_min_pt(arg_min_pt), m_max_iso(arg_max_iso) {};
  float m_min_pt = 20;
  float m_max_iso = 0.4;
  std::vector<fcc::ParticleData>  operator() (std::vector<fcc::ParticleData> in, std::vector<fcc::TaggedParticleData> iso) {
    std::vector<fcc::ParticleData> result;
    result.reserve(in.size());
    for (size_t i = 0; i < in.size(); ++i) {
      auto & p = in[i];
      if (std::sqrt(std::pow(p.core.p4.px,2) + std::pow(p.core.p4.py,2)) > m_min_pt) {
        if (iso[i].tag  < m_max_iso) {
          result.emplace_back(p);
        }
      }
    }
    return result;
  }
};
dataframe_return_type select_leptons_add_to_dataframe( dataframe_arg_type df, std::string input_column, std::string input_column_iso, std::string output_column, float min_pt=20., float max_iso=0.2) {
  return df.Define(output_column, selectLeptons(min_pt, max_iso), {input_column, input_column_iso});
}

struct selectJets {
  float m_min_pt;
  bool m_btag_must_be_zero;
  selectJets(float arg_min_pt, bool arg_btag_must_be_zero) {m_min_pt = arg_min_pt; m_btag_must_be_zero = arg_btag_must_be_zero;} 
std::vector<fcc::JetData> operator()(std::vector<fcc::JetData> in, std::vector<fcc::TaggedJetData> btags) {
  std::vector<fcc::JetData> result;
  result.reserve(in.size());
  for (size_t i = 0; i < in.size(); ++i) {
    auto & p = in[i];
    if (std::sqrt(std::pow(p.core.p4.px,2) + std::pow(p.core.p4.py,2)) > m_min_pt) {
      if (m_btag_must_be_zero) {
        if (btags[i].tag > 0) {
          result.emplace_back(p);
        }
      } else {
        if (btags[i].tag == 0) {
          result.emplace_back(p);
        }
      }
    }
  }
  return result;
}
};
dataframe_return_type selectJets_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string input_column_btags, std::string output_column, float arg_min_pt=20, bool arg_btag_must_be_zero=false) {
  return df.Define(output_column, selectJets(arg_min_pt, arg_btag_must_be_zero), {input_column, input_column_btags});
}

struct noMatchJets {
  float m_max_rel_iso;
  // constructor
  noMatchJets(float arg_max_rel_iso) {m_max_rel_iso = arg_max_rel_iso;};
  std::vector<fcc::JetData> operator() (std::vector<fcc::JetData> in, std::vector<fcc::ParticleData> matchParticles) {
    std::vector<fcc::JetData> result;
    result.reserve(in.size());
    for (size_t i = 0; i < in.size(); ++i) {
      auto & p = in[i];
      bool matched = false;
      for (size_t j = 0; j < matchParticles.size(); ++j) {
        auto & matchCandidate = matchParticles[j];
        if (deltaR(p.core.p4, matchCandidate.core.p4) < m_max_rel_iso) {
          matched = true;
        }
      }
      if (matched == false) {
        result.emplace_back(p);
      }
    }
    return result;
  }
};
dataframe_return_type noMatchJets_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string input_column_matchParticles, std::string output_column, float  max_rel_iso) {
  return df.Define(output_column, noMatchJets(max_rel_iso) , {input_column, input_column_matchParticles});
}

std::vector<float> get_pt(std::vector<fcc::ParticleData> in){
 std::vector<float> result;
 for (size_t i = 0; i < in.size(); ++i) {
   result.push_back(sqrt(in[i].core.p4.px * in[i].core.p4.px + in[i].core.p4.py * in[i].core.p4.py));
 }
 return result;
}

dataframe_return_type get_pt_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column) {
  return df.Define(output_column, get_pt, {input_column});
}


std::vector<fcc::ParticleData> mergeParticles(std::vector<fcc::ParticleData> x, std::vector<fcc::ParticleData> y) {
  std::vector<fcc::ParticleData> result;
  result.reserve(x.size() + y.size());
  result.insert( result.end(), x.begin(), x.end() );
  result.insert( result.end(), y.begin(), y.end() );
  return result;
}

dataframe_return_type mergeParticles_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string input_column2, std::string output_column) {
  return df.Define(output_column, mergeParticles, {input_column, input_column2});
}


struct ResonanceBuilder {
  int m_resonance_pdgid;
  float m_resonance_mass;
  ResonanceBuilder(int arg_resonance_pdgid, float arg_resonance_mass) {m_resonance_pdgid = arg_resonance_pdgid; m_resonance_mass = arg_resonance_mass;}
std::vector<fcc::ParticleData> operator()(std::vector<fcc::ParticleData> leptons) {
  std::vector<fcc::ParticleData> result;
  int n = leptons.size();
  if (n >2) {
    std::vector<bool> v(n);
    std::fill(v.end() - 2, v.end(), true);
    do {
      fcc::ParticleData zed;
      zed.core.pdgId = m_resonance_pdgid;
      TLorentzVector zed_lv; 
      for (int i = 0; i < n; ++i) {
          if (v[i]) {
            zed.core.charge += leptons[i].core.charge;
            TLorentzVector lepton_lv;
            lepton_lv.SetXYZM(leptons[i].core.p4.px, leptons[i].core.p4.py, leptons[i].core.p4.pz, leptons[i].core.p4.mass);
            zed_lv += lepton_lv;
          }
      }
      zed.core.p4.px = zed_lv.Px();
      zed.core.p4.py = zed_lv.Py();
      zed.core.p4.pz = zed_lv.Pz();
      zed.core.p4.mass = zed_lv.M();
      result.emplace_back(zed);
    } while (std::next_permutation(v.begin(), v.end()));
  }
  if (result.size() > 1) {
    auto  higgsresonancesort = [&] (fcc::ParticleData i ,fcc::ParticleData j) { return (abs( m_resonance_mass -i.core.p4.mass)<abs(m_resonance_mass-j.core.p4.mass)); };
    std::sort(result.begin(), result.end(), higgsresonancesort);
    std::vector<fcc::ParticleData>::const_iterator first = result.begin();
    std::vector<fcc::ParticleData>::const_iterator last = result.begin() + 1;
    std::vector<fcc::ParticleData> onlyBestHiggs(first, last);
    return onlyBestHiggs;
  } else {
    return result;
  }
}
};
dataframe_return_type resonancebuilder_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column, int arg_resonance_pdgid=25, float arg_resonance_mass=125.) {
  return df.Define(output_column, ResonanceBuilder(arg_resonance_pdgid, arg_resonance_mass), {input_column});
}

std::vector<float> id_float(std::vector<fcc::FloatValueData> x) {
  std::vector<float> result;
  for (auto & p: x) {
    result.push_back(p.value);
  }
  return result;
}

std::vector<float> get_mass(std::vector<fcc::ParticleData> x) {
  std::vector<float> result;
  for (auto & p: x) {
    result.push_back(p.core.p4.mass);
  }
  return result;
}

dataframe_return_type get_mass_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column) {
  return df.Define(output_column, get_mass, {input_column});
}

int get_nparticles(std::vector<fcc::ParticleData> x) {
  int result =  x.size();
  return result;
}

dataframe_return_type get_nparticles_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column) {
  return df.Define(output_column, get_nparticles, {input_column});
}

int get_njets(std::vector<fcc::JetData> x) {
  int result =  x.size();
  return result;
}

dataframe_return_type get_njets_add_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column) {
  return df.Define(output_column, get_njets, {input_column});
}

int get_njets2(std::vector<fcc::JetData> x, std::vector<fcc::JetData> y) {
  int result =  x.size() + y.size();
  return result;
}

dataframe_return_type add_njets2_to_dataframe(dataframe_arg_type df, std::string input_column, std::string output_column) {
  return df.Define(output_column, get_njets2, {input_column});
}






/*

// Reproduce Heppy analysis
int main(int argc, char* argv[]){


   #ifdef ENABLEIMPLICITMT
   ROOT::EnableImplicitMT();
   #endif

   // fcc edm libraries
   gSystem->Load("libdatamodel.so");

   // very basic command line argument parsing
   if (argc < 3) {
     std::cout << "error: need to specify fcc data files to analyze as command line arguments" << std::endl;
     std::cout << "usage:  fccanalysis_tth_4l outfilename.root datafile1.root datafile2.root ... datafileN.root " << std::endl;
     return 1;
   }
   std::cout << "Read files... ";
   std::vector<std::string> filenames;

   std::string outfilename = argv[1];
   for (int i = 2; i < argc; ++i) {
     std::cout << " " << argv[i];
     filenames.push_back(argv[i]);
   }
   std::cout << std::endl;
   
   std::cout << "Creating TDataFrame ..." << std::endl;
   ROOT::RDataFrame df("events", filenames);




  



  //auto noMatchJets_02 =  [&] (std::vector<fcc::JetData> in, std::vector<fcc::ParticleData> matchParticles) {return noMatchJets(in, matchParticles, 0.2);};
  auto noMatchJets_02 = noMatchJets(0.2);



   std::cout << "Apply selectors and define new branches ..." << std::endl;
   auto selectors =  df
                      .Define("selected_electrons", selectLeptons(20, 0.4), {"electrons", "electronITags"})
                      .Define("selected_muons", selectLeptons(20, 0.4), {"muons", "muonITags"})
                      .Define("selected_leptons", mergeParticles, {"selected_electrons", "selected_muons"})
                      .Define("zeds", ResonanceBuilder(23, 91.1), {"selected_leptons"})
                      .Define("recoil", recoil(240.0), {"zeds"})
                      .Define("selected_leptons_pt", get_pt, {"selected_leptons"})
                      .Define("zeds_pt", get_pt, {"zeds"})
                      .Define("higgs", ResonanceBuilder(25, 125.), {"zeds"})
                      .Define("higgs_m", get_mass, {{"higgs"}})
                      .Define("higgs_pt", get_pt, {"higgs"})
                      .Define("jets_30_bs", selectJets(20, false), {"pfjets", "pfbTags"})
                      .Define("jets_30_lights", selectJets(20, true), {"pfjets", "pfbTags"})
                      .Define("selected_bs", noMatchJets_02, {"jets_30_bs", "selected_leptons"})
                      .Define("selected_lights", noMatchJets_02, {"jets_30_lights", "selected_leptons"})
                      .Define("nbjets", get_njets, {"selected_bs"})
                      .Define("njets", get_njets2, {"selected_bs", "selected_lights"})
                      .Define("weight", id_float, {"mcEventWeights"})
                      .Define("n_selected_leptons", get_nparticles, {"selected_leptons"})
                    ;
  auto nentries = selectors.Count();
  std::cout << "Count events: " <<  *nentries << std::endl;
  std::cout << "Writing snapshot to disk ... \t" << outfilename << std::endl;
  selectors.Snapshot("events", outfilename,
    { 
      // fcc particles with additional infos
      //"zeds",
      //"zeds_pt",
      //"selected_muons",
      //"selected_leptons",
      //"selected_electrons",
      //"selected_bs",
      //"selected_lights",
      //"higgs",
      "selected_leptons_pt",
      "higgs_pt",
      "higgs_m",
      "nbjets",
      "njets",
      "weight"

      }
    );

   return 0;
}
*/
