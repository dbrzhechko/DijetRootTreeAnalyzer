#! /usr/bin/env python
from ROOT import *
import os, multiprocessing
import copy
import math
from array import array
import optparse
import re

gStyle.SetOptStat(0)
default_dir = "output_20180418_163054"
default_mass = "150,200,300,400,500,600,800,1000"
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-d", "--directory", action="store", type="string", dest="dir", default=default_dir)
parser.add_option("-m", "--mass", action="store", type="string", dest="mass", default=default_mass)
parser.add_option("", "--matching", action="store", type="string", dest="matching", default="")
# parser.add_option("-v", "--var", action="store", type="string", dest="var", default="dijet_mass")
parser.add_option("-b", "--batch", action="store", type="string", dest="batch", default="True")
(options, args) = parser.parse_args()
#selection = "isr_pt > 70 && jet2_pt>70  && abs(dijet_deta)<1.1 && jet1_pt>70"
step = 10.
numberOfBins = 14000
leftEdge = 0
rightEdge = 14000
massBoundaries = array('f',[  1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176,
                    197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606,
                    649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246,
                    1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132,
                    2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416,
                    3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253,
                    5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866,
                    8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179,
                    11571, 11977, 12395, 12827, 13272, 13732, 14000])
getHistoNBins = {"mjj": 10000, "mjj_ratio": 75  }
getHistoMin   = {"mjj": 0,     "mjj_ratio": 0   }
getHistoMax   = {"mjj": 10000, "mjj_ratio": 1.5 }


matching = options.matching

if matching is not "":
    matching="_"+matching
# outputFileName = [  #"rootfile_list_VectorDiJet1JetNotRightOne.root",
#                     "rootfile_list_VectorDiJet1Jet"+matching+".root",
#                     "rootfile_list_VectorDiJet1Jet_JERUP"+matching+".root",
#                     "rootfile_list_VectorDiJet1Jet_JERDOWN"+matching+".root",
#                     "rootfile_list_VectorDiJet1Jet_JESUP"+matching+".root",
#                     "rootfile_list_VectorDiJet1Jet_JESDOWN"+matching+".root"]
# h_mjj_ratio_array = {}

# file_prefiring.Close()
def prob_mass(rootTree, vars, outputFileName, mass):
    returnTH3F = TH3F("dijetMassHisto_th3f_%s"%mass, "Dijet Mass TH3F", 5000,0,5000, 110,40,150, 10,0.4,1.4)
    for entry in rootTree:
        isr_pt      = rootTree.isr_pt
        dijet_deta  = rootTree.dijet_deta
        dijet_mass  = rootTree.dijet_mass
        returnTH3F.Fill(dijet_mass,isr_pt,dijet_deta)
        # rootTree.Draw(vars[0]+":"+vars[1]+":"+vars[2]+">>dijetMassHisto_th3f_%s"%mass,"")
    return returnTH3F


def mass_shapes(directory, mass, vars, outputFileName):
    rootTree = {}
    outFile=TFile(outputFileName,"RECREATE")
    pathlist = os.listdir(directory)
    # print data
    mass = re.split(",|, ", mass)
    h_th3f = TH3F()
    for m in mass:
        rootTree[m] = TChain("rootTupleTree/tree")
        print "Creating histogram with %s GeV mass"%m
        for file in pathlist:
            if ('rootfile_list_VectorDiJet1Jet_'+m) in file and 'reduced_skim.root' in file:
                rootTree[m].Add(directory+"/"+file)
                fileName = file
                print "File %s added to %s GeV mass histogram"%(file, m)
        h_th3f = prob_mass(rootTree[m], vars, outputFileName,m)
        h_th3f.Write()
    print "Files:"
    # for out in outputFileName:
    #     print "\t"+out
    print "were created!"

outputFileName = "th3f_mc.root"
vars = ["dijet_mass", "isr_pt", "dijet_deta"]
mass_shapes(options.dir, options.mass, vars, outputFileName)
