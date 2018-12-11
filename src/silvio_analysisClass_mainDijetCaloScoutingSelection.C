#define analysisClass_cxx
#include "analysisClass.h"
#include <TH2.h>
#include <TH1F.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector2.h>
#include <TVector3.h>
#include <TRandom3.h>

#define isMC false

using namespace std;


vector < TLorentzVector > analysisClass::doWideJets (const vector < TLorentzVector > goodjets)
{
  vector < TLorentzVector > wideJets;
  vector < fastjet::PseudoJet > fjInputs;
  for (const auto jet:goodjets) fjInputs.push_back (fastjet::PseudoJet (jet.Px (), jet.Py (), jet.Pz (), jet.E ()));
  fjClusterSeq = ClusterSequencePtr (new fastjet::ClusterSequence (fjInputs, *fjJetDefinition));
  std::vector < fastjet::PseudoJet > inclusiveWideJets_fj = fastjet::sorted_by_pt (fjClusterSeq->inclusive_jets (0.));
  for (const auto fjet:inclusiveWideJets_fj) wideJets.push_back (TLorentzVector (fjet.px (), fjet.py (), fjet.pz (), fjet.e ()));
  return wideJets;
}


bool sortByPt (TLorentzVector i, TLorentzVector j)
{
  return (i.Pt () > j.Pt ());
}

bool sortByP (TLorentzVector i, TLorentzVector j)
{
  return (i.P () > j.P ());
}

bool sortByM (TLorentzVector i, TLorentzVector j)
{
  return (i.M () > j.M ());
}

TRandom3 rnd;
float dijet_value (const TLorentzVector & jet1, const TLorentzVector & jet2, const string & method)
{
  if (method == "dijetPt") {
    return (jet1 + jet2).Pt ();
  }
  else if (method == "dijetM") {
    return (jet1 + jet2).M ();
  }
  else if (method == "dijetMn") {
    return -(jet1 + jet2).M ();
  }
  else if (method == "dijetDPhi") {
    return -abs (jet1.DeltaPhi (jet2));
  }
  else if (method == "dijetDR") {
    return -abs (jet1.DeltaR (jet2));
  }
  else if (method == "dijetPtMod") {
    float pt1 = jet1.Pt ();
    float pt2 = jet2.Pt ();
    return (jet1 * (pt2 / pt1) + jet2).Pt ();
  }
  else if (method == "dijetP") {
    return (jet1 + jet2).P ();
  }
  else if (method == "dijetPMod") {
    float pt1 = jet1.P ();
    float pt2 = jet2.P ();
    return (jet1 * (pt2 / pt1) + jet2).P ();
  }
  else if (method == "dijetEnergy") {
    return (jet1 + jet2).Energy ();
  }
  else if (method == "dijetEnergyMod") {
    float pt1 = jet1.Energy ();
    float pt2 = jet2.Energy ();
    return (jet1 * (pt2 / pt1) + jet2).Energy ();
  }
  else if (method == "crossProduct") {
    return jet1.Vect ().Cross (jet2.Vect ()).Mag ();
  }
  else if (method == "dotProduct3D") {
    return jet1.Vect ().Dot (jet2.Vect ());
  }
  else if (method == "dotProduct") {
    return jet1.Dot (jet2);
  }
  else if (method == "random") {
    return rnd.Rndm ();
  }
  else {
    cout << "ERROR: method " << method << " not found." << endl;
  }
}

pair < int, int >
find_dijet (const vector < TLorentzVector > &goodjets, const string & method, const bool & CM =
  false, const bool & CMz = false)
{
  vector < TLorentzVector > jets;
  int jet1_idx = 0, jet2_idx = 1, jet3_idx = 2;

  if (CM || CMz) {
    TLorentzVector
    trijet,
    jet1,
    jet2,
    jet3;
    trijet = goodjets.at (0) + goodjets.at (1) + goodjets.at (2);
    TVector3 boost = trijet.BoostVector ();
    if (CMz) boost.SetXYZ (0, 0, boost.Z ());
    jet1 = goodjets.at (0);
    jet2 = goodjets.at (1);
    jet3 = goodjets.at (2);

    jet1.Boost (-boost);
    jet2.Boost (-boost);
    jet3.Boost (-boost);

    jets.push_back (jet1);
    jets.push_back (jet2);
    jets.push_back (jet3);

    map < float, int >
    p_key;
    p_key[-jet1.P ()] = 0;
    p_key[-jet2.P ()] = 1;
    p_key[-jet3.P ()] = 2;

    auto it = p_key.begin ();
    jet1_idx = it->second;
    it++;
    jet2_idx = it->second;
    it++;
    jet3_idx = it->second;
  }
  else {
    jets = goodjets;
  }
  if (method == "jets01") {
    return pair < int, int >(jet1_idx, jet2_idx);
  }
  else if (method == "jets12") {
    return pair < int, int >(jet2_idx, jet3_idx);
  }
  else if (method == "jets02") {
    return pair < int, int >(jet1_idx, jet3_idx);
  }
  else {
    float tmp;
    float dijet_val = dijet_value (jets.at (0), jets.at (1), method);
    pair < int, int >
    dijet_pair = std::pair < int, int >(0, 1);
    for (int i = 0; i < jets.size (); i++) {
      for (int j = i + 1; j < jets.size (); j++) {
        tmp = dijet_value (jets.at (i), jets.at (j), method);
        if (tmp > dijet_val) {
          dijet_val = tmp;
          dijet_pair = std::pair < int, int >(i, j);
        }
      }
    }
    //        cout << "dijet_pair:" << dijet_pair.first << " " << dijet_pair.second << " " << method << endl;
    return dijet_pair;
  }
}

bool test_method (const vector < TLorentzVector > &goodjets, const TLorentzVector & dijetMCreco,
  const string & method, const bool & CM = false, const bool & CMz = false){
    pair < int, int >
    dijet_pair = find_dijet (goodjets, method, CM, CMz);
    TLorentzVector
    jet1 = goodjets.at (dijet_pair.first);
    TLorentzVector
    jet2 = goodjets.at (dijet_pair.second);

    if (fabs ((goodjets.at (dijet_pair.first) + goodjets.at (dijet_pair.second)).M () - dijetMCreco.M ()) < 1E-3) return true;
    else return false;
  }


  //tmp = (goodjets.at (i) + goodjets.at (j)).Pt ();
  //tmp = goodjets.at(i).Vect() *  goodjets.at(j).Vect();


  double biasCorrection (double pt)
  {
    // new 2016 bias correction from Federico
    // (page 10 https://www.dropbox.com/s/7sporqeim01675d/Luglio_20_2016_CaloScouting.pdf?dl=1)
    // flattened above 993.264 (point of zero slope)
    if (pt <= 0) return 1;
    float p0 = -31.7198;
    float p1 = 8.58611;
    float p2 = -0.622092;

    float f1 = 0;
    if (pt >= 993.264) f1 = p0 + p1 * log (993.264) + p2 * log (993.264) * log (993.264);
    else f1 = p0 + p1 * log (pt) + p2 * log (pt) * log (pt);
    return 1. / (1. + 0.01 * f1);
  }

  bool analysisClass::jet_id (size_t j)
  {
    //bool isMC = getPreCutValue1("isMC") == 1;
    #if isMC==true
      float hf = (jetChfAK4->at (j) + jetNhfAK4->at (j) + jetHf_hfAK4->at (j));
      float em = (jetNemfAK4->at (j) + jetCemfAK4->at (j) + jetHf_emfAK4->at (j));
    #else
      float hf = (jetHadfAK4->at (j) + jetHf_hfAK4->at (j));
      float em = (jetEmfAK4->at (j) + jetHf_emfAK4->at (j));
    #endif

    if (fabs (jetEtaAK4->at (j) < getPreCutValue1 ("jetFidRegion")))
      if (hf < getPreCutValue1 ("hadFraction") && em < getPreCutValue1 ("emFraction"))
        return true;
    return false;

  }

  analysisClass::analysisClass (string * inputList, string * cutFile, string * treeName, string * outputFileName, string * cutEfficFile):baseClass (inputList, cutFile, treeName, outputFileName, cutEfficFile)
  {
    //bool isMC = getPreCutValue1("isMC") == 1;
    std::cout << "analysisClass::analysisClass(): begins " << std::endl;

    std::string jetAlgo = getPreCutString1 ("jetAlgo");

    double rParam = getPreCutValue1 ("DeltaR");

    if (jetAlgo == "AntiKt")
      fjJetDefinition = JetDefPtr (new fastjet::JetDefinition (fastjet::antikt_algorithm, rParam));
    else if (jetAlgo == "Kt")
      fjJetDefinition = JetDefPtr (new fastjet::JetDefinition (fastjet::kt_algorithm, rParam));
    else
      fjJetDefinition = JetDefPtr (new fastjet::JetDefinition (fastjet::cambridge_algorithm, rParam));

    // For JECs
    if (int (getPreCutValue1 ("useJECs")) == 1) {
      std::cout << "Reapplying JECs on the fly" << std::endl;
      std::vector < JetCorrectorParameters > vPar;
      #if isMC==true
        vPar.push_back (JetCorrectorParameters("data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L1FastJet_AK4PFchs.txt"));
        vPar.push_back (JetCorrectorParameters("data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L2Relative_AK4PFchs.txt"));
        vPar.push_back (JetCorrectorParameters("data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L3Absolute_AK4PFchs.txt"));
      #else
        // procedure for 2016 CaloScouting data:
        vPar.push_back (JetCorrectorParameters("data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L1FastJet_AK4CaloHLT.txt"));
        vPar.push_back (JetCorrectorParameters("data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L2Relative_AK4CaloHLT.txt"));
        vPar.push_back (JetCorrectorParameters("data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L3Absolute_AK4CaloHLT.txt"));
        // 2016 data for Moriond
        //residuals are applied only to data
        vPar.push_back (JetCorrectorParameters("data/Spring16_V8_DATA/Spring16_25nsV8p2_DATA_L2L3Residual_AK4PFchs.txt"));
      #endif

      //std::string L1Path = "data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L1FastJet_AK4PFchs.txt";
      //std::string L2Path = "data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L2Relative_AK4PFchs.txt";
      //std::string L3Path = "data/Summer15_25nsV7_MC/Summer15_25nsV7_MC_L3Absolute_AK4PFchs.txt";
      //// procedure for 2016 CaloScouting data:
      //std::string L1DATAPath =
      //"data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L1FastJet_AK4CaloHLT.txt";
      //std::string L2DATAPath =
      //"data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L2Relative_AK4CaloHLT.txt";
      //std::string L3DATAPath =
      //"data/80X_dataRun2_HLT_frozen_v12/80X_dataRun2_HLT_frozen_v12_L3Absolute_AK4CaloHLT.txt";
      //// 2016 data for Moriond
      //std::string L2L3ResidualPath =
      //"data/Spring16_V8_DATA/Spring16_25nsV8p2_DATA_L2L3Residual_AK4PFchs.txt";

      //if (isData == 1) {
      //vPar.push_back (JetCorrectorParameters (L1DATAPath));
      //vPar.push_back (JetCorrectorParameters (L2DATAPath));
      //vPar.push_back (JetCorrectorParameters (L3DATAPath));
      ////residuals are applied only to data
      //vPar.push_back (JetCorrectorParameters (L2L3ResidualPath));
      //}
      //else {
      //vPar.push_back (JetCorrectorParameters (L1Path));
      //vPar.push_back (JetCorrectorParameters (L2Path));
      //vPar.push_back (JetCorrectorParameters (L3Path));
      //}
      // define later as struct
      JetCorrector = new FactorizedJetCorrector (vPar);

      //uncertainty
      //unc = new JetCorrectionUncertainty("data/Summer15_50nsV5_DATA/Summer15_50nsV5_DATA_Uncertainty_AK4PFchs.txt");
      //unc = new JetCorrectionUncertainty("data/Summer15_25nsV5_DATA/Summer15_25nsV5_DATA_Uncertainty_AK4PFchs.txt");
      //unc = new JetCorrectionUncertainty("data/Summer15_25nsV6_DATA/Summer15_25nsV6_DATA_Uncertainty_AK4PFchs.txt");
      // for ICHEP 2016 CaloScouting
      //unc = new JetCorrectionUncertainty("data/Spring16_25nsV6_DATA/Spring16_25nsV6_DATA_Uncertainty_AK4PFchs.txt");
      // for 2016 CaloScouting
      unc = new JetCorrectionUncertainty("data/Spring16_V8_DATA/Spring16_25nsV8p2_DATA_Uncertainty_AK4PFchs.txt");

    }

    std::cout << "analysisClass::analysisClass(): ends " << std::endl;
  }

  analysisClass::~analysisClass ()
  {
    std::cout << "analysisClass::~analysisClass(): begins " << std::endl;

    std::cout << "analysisClass::~analysisClass(): ends " << std::endl;
  }

  void
  analysisClass::Loop ()
  {
    std::cout << "analysisClass::Loop() begins" << std::endl;

    if (fChain == 0) return;

    bool store_ntuple = abs(getPreCutValue1("saveNtuple")) == 1;
    bool store_histogram = getPreCutValue1("saveNtuple") != -1;

    if(store_histogram){
      dijetMassHisto          = new TH1F("dijet_mass", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_40_50    = new TH1F("dijetMassHisto_isrptcut_40_50",   "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_50_60    = new TH1F("dijetMassHisto_isrptcut_50_60",   "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_60_70    = new TH1F("dijetMassHisto_isrptcut_60_70",   "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70_80    = new TH1F("dijetMassHisto_isrptcut_70_80",   "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_80_90    = new TH1F("dijetMassHisto_isrptcut_80_90",   "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_90_100   = new TH1F("dijetMassHisto_isrptcut_90_100",  "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_100_150  = new TH1F("dijetMassHisto_isrptcut_100_150", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_150_200  = new TH1F("dijetMassHisto_isrptcut_150_200", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_200_300  = new TH1F("dijetMassHisto_isrptcut_200_300", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_300      = new TH1F("dijetMassHisto_isrptcut_300",     "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70       = new TH1F("dijetMassHisto_isrptcut_70",      "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70_HT_270 = new TH1F("dijetMassHisto_isrptcut_70_HT_270", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70_L1_HTT240_L1_HTT270 = new TH1F("dijetMassHisto_isrptcut_70_L1_HTT240_L1_HTT270", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_L1_HTT_240_270_or      = new TH1F("dijetMassHisto_L1_HTT_240_270_or", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_L1_HTT_240_270_280_or  = new TH1F("dijetMassHisto_L1_HTT_240_270_280_or", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_L1_HTT_240_270_280_300_or     = new TH1F("dijetMassHisto_L1_HTT_240_270_280_300_or", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_L1_HTT_240_270_280_300_320_or = new TH1F("dijetMassHisto_L1_HTT_240_270_280_300_320_or", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70_L1_HTT240_L1_HTT320 = new TH1F("dijetMassHisto_70_L1_HTT240_L1_HTT320", "Dijet Mass", 5000, 0, 5000);
      dijetMassHisto_70_dijet_deta_unblind  = new TH1F("dijetMassHisto_70_dijet_deta_unblind", "Dijet Mass", 5000, 0, 5000);
    }
    //////////book histos here

    // variable binning for dijet_mass trigger efficiency plots
    const int nMassBins = 103;

    double massBoundaries[nMassBins + 1] =
    { 1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176,
      197, 220, 244, 270, 296, 325,
      354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944,
      1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687,
      1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895,
      3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509,
      4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060,
      7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430,
      10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000
    };

    /////////initialize variables

    Long64_t nentries = fChain->GetEntriesFast ();
    int maxEvents = getPreCutValue1 ("maxEvents");
    int skimHLT_CaloJet40_CaloScouting_PFScouting = getPreCutValue1 ("skimHLT_CaloJet40_CaloScouting_PFScouting");
    int skimHLT_L1HTT_CaloScouting_PFScouting = getPreCutValue1 ("skimHLT_L1HTT_CaloScouting_PFScouting");
    int skimHLT_CaloScoutingHT250 = getPreCutValue1 ("skimHLT_CaloScoutingHT250");
    if (maxEvents > 0) nentries = std::min (Long64_t (maxEvents), nentries);
    std::cout << "analysisClass::Loop(): nentries = " << nentries << std::endl;

    ////// The following ~7 lines have been taken from rootNtupleClass->Loop() /////
    ////// If the root version is updated and rootNtupleClass regenerated,     /////
    ////// these lines may need to be updated.                                 /////
    Long64_t nbytes = 0, nb = 0;
    int idx_InTimeBX = -1;
    for (Long64_t jentry = 0; jentry < nentries; jentry++) {
      Long64_t ientry = LoadTree (jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry (jentry);
      nbytes += nb;
      if (jentry < 10 || jentry % 1000 == 0) std::cout << "analysisClass::Loop(): jentry = " << jentry << std::endl;
      ////////////////////// User's code starts here ///////////////////////
      ///Stuff to be done for every event
      if ((skimHLT_CaloJet40_CaloScouting_PFScouting > 0) && (triggerResult->at (0) == 0)) continue;
      if ((skimHLT_L1HTT_CaloScouting_PFScouting > 0) && (triggerResult->at (2) == 0)) continue;
      if ((skimHLT_CaloScoutingHT250 > 0) && (triggerResult->at (4) == 0)) continue;

      size_t no_jets_ak4 = jetPtAK4->size ();

      vector < TLorentzVector > myjets, myjets_CM;
      bool mcReco_matching = false;
      TLorentzVector jet1, jet2, isr, dijet, trijet;
      TLorentzVector jet1_mc, jet2_mc, isr_mc, dijet_mc, trijet_mc, jet1_mcReco, jet2_mcReco,
      isr_mcReco, dijet_mcReco, trijet_mcReco;

      resetCuts ();

      std::vector < double >jecFactors;
      std::vector < double >jecUncertainty;
      std::vector < bool > idCaloJet;     // CaloJet ID
      // new JECs could change the jet pT ordering. the vector below
      // holds sorted jet indices after the new JECs had been applied
      std::vector < unsigned >sortedJetIdx;

      double HTaddjets = 0;
      double HTdijets = 0;
      double HTtrijets = 0;
      double HTgoodjets = 0;
      double HTbadjets = 0;
      std::multimap < double, unsigned >sortedJets;
      for (size_t j = 0; j < no_jets_ak4; ++j) {
        double correction = 1.;
        double uncertainty = 0.;
        if (int (getPreCutValue1 ("useJECs")) == 1) {     // sort jets by increasing pT, after corrections
          JetCorrector->setJetEta (jetEtaAK4->at (j));
          JetCorrector->setJetPt (jetPtAK4->at (j) / jetJecAK4->at (j));  //pTraw
          JetCorrector->setJetA (jetAreaAK4->at (j));
          JetCorrector->setRho (rho);
          //nominal value of JECs
          correction = JetCorrector->getCorrection ();
          //JEC uncertainties
          unc->setJetEta (jetEtaAK4->at (j));
          unc->setJetPt (jetPtAK4->at (j) / jetJecAK4->at (j) * correction);
          uncertainty = unc->getUncertainty (true);
          //use "shifted" JECs for study of systematic uncertainties
          if (int (getPreCutValue1 ("shiftJECs")) == 1) {
            correction = correction + getPreCutValue2 ("shiftJECs") * uncertainty * correction;
          }
        }
        else if (int (getPreCutValue1 ("noJECs")) == 1) { // sort jets by increasing pT, removing corrections
          jecFactors.push_back (1.);
          jecUncertainty.push_back (0.);
          idCaloJet.push_back (jet_id (j));
          correction = 1;
        }
        else {
          correction = jetJecAK4->at (j); //same ordering of original root trees
        }
        // get jet indices in decreasing pT order
        jecFactors.push_back (correction);
        jecUncertainty.push_back (uncertainty);
        idCaloJet.push_back (jet_id (j));
        sortedJets.insert (std::make_pair ((jetPtAK4->at (j) / jetJecAK4->at (j)) * correction, j));
      }
      for (std::multimap < double, unsigned >::const_reverse_iterator it = sortedJets.rbegin ();
      it != sortedJets.rend (); ++it) {
        sortedJetIdx.push_back (it->second);
      }
      //#############################################################
      //########## NOTE: from now on sortedJetIdx[ijet] should be used
      //#############################################################
      //count ak4 jets passing pt threshold and id criteria

      int Nak4 = 0;
      double HTak4 = 0;

      for (size_t ijet = 0; ijet < no_jets_ak4; ++ijet) {
        int idx = sortedJetIdx.at (ijet);
        if (fabs (jetEtaAK4->at (idx)) < getPreCutValue1 ("jetFidRegion")
        && idCaloJet.at (idx) == getPreCutValue1 ("tightJetID")
        && (jecFactors.at (idx) / jetJecAK4->at (idx)) *
        jetPtAK4->at (idx) > getPreCutValue1 ("ptCut")) {
          Nak4 += 1;
          HTak4 += (jecFactors.at (idx) / jetJecAK4->at (idx)) * jetPtAK4->at (idx);
        }
      }

      // vector of goodjets passing the jet selection
      std::vector < TLorentzVector > goodjets;
      for (size_t j = 0; j < no_jets_ak4; ++j) {
        bool good = true;
        int idx = sortedJetIdx.at (j);
        if (!(fabs (jetEtaAK4->at (idx)) < getPreCutValue1 ("jetFidRegion")
        // && idTAK4->at(idx) == getPreCutValue1("tightJetID")
        && idCaloJet.at (idx) == getPreCutValue1 ("tightJetID")))
        good = false;

        double rescale = (jecFactors.at (idx) / jetJecAK4->at (idx));
        double jet_pt = rescale * jetPtAK4->at (idx);

        if (j == 0 && !(jet_pt > getPreCutValue1 ("pt0Cut")))
        good = false;
        else if (j == 1 && !(jet_pt > getPreCutValue1 ("pt1Cut")))
        good = false;
        else if (!(jet_pt > getPreCutValue1 ("ptCut")))
        good = false;

        TLorentzVector jet;
        jet.SetPtEtaPhiM (jet_pt, jetEtaAK4->at (idx), jetPhiAK4->at (idx), jetMassAK4->at (idx));

        if (good) goodjets.push_back (jet);
        if (good && jet.Pt () > getPreCutValue1 ("ptCutHT")) {
          HTgoodjets += jet.Pt ();
          if (j <= 1)
          HTdijets += jet.Pt ();
          if (j <= 2)
          HTtrijets += jet.Pt ();
          if (j >= 2)
          HTaddjets += jet.Pt ();
        }
        else
        HTbadjets += jet.Pt ();
      }

      if (getPreCutValue1 ("useWideJets") == 1) {
        goodjets = doWideJets (goodjets);
      }
      std::sort (goodjets.begin (), goodjets.end (), sortByPt);
      float corr1 = 1;
      float corr2 = 1;
      float corr3 = 1;
      std::pair<int,int> dijet_index[3] = {make_pair(1,2), make_pair(0,2), make_pair(0,1)};
      int isr_index = 0;
      if (goodjets.size () >= 2) {
        //      std::pair < int, int >dijet_pair = find_dijet(goodjets, "dotProduct3D");
        //std::pair < int, int >dijet_pair = find_dijet (goodjets, "dijetM");
        jet1 = goodjets.at (0);
        jet2 = goodjets.at (1);
        if (goodjets.size () >= 3) {
          std::pair < int, int >dijet_pair = find_dijet (goodjets, getPreCutString1("jetMatching"));
          int jet_isr = 0;
          while (jet_isr == dijet_pair.first || jet_isr == dijet_pair.second) {
            jet_isr++;
          }
          jet1 = goodjets.at (dijet_pair.first);
          jet2 = goodjets.at (dijet_pair.second);
          isr = goodjets.at (jet_isr);
          if (getPreCutValue1 ("useWideJets") == 1) {
            corr3 = biasCorrection (isr.Pt ());
            isr *= corr3;
          }
        }
        if (getPreCutValue1 ("useWideJets") == 1) {
          corr1 = biasCorrection (jet1.Pt ());
          corr2 = biasCorrection (jet2.Pt ());
          jet1 *= corr1;
          jet2 *= corr2;
        }
        // if (goodjets.size () >= 3) {
        //   //jet1 = goodjets.at (dijet_index[isr_index].first);
        //   //jet2 = goodjets.at (dijet_index[isr_index].second);
      	//   jet1 = goodjets.at(0);
      	//   jet2 = goodjets.at(1);
        //   if (getPreCutValue1 ("useWideJets") == 1) {
        //     corr1 = biasCorrection (jet1.Pt ());
        //     corr2 = biasCorrection (jet2.Pt ());
        //     jet1 *= corr1;
        //     jet2 *= corr2;
        //   }
        //   isr = goodjets.at(2);
        //   if (getPreCutValue1 ("useWideJets") == 1) {
        //     corr3 = biasCorrection (isr.Pt ());
        //     isr *= corr3;
        //   }
        // }
      }

      jet1_mc.SetXYZT (0, 0, 0, 0);
      jet2_mc.SetXYZT (0, 0, 0, 0);
      isr_mc.SetXYZT (0, 0, 0, 0);
      jet1_mcReco.SetXYZT (0, 0, 0, 0);
      jet2_mcReco.SetXYZT (0, 0, 0, 0);
      isr_mcReco.SetXYZT (0, 0, 0, 0);

      #if isMC==true
      //find intime BX
        if (idx_InTimeBX < 0 || PileupOriginBX->at (idx_InTimeBX) != 0) {
          for (size_t j = 0; j < PileupOriginBX->size (); ++j) {
            //cout << PileupOriginBX->at(j) << endl;
            if (PileupOriginBX->at (j) == 0) {
              idx_InTimeBX = j;
              //cout << "idx_InTimeBX: " << idx_InTimeBX << endl;
            }
          }
        }
        for (size_t igen = 0; igen < gen_motherIndex->size (); ++igen) {
          if ((gen_motherIndex->at (igen) >= 0) && (gen_status->at (igen) == 23)) {
            if (gen_pdgId->at (gen_motherIndex->at (igen)) > 1000) {
              if (jet1_mc.Energy () < 5) {
                jet1_mc.SetPxPyPzE (gen_px->at (igen), gen_py->at (igen),
                gen_pz->at (igen), gen_energy->at (igen));
              }
              else if (jet2_mc.Energy () < 5) {
                jet2_mc.SetPxPyPzE (gen_px->at (igen), gen_py->at (igen),
                gen_pz->at (igen), gen_energy->at (igen));
              }
            }
            else if (isr_mc.Energy () < 5) {
              isr_mc.SetPxPyPzE (gen_px->at (igen), gen_py->at (igen), gen_pz->at (igen),
              gen_energy->at (igen));
            }

          }
        }
        if (jet2_mc.Pt () > jet1_mc.Pt ()) {
          TLorentzVector tmp = jet2_mc;
          jet2_mc = jet1_mc;
          jet1_mc = tmp;
        }
        float dR1 = 1000;
        float dR2 = 1000;
        float dR3 = 1000;
        float tmp;
        if (jet1_mc.Pt () > 5) {
          for (size_t ijet = 0; ijet < goodjets.size (); ++ijet) {
            tmp = goodjets.at (ijet).DeltaR (jet1_mc);
            if (tmp < dR1) {
              dR1 = tmp;
              jet1_mcReco = goodjets.at (ijet);
            }
          }
        }
        if (jet2_mc.Pt () > 5) {
          for (size_t ijet = 0; ijet < goodjets.size (); ++ijet) {
            tmp = goodjets.at (ijet).DeltaR (jet2_mc);
            if (tmp < dR2 && abs (jet1_mcReco.Pt () - goodjets.at (ijet).Pt ()) > 0.01) {
              dR2 = tmp;
              jet2_mcReco = goodjets.at (ijet);
            }
          }
        }
        if (isr_mc.Pt () > 5) {
          for (size_t ijet = 0; ijet < goodjets.size (); ++ijet) {
            tmp = goodjets.at (ijet).DeltaR (isr_mc);
            if (tmp < dR3 && abs (jet1_mcReco.Pt () - goodjets.at (ijet).Pt ()) > 0.01
            && abs (jet2_mcReco.Pt () - goodjets.at (ijet).Pt ()) > 0.01) {
              dR3 = tmp;
              isr_mcReco = goodjets.at (ijet);
            }
          }
        }
        dijet_mc = jet1_mc + jet2_mc;
        trijet_mc = jet1_mc + jet2_mc + isr_mc;
        dijet_mcReco = jet1_mcReco + jet2_mcReco;
        trijet_mcReco = jet1_mcReco + jet2_mcReco + isr_mcReco;
        if (dR1 < 0.8 && dR2 < 0.8 && (jet1_mcReco.Pt () > 0.5 * jet1_mc.Pt ())
        && (jet2_mcReco.Pt () > 0.5 * jet2_mc.Pt ())
        && (jet1_mc.Pt () > 0.5 * jet1_mcReco.Pt ())
        && (jet2_mc.Pt () > 0.5 * jet2_mcReco.Pt ())) {
          mcReco_matching = true;
      }
      #endif
      /*
      cout << "goodjets.size () " << goodjets.size () << endl;
      cout << "jet1.Pt () " << jet1.Pt () << endl;
      cout << "jet2.Pt () " << jet2.Pt () << endl;
      cout << "isr.Pt () " << isr.Pt () << endl;
      */

      dijet = jet1 + jet2;
      trijet = jet1 + jet2 + isr;
      myjets.push_back (jet1);
      myjets.push_back (jet2);
      myjets.push_back (isr);

      TLorentzVector jet1_CM = jet1;
      TLorentzVector jet2_CM = jet2;
      TLorentzVector isr_CM = isr;

      double AdditionalHTgoodjets = 0;
      AdditionalHTgoodjets = HTgoodjets;
      AdditionalHTgoodjets -= jet1.Pt ();
      AdditionalHTgoodjets -= jet2.Pt ();
      AdditionalHTgoodjets -= isr.Pt ();

      //== Fill Variables ==
      fillVariableWithValue ("isData", isData);
      fillVariableWithValue ("run", runNo);
      fillVariableWithValue ("event", evtNo);
      //    fillVariableWithValue ("goodjets", goodjets);
      fillVariableWithValue ("lumi", lumi);
      fillVariableWithValue ("nVtx", nvtx);
      fillVariableWithValue ("rho", rho);
      fillVariableWithValue ("nJet", goodjets.size ());
      fillVariableWithValue ("Nak4", Nak4);
      fillVariableWithValue ("PassJSON", passJSON (runNo, lumi, isData));
      //directly taken from big root tree (i.e. jec not reapplied)
      fillVariableWithValue ("htAK4", htAK4);     // summing all jets with minimum pT cut and no jetid cut (jec not reapplied)
      fillVariableWithValue ("mhtAK4", mhtAK4);   //summing all jets with minimum pT cut and no jetid cut (jec not reapplied)
      fillVariableWithValue ("mhtAK4Sig", mhtAK4Sig);     // mhtAK4/htAK4 summing all jets with minimum pT cut and no jetid cut (jec not reapplied)
      fillVariableWithValue ("met", met); //directly taken from event
      fillVariableWithValue ("HTak4", HTak4);
      fillVariableWithValue ("HTgoodJets", HTgoodjets);
      fillVariableWithValue ("HTdijets", HTdijets);
      fillVariableWithValue ("HTtrijets", HTtrijets);
      fillVariableWithValue ("HTaddjets", HTaddjets);
      fillVariableWithValue ("HTbadJets", HTbadjets);

      if (myjets.size () >= 1) {
        fillVariableWithValue ("jet1_idtight", 1);        //idCaloJet.at(sortedJetIdx.at(1)));
        fillVariableWithValue ("jet1_pt", jet1.Pt ());
        fillVariableWithValue ("jet1_eta", jet1.Eta ());
        //no cuts on these variables, just to store in output
        fillVariableWithValue ("jet1_phi", jet1.Phi ());
        fillVariableWithValue ("jet1_mass", jet1.M ());
        fillVariableWithValue ("jet1_corr", corr1);
        //      cout << myjets.at(0).Pt () << endl;
      }

      if (myjets.size () >= 2) {
        fillVariableWithValue ("jet2_idtight", 1);        //idCaloJet.at(sortedJetIdx.at(1)));
        fillVariableWithValue ("jet2_pt", jet2.Pt ());
        fillVariableWithValue ("jet2_eta", jet2.Eta ());
        fillVariableWithValue ("jet2_phi", jet2.Phi ());
        fillVariableWithValue ("jet2_mass", jet2.M ());
        fillVariableWithValue ("jet2_corr", corr2);
        fillVariableWithValue ("dijet_deta", (jet1.Eta () - jet2.Eta ()));
        fillVariableWithValue ("dijet_dphi", jet1.DeltaPhi (jet2));
        fillVariableWithValue ("dijet_dr", jet1.DeltaR (jet2));
        fillVariableWithValue ("dijet_mass", dijet.M ());
        fillVariableWithValue ("dijet_pt", dijet.Pt ());
        fillVariableWithValue ("dijet_eta", dijet.Eta ());
        fillVariableWithValue ("dijet_phi", dijet.Phi ());
        fillVariableWithValue ("addHT", AdditionalHTgoodjets);
        //      cout << myjets.at(1).Pt () << endl;
      }
      if (myjets.size () >= 3) {
        fillVariableWithValue ("isr_mass", isr.M ());
        fillVariableWithValue ("isr_pt", isr.Pt ());
        fillVariableWithValue ("isr_eta", isr.Eta ());
        fillVariableWithValue ("isr_phi", isr.Phi ());
        //      fillVariableWithValue ("isr_corr", corr3);
        fillVariableWithValue ("isr_idtight", 1); //idCaloJet.at(sortedJetIdx.at(1)));
        fillVariableWithValue ("trijet_pt", trijet.Pt ());
        fillVariableWithValue ("trijet_eta", trijet.Eta ());
        fillVariableWithValue ("trijet_phi", trijet.Phi ());
        fillVariableWithValue ("trijet_mass", trijet.M ());
        fillVariableWithValue ("trijet_deta", (dijet.Eta () - isr.Eta ()));
        fillVariableWithValue ("trijet_dphi", dijet.DeltaPhi (isr));
        fillVariableWithValue ("trijet_dr", dijet.DeltaR (isr));
      }

      //no cuts on these variables, just to store in output
      // if(!isData)
      //   fillVariableWithValue("trueVtx",PileupInteractions->at(idx_InTimeBX));
      // else if(isData)
      //   fillVariableWithValue("trueVtx",999);

      // Trigger
      //int NtriggerBits = triggerResult->size();
      #if isMC
      fillVariableWithValue ("processID", processID);
      fillVariableWithValue ("weight", weight);
      fillVariableWithValue ("ptHat", ptHat);
      fillVariableWithValue ("trueVtx", PileupInteractions->at (idx_InTimeBX));
      fillVariableWithValue ("mcReco_matching", mcReco_matching);

      fillVariableWithValue ("dijetMC_deta", (jet1_mc.Eta () - jet2_mc.Eta ()));
      fillVariableWithValue ("dijetMC_dphi", jet1_mc.DeltaPhi (jet2_mc));
      fillVariableWithValue ("dijetMC_dr", jet1_mc.DeltaR (jet2_mc));
      fillVariableWithValue ("dijetMC_mass", dijet_mc.M ());
      fillVariableWithValue ("dijetMC_pt", dijet_mc.Pt ());
      fillVariableWithValue ("dijetMC_eta", dijet_mc.Eta ());
      fillVariableWithValue ("dijetMC_phi", dijet_mc.Phi ());

      fillVariableWithValue ("dijetMCreco_deta", (jet1_mcReco.Eta () - jet2_mcReco.Eta ()));
      fillVariableWithValue ("dijetMCreco_dphi", jet1_mcReco.DeltaPhi (jet2_mcReco));
      fillVariableWithValue ("dijetMCreco_dr", jet1_mcReco.DeltaR (jet2_mcReco));
      fillVariableWithValue ("dijetMCreco_mass", dijet_mcReco.M ());
      fillVariableWithValue ("dijetMCreco_pt", dijet_mcReco.Pt ());
      fillVariableWithValue ("dijetMCreco_eta", dijet_mcReco.Eta ());
      fillVariableWithValue ("dijetMCreco_phi", dijet_mcReco.Phi ());

      fillVariableWithValue ("trijetMC_deta", (dijet_mc.Eta () - isr_mc.Eta ()));
      fillVariableWithValue ("trijetMC_dphi", dijet_mc.DeltaPhi (isr_mc));
      fillVariableWithValue ("trijetMC_dr", dijet_mc.DeltaR (isr_mc));

      fillVariableWithValue ("trijetMC_mass", trijet_mc.M ());
      fillVariableWithValue ("trijetMC_pt", trijet_mc.Pt ());
      fillVariableWithValue ("trijetMC_eta", trijet_mc.Eta ());
      fillVariableWithValue ("trijetMC_phi", trijet_mc.Phi ());

      fillVariableWithValue ("trijetMCreco_deta", (dijet_mcReco.Eta () - isr_mcReco.Eta ()));
      fillVariableWithValue ("trijetMCreco_dphi", dijet_mcReco.DeltaPhi (isr_mcReco));
      fillVariableWithValue ("trijetMCreco_dr", dijet_mcReco.DeltaR (isr_mcReco));

      fillVariableWithValue ("trijetMCreco_mass", trijet_mcReco.M ());
      fillVariableWithValue ("trijetMCreco_pt", trijet_mcReco.Pt ());
      fillVariableWithValue ("trijetMCreco_eta", trijet_mcReco.Eta ());
      fillVariableWithValue ("trijetMCreco_phi", trijet_mcReco.Phi ());

      fillVariableWithValue ("jet1MCreco_mass", jet1_mcReco.M ());
      fillVariableWithValue ("jet1MCreco_pt", jet1_mcReco.Pt ());
      fillVariableWithValue ("jet1MCreco_eta", jet1_mcReco.Eta ());
      fillVariableWithValue ("jet1MCreco_phi", jet1_mcReco.Phi ());

      fillVariableWithValue ("jet2MCreco_mass", jet2_mcReco.M ());
      fillVariableWithValue ("jet2MCreco_pt", jet2_mcReco.Pt ());
      fillVariableWithValue ("jet2MCreco_eta", jet2_mcReco.Eta ());
      fillVariableWithValue ("jet2MCreco_phi", jet2_mcReco.Phi ());

      fillVariableWithValue ("isrMCreco_mass", isr_mcReco.M ());
      fillVariableWithValue ("isrMCreco_pt", isr_mcReco.Pt ());
      fillVariableWithValue ("isrMCreco_eta", isr_mcReco.Eta ());
      fillVariableWithValue ("isrMCreco_phi", isr_mcReco.Phi ());

      fillVariableWithValue ("jet1MC_mass", jet1_mc.M ());
      fillVariableWithValue ("jet1MC_pt", jet1_mc.Pt ());
      fillVariableWithValue ("jet1MC_eta", jet1_mc.Eta ());
      fillVariableWithValue ("jet1MC_phi", jet1_mc.Phi ());

      fillVariableWithValue ("jet2MC_mass", jet2_mc.M ());
      fillVariableWithValue ("jet2MC_pt", jet2_mc.Pt ());
      fillVariableWithValue ("jet2MC_eta", jet2_mc.Eta ());
      fillVariableWithValue ("jet2MC_phi", jet2_mc.Phi ());

      fillVariableWithValue ("isrMC_mass", isr_mc.M ());
      fillVariableWithValue ("isrMC_pt", isr_mc.Pt ());
      fillVariableWithValue ("isrMC_eta", isr_mc.Eta ());
      fillVariableWithValue ("isrMC_phi", isr_mc.Phi ());

      if (goodjets.size () >= 2) {
        fillVariableWithValue ("method_crossProduct",
        test_method (goodjets, dijet_mcReco, "crossProduct"));
        fillVariableWithValue ("method_dotProduct3D",
        test_method (goodjets, dijet_mcReco, "dotProduct3D"));
        fillVariableWithValue ("method_dotProduct",
        test_method (goodjets, dijet_mcReco, "dotProduct"));
        fillVariableWithValue ("method_jets01", test_method (goodjets, dijet_mcReco, "jets01"));
        fillVariableWithValue ("method_dijetPt", test_method (goodjets, dijet_mcReco, "dijetPt"));
        fillVariableWithValue ("method_dijetPt", test_method (goodjets, dijet_mcReco, "dijetM"));
        fillVariableWithValue ("method_dijetPtMod",
        test_method (goodjets, dijet_mcReco, "dijetPtMod"));
        fillVariableWithValue ("method_dijetP", test_method (goodjets, dijet_mcReco, "dijetP"));
        fillVariableWithValue ("method_dijetPMod", test_method (goodjets, dijet_mcReco, "dijetPMod"));
        fillVariableWithValue ("method_dijetEnergy",
        test_method (goodjets, dijet_mcReco, "dijetEnergy"));
        fillVariableWithValue ("method_dijetEnergyMod",
        test_method (goodjets, dijet_mcReco, "dijetEnergyMod"));
        fillVariableWithValue ("method_dijetM", test_method (goodjets, dijet_mcReco, "dijetM"));
        fillVariableWithValue ("method_dijetMn", test_method (goodjets, dijet_mcReco, "dijetMn"));

        fillVariableWithValue ("method_dijetDPhi", test_method (goodjets, dijet_mcReco, "dijetDPhi"));
        fillVariableWithValue ("method_dijetDR", test_method (goodjets, dijet_mcReco, "dijetDR"));

      }
      if (goodjets.size () >= 3) {
        fillVariableWithValue ("method_jets02", test_method (goodjets, dijet_mcReco, "jets02"));
        fillVariableWithValue ("method_jets12", test_method (goodjets, dijet_mcReco, "jets12"));

        fillVariableWithValue ("method_dijetM_CM",
        test_method (goodjets, dijet_mcReco, "dijetM", true));
        fillVariableWithValue ("method_dijetMn_CM",
        test_method (goodjets, dijet_mcReco, "dijetMn", true));
        fillVariableWithValue ("method_dijetPt_CM",
        test_method (goodjets, dijet_mcReco, "dijetPt", true));
        fillVariableWithValue ("method_dijetPtMod_CM",
        test_method (goodjets, dijet_mcReco, "dijetPtMod", true));
        fillVariableWithValue ("method_dijetP_CM",
        test_method (goodjets, dijet_mcReco, "dijetP", true));
        fillVariableWithValue ("method_dijetPMod_CM",
        test_method (goodjets, dijet_mcReco, "dijetPMod", true));
        fillVariableWithValue ("method_dijetEnergy_CM",
        test_method (goodjets, dijet_mcReco, "dijetEnergy", true));
        fillVariableWithValue ("method_dijetEnergyMod_CM",
        test_method (goodjets, dijet_mcReco, "dijetEnergyMod", true));
        fillVariableWithValue ("method_crossProduct_CM",
        test_method (goodjets, dijet_mcReco, "crossProduct", true));
        fillVariableWithValue ("method_dotProduct3D_CM",
        test_method (goodjets, dijet_mcReco, "dotProduct3D", true));
        fillVariableWithValue ("method_dotProduct_CM",
        test_method (goodjets, dijet_mcReco, "dotProduct", true));

        fillVariableWithValue ("method_dijetM_CMz",
        test_method (goodjets, dijet_mcReco, "dijetM", true, true));
        fillVariableWithValue ("method_dijetMn_CMz",
        test_method (goodjets, dijet_mcReco, "dijetMn", true, true));
        fillVariableWithValue ("method_dijetPt_CMz",
        test_method (goodjets, dijet_mcReco, "dijetPt", true, true));
        fillVariableWithValue ("method_dijetPtMod_CMz",
        test_method (goodjets, dijet_mcReco, "dijetPtMod", true, true));
        fillVariableWithValue ("method_dijetP_CMz",
        test_method (goodjets, dijet_mcReco, "dijetP", true, true));
        fillVariableWithValue ("method_dijetPMod_CMz",
        test_method (goodjets, dijet_mcReco, "dijetPMod", true, true));
        fillVariableWithValue ("method_dijetEnergy_CMz",
        test_method (goodjets, dijet_mcReco, "dijetEnergy", true, true));
        fillVariableWithValue ("method_dijetEnergyMod_CMz",
        test_method (goodjets, dijet_mcReco, "dijetEnergyMod", true, true));
        fillVariableWithValue ("method_crossProduct_CMz",
        test_method (goodjets, dijet_mcReco, "crossProduct", true, true));
        fillVariableWithValue ("method_dotProduct3D_CMz",
        test_method (goodjets, dijet_mcReco, "dotProduct3D", true, true));
        fillVariableWithValue ("method_dotProduct_CMz",
        test_method (goodjets, dijet_mcReco, "dotProduct", true, true));
        fillVariableWithValue ("method_random_CM",
        test_method (goodjets, dijet_mcReco, "random", true));
        fillVariableWithValue ("method_random", test_method (goodjets, dijet_mcReco, "random"));

        fillVariableWithValue ("method_jets01_CM",
        test_method (goodjets, dijet_mcReco, "jets01", true));
        fillVariableWithValue ("method_jets02_CM",
        test_method (goodjets, dijet_mcReco, "jets02", true));
        fillVariableWithValue ("method_jets12_CM",
        test_method (goodjets, dijet_mcReco, "jets12", true));

        fillVariableWithValue ("method_dijetDPhi_CM",
        test_method (goodjets, dijet_mcReco, "dijetDPhi", true));
        fillVariableWithValue ("method_dijetDR_CM",
        test_method (goodjets, dijet_mcReco, "dijetDR", true));

        fillVariableWithValue ("method_dijetDPhi_CMz",
        test_method (goodjets, dijet_mcReco, "dijetDPhi", true, true));
        fillVariableWithValue ("method_dijetDR_CMz",
        test_method (goodjets, dijet_mcReco, "dijetDR", true, true));
      }

      #else
      fillVariableWithValue ("L1_HTT200", l1Result->at (0));      //
      fillVariableWithValue ("L1_HTT240", l1Result->at (1));      //
      fillVariableWithValue ("L1_HTT270", l1Result->at (2));      //
      fillVariableWithValue ("L1_HTT280", l1Result->at (3));      //
      fillVariableWithValue ("L1_HTT300", l1Result->at (4));      //
      fillVariableWithValue ("L1_HTT320", l1Result->at (5));      //
      fillVariableWithValue ("L1_ZeroBias", l1Result->at (6));    //
      #endif
      fillVariableWithValue ("HLT_CaloJet40_CaloScouting_PFScouting", triggerResult->at (0));     // CaloJet40_CaloScouting_PFScouting
      fillVariableWithValue ("HLT_L1HTT_CaloScouting_PFScouting", triggerResult->at (2)); // L1HTT_CaloScouting_PFScouting
      fillVariableWithValue ("HLT_CaloScoutingHT250", triggerResult->at (4));     // CaloScoutingHT250
      fillVariableWithValue ("HLT_PFScoutingHT450", triggerResult->at (8));
      fillVariableWithValue ("HLT_PFHT900", triggerResult->at (15));
      fillVariableWithValue ("HLT_PFHT800", triggerResult->at (16));
      fillVariableWithValue ("HLT_PFHT650MJJ950", triggerResult->at (25));
      fillVariableWithValue ("HLT_PFHT650MJJ900", triggerResult->at (26));
      fillVariableWithValue ("HLT_PFJET500", triggerResult->at (27));
      fillVariableWithValue ("HLT_PFJET450", triggerResult->at (28));
      fillVariableWithValue ("HLT_Mu45Eta2p1", triggerResult->at (32));
      fillVariableWithValue ("HLT_AK8PFHT700TriMass50", triggerResult->at (33));
      fillVariableWithValue ("HLT_AK8PFJet360TrimMass50", triggerResult->at (34));
      fillVariableWithValue ("HLT_CaloJet500NoJetID", triggerResult->at (35));
      fillVariableWithValue ("HLT_ZeroBias_PFScouting", triggerResult->at (9));
      fillVariableWithValue ("HLT_ZeroBias_BTagScouting", triggerResult->at (10));
      // Evaluate cuts (but do not apply them)
      evaluateCuts ();
      /*
      cout << "Hello \n" << endl;
      cout << passedCut ("PassJSON") << endl;
      cout << passedCut ("jet1_idtight") << endl;
      cout << passedCut ("jet2_idtight") << endl;
      cout << passedCut ("nJet") << endl;
      cout << passedCut ("jet1_pt") << endl;
      cout << passedCut ("jet1_eta") << endl;
      cout << passedCut ("jet2_pt") << endl;
      cout << passedCut ("jet2_eta") << endl;
      */
      // optional call to fill a skim with the full content of the input roottuple
      //if( passedCut("nJetFinal") ) fillSkimTree();
      if (passedCut ("PassJSON")
      && passedCut ("jet1_idtight")
      && passedCut ("jet2_idtight")
      && passedCut ("nJet")
      && passedCut ("jet1_pt")
      && passedCut ("jet1_eta") && passedCut ("jet2_pt") && passedCut ("jet2_eta"))
      //        && getVariableValue ("dijet_deta") < getPreCutValue1 ("DetaJJforTrig")
      {

        //      cout << "PassJSON \n" << endl;
        //      if (passedAllPreviousCuts ("dijet_mass"))
        //        cout << "passedAllPreviousCuts dijet_mass \n" << endl;
        //      if (passedCut ("dijet_mass"))
        //        cout << "passedCut dijet_mass \n" << endl;
        //h_dijet_mass_NoTrigger_1GeVbin->Fill (MJJWide);
        //h_dijet_mass_NoTrigger->Fill (MJJWide);


        // if( (getVariableValue("HLT_L1HTT150_BtagSeq")||getVariableValue("HLT_L1HTT150")) )
        //          h_dijet_mass_HLTpass_L1HTT150 -> Fill(MJJWide);

        //if (getVariableValue ("HLT_CaloJet40_CaloScouting_PFScouting"))
        //  h_dijet_mass_HLTpass_CaloJet40_CaloScouting_PFScouting->Fill (MJJWide);
        //if (getVariableValue ("HLT_L1HTT_CaloScouting_PFScouting"))
        //  h_dijet_mass_HLTpass_L1HTT_CaloScouting_PFScouting->Fill (MJJWide);
        //if (getVariableValue ("HLT_CaloScoutingHT250"))
        //  h_dijet_mass_HLTpass_CaloScoutingHT250->Fill (MJJWide);
      }
      /*
      cout << "Hello \n" << endl;
      cout << passedAllPreviousCuts ("dijet_mass") << endl;
      cout << passedCut ("dijet_mass") << endl;
      */
      // optional call to fill a skim with a subset of the variables defined in the cutFile (use flag SAVE)
      if(getPreCutValue1("SaveAllEvents")){
      	if(store_ntuple == true) fillReducedSkimTree ();
      }
      else if (passedAllPreviousCuts ("dijet_mass") && passedCut ("dijet_mass") && passedCut ("isr_pt") && passedCut ("dijet_deta") ) {
        if(store_ntuple == true) fillReducedSkimTree ();

        // ===== Take a look at this =====
        // //Example on how to investigate quickly the data
        // 40-50, 50-60, 60-70, 70-80, 80-90, 90-100, 100-150,150-200,200-300,>300
        // if(isMC == false){
        //   if(getVariableValue("L1_HTT240") == 1 && getVariableValue("isr_pt") > 50  && getVariableValue("jet2_pt")>45  && abs(getVariableValue("dijet_deta"))<1.2 && getVariableValue("jet1_pt")>90 ){
        //       dijetMassHisto->Fill(getVariableValue("dijet_mass"));
        //   }
        // }
        if(!isMC){
          if(store_histogram){
            if(getVariableValue("isr_pt") > 70 && getVariableValue("jet2_pt")>70  /*&& abs(getVariableValue("dijet_deta"))<1.1*/ && getVariableValue("jet1_pt")>70 ){
              if(getVariableValue("L1_HTT240") || getVariableValue("L1_HTT270")){
                dijetMassHisto_L1_HTT_240_270_or->Fill(getVariableValue("dijet_mass"));
              }
              if(getVariableValue("L1_HTT240") || getVariableValue("L1_HTT270") || getVariableValue("L1_HTT280")){
                dijetMassHisto_L1_HTT_240_270_280_or->Fill(getVariableValue("dijet_mass"));
              }
              if(getVariableValue("L1_HTT240") || getVariableValue("L1_HTT270") || getVariableValue("L1_HTT280") || getVariableValue("L1_HTT300")){
                dijetMassHisto_L1_HTT_240_270_280_300_or->Fill(getVariableValue("dijet_mass"));
              }
              if(getVariableValue("L1_HTT240") || getVariableValue("L1_HTT270") || getVariableValue("L1_HTT280") || getVariableValue("L1_HTT300") || getVariableValue("L1_HTT320")){
                dijetMassHisto_L1_HTT_240_270_280_300_320_or->Fill(getVariableValue("dijet_mass"));
              }
            }
            if(getVariableValue("L1_HTT240") == 1 && getVariableValue("jet2_pt")>70  /*&& abs(getVariableValue("dijet_deta"))<1.1*/ && getVariableValue("jet1_pt")>70){
              if(getVariableValue("isr_pt") > 70) {
                dijetMassHisto_70->Fill(getVariableValue("dijet_mass"));
                if(abs(getVariableValue("dijet_deta"))>0.9 && abs(getVariableValue("dijet_deta"))<1.1) dijetMassHisto_70_dijet_deta_unblind->Fill(getVariableValue("dijet_deta"));
                if(getVariableValue("htAK4") > 270) dijetMassHisto_70_HT_270->Fill(getVariableValue("dijet_mass"));
                if(getVariableValue("L1_HTT270") == 1) dijetMassHisto_70_L1_HTT240_L1_HTT270->Fill(getVariableValue("dijet_mass"));
                if(getVariableValue("L1_HTT320") == 1) dijetMassHisto_70_L1_HTT240_L1_HTT320->Fill(getVariableValue("dijet_mass"));
              }
              if      (getVariableValue("isr_pt") > 40   && getVariableValue("isr_pt") <= 50 )  dijetMassHisto_40_50->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 50   && getVariableValue("isr_pt") <= 60 )  dijetMassHisto_50_60->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 60   && getVariableValue("isr_pt") <= 70 )  dijetMassHisto_60_70->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 70   && getVariableValue("isr_pt") <= 80 )  dijetMassHisto_70_80->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 80   && getVariableValue("isr_pt") <= 90 )  dijetMassHisto_80_90->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 90   && getVariableValue("isr_pt") <= 100)  dijetMassHisto_90_100->Fill(getVariableValue( "dijet_mass"));
              else if (getVariableValue("isr_pt") > 100  && getVariableValue("isr_pt") <= 150)  dijetMassHisto_100_150->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 150  && getVariableValue("isr_pt") <= 200)  dijetMassHisto_150_200->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 200  && getVariableValue("isr_pt") <= 300)  dijetMassHisto_200_300->Fill(getVariableValue("dijet_mass"));
              else if (getVariableValue("isr_pt") > 300                                      )  dijetMassHisto_300->Fill(getVariableValue("dijet_mass"));
            }
          }
        }
        else{
      	  if(store_histogram){
      	    if(getVariableValue("isr_pt") > 50  && getVariableValue("jet2_pt")>45  && abs(getVariableValue("dijet_deta"))<1.2 && getVariableValue("jet1_pt")>90 ){
      	      dijetMassHisto->Fill(getVariableValue("dijet_mass"));
      	    }
      	  }
        }


      }

      // ===== Example of dijet_mass spectrum after HLT selection =====
      // if( passedAllPreviousCuts("dijet_mass") )
      //   {
      //          if(getVariableValue("passHLT")>0)
      //            {
      //              //fast creation and filling of histograms
      //              CreateAndFillUserTH1D("h_dijet_mass_passHLT", getHistoNBins("dijet_mass"), getHistoMin("dijet_mass"), getHistoMax("dijet_mass"), getVariableValue("dijet_mass"));
      //            }
      //   }

      // reject events that did not pass level 0 cuts
      //if( !passedCut("0") ) continue;
      // ......

      // reject events that did not pass level 1 cuts
      //if( !passedCut("1") ) continue;
      // ......

      // reject events that did not pass the full cut list
      //if( !passedCut("all") ) continue;
      // ......

      // if( widejets.size() >= 2) {
      //  h_nJetFinal->Fill(widejets.size());
      //  h_DijetMass->Fill(wdijet.M());
      //  h_pT1stJet->Fill(widejets[0].Pt());
      //  h_pT2ndJet->Fill(widejets[1].Pt());
      //  h_eta1stJet->Fill(widejets[0].Eta());
      //  h_eta2ndJet->Fill(widejets[1].Eta());
      // }
      ////////////////////// User's code ends here ///////////////////////

    }                             // End loop over events

    //////////write histos

    //h_dijet_mass_NoTrigger_1GeVbin->Write ();
    //h_dijet_mass_NoTrigger->Write ();
    //h_dijet_mass_HLTpass_CaloJet40_CaloScouting_PFScouting->Write ();
    //h_dijet_mass_HLTpass_L1HTT_CaloScouting_PFScouting->Write ();
    //h_dijet_mass_HLTpass_CaloScoutingHT250->Write ();

    // h_nVtx->Write();
    // h_trueVtx->Write();
    // h_nJetFinal->Write();
    // h_pT1stJet->Write();
    // h_pT2ndJet->Write();
    // h_DijetMass->Write();
    // h_eta1stJet->Write();
    // h_eta2ndJet->Write();

    // //pT of both jets, to be built using the histograms produced automatically by baseClass
    // TH1F * h_pTJets = new TH1F ("h_pTJets","", getHistoNBins("pT1stJet"), getHistoMin("pT1stJet"), getHistoMax("pT1stJet"));
    // h_pTJets->Add( & getHisto_noCuts_or_skim("pT1stJet") ); // all histos can be retrieved, see other getHisto_xxxx methods in baseClass.h
    // h_pTJets->Add( & getHisto_noCuts_or_skim("pT2ndJet") );
    // //one could also do:  *h_pTJets = getHisto_noCuts_or_skim("pT1stJet") + getHisto_noCuts_or_skim("pT2ndJet");
    // h_pTJets->Write();
    // //one could also do:   const TH1F& h = getHisto_noCuts_or_skim// and use h
    // if (store_histogram) {
    //   reduced_skim_file_->cd();
    //   TDirectory *dir1 = reduced_skim_file_->mkdir("DijetFilter");
    //   // TDirectory *dir1 = reduced_skim_file_->GetDirectory("DijetFilter");
    //   cout << dir1 << endl;
    //   TDirectory *dir4 = dir1->mkdir("dijetMassHisto");
    //   cout << dir4 << endl;
    //   reduced_skim_file_->cd("DijetFilter/dijetMassHisto");
    //   reduced_skim_file_->ls();
    //   dijetMassHisto->Write();
    //   dijetMassHisto_40_50->Write();
    //   dijetMassHisto_50_60->Write();
    //   dijetMassHisto_60_70->Write();
    //   dijetMassHisto_70_80->Write();
    //   dijetMassHisto_80_90->Write();
    //   dijetMassHisto_90_100->Write();
    //   dijetMassHisto_100_150->Write();
    //   dijetMassHisto_150_200->Write();
    //   dijetMassHisto_200_300->Write();
    //   dijetMassHisto_300->Write();
    //   dijetMassHisto_50->Write();
    //   dijetMassHisto_50_HT_270->Write();
    //   dijetMassHisto_50_L1_HTT240_L1_HTT270->Write();
    //   dijetMassHisto_L1_HTT_240_270_or->Write();
    //   dijetMassHisto_L1_HTT_240_270_280_or->Write();
    //   dijetMassHisto_L1_HTT_240_270_280_300_or->Write();
    //   dijetMassHisto_L1_HTT_240_270_280_300_320_or->Write();
    //   // Any failure mode to implement?
    //   reduced_skim_file_->cd();
    // }
    std::cout << "analysisClass::Loop() ends" << std::endl;
  }
