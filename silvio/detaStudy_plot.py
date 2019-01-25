import ROOT
import copy

ROOT.gROOT.SetBatch(1)

mass = 600

wj = 1.1

#wjs = [round(x/10.,1) for x in range(4,19,1)]

#detas = [round(x/10.,1) for x in range(4,19,1)]

masses = [
    200, 300, 400, 500, 600, 800
]

#masses = [
#    mass
#]

selection = "isr_pt>50 && HLT_CaloScoutingHT250 "
variable = "abs(dijet_deta)"
binning = "(60,0,3)"

dataFileName = "/mnt/t3nfs01/data01/shome/dbrzhech/DijetScouting/CMSSW_8_0_30/src/DijetRootTreeAnalyzer/data_wj_studies/data_wj_studies_%sdata.root"
signalFileName = "/mnt/t3nfs01/data01/shome/sdonato/scoutingNew/copy/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer/wideJetMC/signal_%s_wj%s.root"

###################################

ROOT.gStyle.SetOptStat(0)

c1 = ROOT.TCanvas("c1","",1280,720)
#c1.SetLogy()
c1.SetGridx()
c1.SetGridy()

colors = [
ROOT.kRed +3,
ROOT.kRed +1,
ROOT.kRed -4,
ROOT.kRed -7,
ROOT.kRed -9,
ROOT.kGreen +3,
ROOT.kGreen +1,
ROOT.kGreen -4,
ROOT.kGreen -7,
ROOT.kGreen -9,
ROOT.kBlue +3,
ROOT.kBlue +1,
ROOT.kBlue -4,
ROOT.kBlue -7,
ROOT.kBlue -9,
ROOT.kRed +3,
ROOT.kRed +1,
ROOT.kRed -4,
ROOT.kRed -7,
ROOT.kRed -9,
ROOT.kGreen +3,
ROOT.kGreen +1,
ROOT.kGreen -4,
ROOT.kGreen -7,
ROOT.kGreen -9,
ROOT.kBlue +3,
ROOT.kBlue +1,
ROOT.kBlue -4,
ROOT.kBlue -7,
ROOT.kBlue -9,
]


def getHisto(fileName, sel = selection):
    file_ = ROOT.TFile.Open(fileName)
    tree = file_.Get("rootTupleTree/tree")
    tree.Draw(variable + ">> histo"+binning, sel + "&& dijet_mass>%f && dijet_mass<%f"%(mass*0.9,mass*1.1))
    print(sel + "&& dijet_mass>%f && dijet_mass<%f"%(mass*0.9,mass*1.1))
    histo = file_.Get("histo").Clone(fileName.replace("/",""))
    histo.SetLineWidth(2)
    return copy.copy(histo)

def getBestSsqrtB(dat,sig):
    s_sqrtB_max = 0
    for i in range(mass-100,mass,10):
        bin_min = sig.FindBin(i)
        for j in range(mass,mass+300,10):
            bin_max = sig.FindBin(j)
            s = 1.*sig.Integral(bin_min, bin_max)
            b = 1.*dat.Integral(bin_min, bin_max)
            s_sqrtB = s/(b**0.5)
            if s_sqrtB>s_sqrtB_max:
                s_sqrtB_max = s_sqrtB
                minBin = dat.GetBinLowEdge(bin_min)
                maxBin = dat.GetBinLowEdge(bin_max+1)
    #            print(i,j,s,b,s_sqrtB_max)
    return s_sqrtB_max,minBin,maxBin

def getSsqrtB(dat,sig, mass):
    bin_min = sig.FindBin(mass*0.98)
    bin_max = sig.FindBin(mass*1.02)
    s = 1.*sig.Integral(bin_min, bin_max)
    b = 1.*dat.Integral(bin_min, bin_max)
    s_sqrtB_max = s/(b**0.5+1E-9)
    minBin = dat.GetBinLowEdge(bin_min)
    maxBin = dat.GetBinLowEdge(bin_max+1)
    return s_sqrtB_max,minBin,maxBin


data = {}
signal = {}
signalGoodMatch = {}
data = getHisto(dataFileName%wj)
for mass in masses:
    signal[(mass)] = getHisto(signalFileName%(mass,wj))
    signalGoodMatch[(mass)] = getHisto(signalFileName%(mass,wj), selection + " && (sqrt(TVector2::Phi_mpi_pi(jet1_phi-jet1MC_phi)**2 + (jet1_eta-jet1MC_eta)**2)<0.4 && sqrt(TVector2::Phi_mpi_pi(jet2_phi-jet2MC_phi)**2 + (jet2_eta-jet2MC_eta)**2)<0.4) ")
print(data)

print(data)
print(signal)

'''
## rescale to show plots nicer
for mass in masses:
    bin_ = data.FindBin(mass)
    scale = 10. * data.GetBinContent(bin_) / signal[(0.4,mass)].GetBinContent(bin_)
    for deta in detas:
        signal[(mass)].Scale(scale)
        signalGoodMatch[(mass)].Scale(scale)
'''



for matching in [True,False]:
    if matching:
        signals = signal
    else:
        signals = signalGoodMatch
    for mass in masses:
        leg = ROOT.TLegend(0.78,0.83,0.98,0.98)
#        leg.SetHeader("")
        print("M(jj) = %s GeV. Matching %s"%(mass,matching))
        data.SetLineColor(ROOT.kBlack)
        data.Scale(1./data.Integral())
        signals[(mass)].Scale(1./signals[(mass)].Integral())
        signals[(mass)].SetLineColor(ROOT.kRed)
        signals[(mass)].SetTitle("#Delta#eta (%d GeV)"%mass)
        signals[(mass)].GetYaxis().SetTitle("Events")
        signals[(mass)].GetXaxis().SetTitle("#Delta#eta")
#        signals[(mass)].GetYaxis().SetRangeUser(1E1,1E4)
        signals[(mass)].SetMaximum(1.2*max(signals[(mass)].GetMaximum(),data.GetMaximum()))
        signals[(mass)].SetMinimum(0)
        signals[(mass)].Draw("")
                
        data.Draw("same")
        leg.AddEntry(data,"data")
        leg.AddEntry(signals[(mass)],"signal")
    #    SsqrtB,minBin,maxBin = getBestSsqrtB(data[wj],signalGoodMatch[(wj,mass)])
    #    print("wide jet R=%s, S/sqrt(B)=%s, in mjj=[%s,%s]"%(wj,SsqrtB,minBin,maxBin))
        SsqrtB,minBin,maxBin = getSsqrtB(data,signals[(mass)],mass)
        print("wide jet S/sqrt(B)=%s, in mjj=[%s,%s]"%(SsqrtB,minBin,maxBin))
        leg.Draw()

        c1.Update()
        c1.Modified()
        if matching:
            c1.SaveAs("deta_%s_matching.png"%mass)
            c1.SaveAs("deta_%s_matching.pdf"%mass)
        else:
            c1.SaveAs("deta_%s.png"%mass)
            c1.SaveAs("deta_%s.pdf"%mass)

#data[wj].Scale(1./data[wj].Integral())
#signal[(wj,mass)].Scale(1./signal[(wj,mass)].Integral())
#signalGoodMatch[(wj,mass)].Scale(1./signalGoodMatch[(wj,mass)].Integral())

#data[wj].Draw()
#signal[(wj,mass)].Draw("same")
#signalGoodMatch[(wj,mass)].Draw("same")


sig = signalGoodMatch[(mass)]
dat = data

