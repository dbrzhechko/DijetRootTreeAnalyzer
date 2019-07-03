#! /usr/bin/env python
from ROOT import *
import os, multiprocessing
import copy
import math
from array import array
import optparse

gROOT.SetBatch(1)

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-i", "--input", action="store", type="string", dest="input", default="dijet_isr_distr_default")
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="dijet_isr_distr_default")
parser.add_option("--histo", action="store", type="string", dest="histoName", default="dijet_mass")
(options, args) = parser.parse_args()

def th3ftoth1f(h3_mjj, fin, histoName, isrPtCut, dijetDetaSelection):
    fin.GetObject("DijetFilter/dijetMassHisto/%s"%histoName, h3_mjj)
    # fin.GetObject("DijetFilter/dijetMassHisto/dijet_mass_cr", h3_mjj)
    h_mjj_name = "dijetMassHisto_isrptcut_%s"%(isrPtCut)
    h_mjj = TH1D(h_mjj_name, "Dijet Mass", 5000, 0, 5000)
    h_mjj_add = {}
    for i,cuts in dijetDetaSelection.iteritems():
        h_mjj_add[i]=TH1D(h_mjj_name+"_"+str(i), "Dijet Mass", 5000, 0, 5000)
    isrPtCutBin = (isrPtCut-40)+1
    # dijetdetacutMinBin = int(round((dijetDetaSelection[0][0]+1.5)*20))+1
    # dijetdetacutMaxBin = int((dijetDetaSelection[0][1]+1.5)*20)
    # dijetdetacutMinBin1 = int(round((dijetDetaSelection[1][0]+1.5)*20))+1
    # dijetdetacutMaxBin1 = int((dijetDetaSelection[1][1]+1.5)*20)
    for i,cuts in dijetDetaSelection.iteritems():
        dijetdetacutMinBin = int(round((dijetDetaSelection[i][0]+1.5)*20))+1
        # print "dijetdetacutMinBin = %s"%dijetdetacutMinBin
        dijetdetacutMaxBin = int(round((dijetDetaSelection[i][1]+1.5)*20))
        # print "dijetdetacutMaxBin = %s"%dijetdetacutMaxBin
        h_mjj_add[i]=h3_mjj.ProjectionX(h_mjj_name+"_"+str(i), isrPtCutBin, h3_mjj.GetNbinsY()+1, dijetdetacutMinBin, dijetdetacutMaxBin)
        # print "%s.Integral() = %4.2f"%(h_mjj_name,h_mjj_add[i].Integral())
    binContent=0
    for i in range(1,h_mjj.GetNbinsX()+1):
        for j,hist in h_mjj_add.iteritems():
            binContent+=hist.GetBinContent(i)
        h_mjj.SetBinContent(i,binContent)
        binContent=0
    # h_mjj=h3_mjj.ProjectionX(h_mjj_name, isrPtCutBin, h3_mjj.GetNbinsY()+1, dijetdetacutMinBin, dijetdetacutMaxBin)
    # h_mjj.Add(h3_mjj.ProjectionX(h_mjj_name, isrPtCutBin, h3_mjj.GetNbinsY()+1, dijetdetacutMinBin1, dijetdetacutMaxBin1))

    # for i,sel in dijetDetaSelection[1:-1].iteritems():
    #     dijetdetacutMinBin = int(round((sel[0]+1.5)*20))+1 if sel[0] >= -1.5 and sel[0] <= 1.5 else 0
    #     dijetdetacutMaxBin = int((sel[1]+1.5)*20) if sel[1] >= -1.5 and sel[1] <= 1.5 else 61
    #     h_mjj.Add(h3_mjj.ProjectionX(h_mjj_name, isrPtCutBin, h3_mjj.GetNbinsY()+1, dijetdetacutMinBin, dijetdetacutMaxBin))
    # h_mjj = h3_mjj.ProjectionX(h_mjj_name, isrptcutMinBin,111, 9,52)
    # h_mjj.Draw()
    return h_mjj

def main(opt):
    fin = TFile(opt.input)
    h3_mjj = TH3F("dijetMassHisto_th3f", "Dijet Mass TH3F", 5000,0,5000, 110,40,150, 60,-1.5,1.5)
    fout = TFile(opt.output, "RECREATE")
    step = 1
#    dijetDetaSelection={0: [-1.55,-1.1], 1: [1.1,1.55]}
#    dijetDetaSelection={0: [-1.5,-1.1], 1: [1.1,1.5]}
#    dijetDetaSelection={0: [-1.4,-1.1], 1: [1.1,1.4]}

#    dijetDetaSelection={0: [-1.1,-0.9], 1: [0.9,1.1]}
#    dijetDetaSelection={0: [-1.0,-0.5], 1: [0.5,1.0]}
#    dijetDetaSelection={0:  [-0.5,0.5]}
    dijetDetaSelection={0: [-1.1,1.1]}
    for isrptcutMin in range(40,100,step):
        thist1f=th3ftoth1f(h3_mjj, fin, options.histoName,isrptcutMin, dijetDetaSelection)
        thist1f.Write()
        print "Histogram %s was created!"%(thist1f.GetName())
    fin.Close()
    print "File %s was created!"%opt.output
    fout.Close()

main(options)
