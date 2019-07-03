import ROOT
from inputAcceptance import acc_dict

ROOT.gInterpreter.ProcessLine(".L function.C+")

lumi = 1.992 #fb-1
lumi = lumi*1000 #pb-1

outputFileName = "histograms_isrPt_signal_%d.root"
variable = "dijet_mass"
selection = "isr_pt > %d && abs(jet1_eta)<2.5 && abs(jet2_eta)<2.5 && abs(isr_eta)<2.5 && abs(jet1_eta -jet2_eta)<1.1 && L1_HTT240"

variable_flipped = "MyMass(jet1_pt,  jet1_eta, jet1_phi, jet1_mass, jet2_pt,-jet2_eta, jet2_phi, jet2_mass)*weight2_rnd(jet1_pt*jet2_pt)"
selection_flipped = "isr_pt > %d && abs(jet1_eta)<2.5 && abs(jet2_eta)<2.5 && abs(isr_eta)<2.5 && abs(jet1_eta +jet2_eta)<1.1 && L1_HTT240"


isrPts = range(40,100)
#isrPts = [70]

fileNames = ["/work/sdonato/scoutingAnalysis/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer/silvio/mc_signal_%d.root"]

signalMasses = [300, 400, 500, 600]
#signalMasses = [300]

histos = {}

#asymptoticFile = "/work/sdonato/scoutingAnalysis/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer/cards_qq_freq_bak/xsecUL_Asymptotic_qq_CaloTrijet2016.root"
asymptoticFile = "/work/sdonato/scoutingAnalysis/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer/cards_qq_freq_fullFakeLumi/xsecUL_Asymptotic_qq_CaloTrijet2016.root"
asymptoticRootFile = ROOT.TFile.Open(asymptoticFile,"READ")
xsecTree = asymptoticRootFile.Get("xsecTree")
limits = {}
for entry in xsecTree:
    limits[entry.mass] = entry.xsecULExp_CaloTrijet2016 / acc_dict["jets01"][entry.mass] #sigma(pb)*A / A

xmin, xmax, xbins = 0, 5000, 5000
for flipped in [True,False]:
    for signalMass in signalMasses:
        fName = outputFileName%signalMass
        if flipped: fName = fName.replace("signal_","signal_flipped_")
        newFile = ROOT.TFile(outputFileName%signalMass,"recreate")
        for fileName in fileNames:
            file_ = ROOT.TFile.Open(fileName%signalMass)
            tree = file_.Get("tree")
            nentries = tree.GetEntries()
            for isrPt in isrPts:
                histos[isrPt] = ROOT.TH1F("dijetMassHisto_isrptcut_%d"%isrPt,"", xbins, xmin, xmax)
                print("isrPt = %d"%isrPt)
                histos[isrPt].Reset()
                if flipped:
                    tree.Draw("%s >> dijetMassHisto_isrptcut_%d"%(variable_flipped,isrPt),selection_flipped%isrPt,"goff")
                else:
                    tree.Draw("%s >> dijetMassHisto_isrptcut_%d"%(variable,isrPt),selection%isrPt,"goff")
                histos[isrPt].Scale(lumi*limits[signalMass]/nentries)
                newFile.cd()
                histos[isrPt].Write()
            file_.Close()
        newFile.Close()

