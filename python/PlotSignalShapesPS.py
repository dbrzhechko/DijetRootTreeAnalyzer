from optparse import OptionParser
import ROOT as rt
import rootTools
from framework import Config
from array import *
import os
import random
import sys
import math
from scipy.integrate import quad
from itertools import *
from operator import *
import copy

bins = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]

rebinned = rt.TH1F("rebinned","",len(bins)-1,array('f',bins))

def rebinHisto(histo):
    newhisto = rebinned.Clone(histo.GetName()+"_rebin")
    newhisto.Reset()
    for i in range(histo.GetNbinsX()):
        j = newhisto.FindBin(histo.GetBinCenter(i))
        
        newhisto.SetBinContent( j, newhisto.GetBinContent(j) + histo.GetBinContent(i) )
#        newhisto.SetBinError( j, (newhisto.GetBinContent(j)**2 + histo.GetBinError(i)**2)**0.5 )
    
    return copy.deepcopy(newhisto)

def massIterable(massList):    
    if len(massList.split(','))==1:
        massIterableList = [options.mass]
    else:
        massIterableList = list(eval(options.mass))
    return massIterableList

def setStyle():
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPaintTextFormat("1.2g")
    rt.gROOT.SetBatch()
    rt.RooMsgService.instance().setGlobalKillBelow(rt.RooFit.FATAL)

    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default="config/run2.config",
                  help="Name of the config file to use")
    parser.add_option('-d','--dir',dest="outDir",default="./",type="string",
                  help="Output directory to store results")
    parser.add_option('-b','--box',dest="box", default="MultiJet",type="string",
                  help="box name")
    parser.add_option('-m','--model',dest="model", default="gg",type="string",
                  help="signal model name")
    parser.add_option('--mass',dest="mass", default='750',type="string",
                  help="mass of resonance")
    
    (options,args) = parser.parse_args()

    box = options.box
    cfg = Config.Config(options.config)
    models = options.model.split('_')
    setStyle()
    
    lineStyle = {
        'gg': 2,
        'qq': 3,
        'gaus': 5
        }
    lineColor = {
        'gg': rt.kGreen+1,
        'qq': rt.kRed,
        'gaus': rt.kBlue
        }

        
        
    legendLabel = {
                   'gg':'gg #rightarrow X #rightarrow jj',
                   'qq':'qq #rightarrow X #rightarrow jj',
                   'gaus':'Gaussian, 7% width'
                   }
    
    c = rt.TCanvas('c','c',500,400)    
    c.SetLeftMargin(0.15) 
    c.SetBottomMargin(0.12)
    

    yLabel = "Normalized Yield / GeV"
    xLabel = "m_{jj}"
    
    x = array('d', cfg.getBinning(box)[0]) # mjj binning
    nBins = (len(x)-1)
    

    lumiLabel = "#sqrt{s} = 13 TeV" 
    boxLabel = ''

    signalFileName = {}
    for f in args:
        if f.lower().endswith('.root'):
            if f.lower().find('resonanceshapes')!=-1:
                for model in models:
                    if f.lower().find(model)!=-1:
                        signalFileName[model] = f

    histosByModel = {}
    for model in models:                
        shapes = []
        shapeFiles = {}
        shapes.append('ps')
        shapeFiles['psUp'] = signalFileName[model].replace('.root','_PSUP.root')
        shapeFiles['psDown'] = signalFileName[model].replace('.root','_PSDOWN.root')
        shapes.append('jes')
        shapeFiles['jesUp'] = signalFileName[model].replace('.root','_JESUP.root')
        shapeFiles['jesDown'] = signalFileName[model].replace('.root','_JESDOWN.root')
        shapes.append('jer')
        shapeFiles['jerUp'] = signalFileName[model].replace('.root','_JERUP.root')
        shapeFiles['jerDown'] = signalFileName[model].replace('.root','_JERDOWN.root')
        #shapeFiles['jerDown'] = signalFileName[model].replace('.root','.root')
    

        histos = {}
        for shape in shapes:
            histos[shape] = []
            
        signalFile = rt.TFile.Open(signalFileName[model])
        for rebin in [False,True]:
            for massPoint in massIterable(options.mass):
                
                h = signalFile.Get('h_%s_%s'%(model,massPoint))
                h.SetDirectory(0)
                
                if rebin:
                    h = rebinHisto(h)
                for shape in shapes:
                    fUp = rt.TFile.Open(shapeFiles[shape+'Up'])
                    hUp = fUp.Get('h_%s_%s'%(model,massPoint))
                    hUp.SetName('h_%s_%s_%sUp'%(model,massPoint,shape))
                    hUp.SetDirectory(0)
                    fDown = rt.TFile.Open(shapeFiles[shape+'Down'])
                    hDown = fDown.Get('h_%s_%s'%(model,massPoint))
                    hDown.SetName('h_%s_%s_%sDown'%(model,massPoint,shape))
                    hDown.SetDirectory(0)
                    
                    if rebin: 
                        hDown = rebinHisto(hDown)
                        hUp = rebinHisto(hUp)
                    
                    for histo in [h, hUp, hDown]:
                        histo.SetTitle('')
                        histo.SetXTitle(xLabel)
                        histo.SetYTitle(yLabel)
                        histo.SetLineColor(lineColor[model])
                        histo.SetLineStyle(lineStyle[model])
                        histo.SetLineWidth(1)
                        histo.GetXaxis().SetRangeUser(150,2.49*int(massPoint))
                        histo.SetMaximum(1.2*histo.GetBinContent(histo.GetMaximumBin()))
                        histo.GetYaxis().SetTitleOffset(1.5)
                        histo.GetYaxis().SetLabelSize(0.04)
                        histo.GetXaxis().SetLabelSize(0.04)
                        histo.GetYaxis().SetTitleSize(0.05)
                        histo.GetXaxis().SetTitleSize(0.05)
                    h.SetLineStyle(1)
                    h.SetLineWidth(3)
                    hUp.SetLineWidth(2)
                    hDown.SetLineWidth(2)
                    hUp.SetLineColor(rt.kBlue)
                    hDown.SetLineColor(rt.kBlack)
#                    hUp.SetLineColor(lineColor[model]-7)
#                    hDown.SetLineColor(lineColor[model]-7)
                    for histo in [h, hUp, hDown]:
                        histos[shape].append(histo)
                        
                        if rebin:
                            h.Draw("HIST,")
                            hUp.Draw("HIST,same")
                            hDown.Draw("HIST,same")
                        else:
                            h.Draw("c")
                            hUp.Draw("csame")
                            hDown.Draw("csame")
                    
                    
                    tLeg = rt.TLegend(0.2,0.6,0.44,0.89)
                    tLeg.SetLineColor(rt.kWhite)
                    tLeg.SetLineWidth(0)
                    tLeg.SetFillStyle(0)
                    tLeg.AddEntry(h,"%s, %s GeV"%(model,massPoint),"l")
                    tLeg.AddEntry(hUp,"%s +1#sigma"%(shape),"l")
                    tLeg.AddEntry(hDown,"%s -1#sigma"%(shape),"l")
                    
                    tLeg.Draw("same")
                
                    l = rt.TLatex()
                    l.SetTextAlign(11)
                    l.SetTextSize(0.06)
                    l.SetTextFont(62)
                    l.SetNDC()
                    l.DrawLatex(0.15,0.91,"CMS")
                    l.SetTextSize(0.05)
                    l.SetTextFont(52)
                    l.DrawLatex(0.26,0.91,"Simulation")
                    l.SetTextFont(42)
                    l.DrawLatex(0.72,0.91,"%s"%lumiLabel)
                    l.SetTextFont(52)
                    l.SetTextSize(0.045)

                    if rebin:
                        c.Print(options.outDir+"/signal_rebinned_%s_%s_%s.pdf"%(model,massPoint,shape))
                        c.Print(options.outDir+"/signal_rebinned_%s_%s_%s.C"%(model,massPoint,shape))
                    else:
                        c.Print(options.outDir+"/signal_%s_%s_%s.pdf"%(model,massPoint,shape))
                        c.Print(options.outDir+"/signal_%s_%s_%s.C"%(model,massPoint,shape))


            for shape in shapes:
                histos[shape][0].Draw("c")
                histos[shape][0].GetXaxis().SetRangeUser(150,1.49*int(massPoint))
                for histo in histos[shape][1:]:
                    histo.Draw("csame")

            histosByModel[model] = histos
                
            tLeg = rt.TLegend(0.52,0.6,0.89,0.89)
            tLeg.SetLineColor(rt.kWhite)
            tLeg.SetLineWidth(0)
            tLeg.SetFillStyle(0)
            massString = ''
            for massPoint in massIterable(options.mass):
                massString += '%s, '%massPoint
            massString = massString[:-2]
            massString += ' GeV'
            tLeg.AddEntry(h,legendLabel[model],"l")
            tLeg.AddEntry(None,massString,"")
            tLeg.AddEntry(hUp,"+1#sigma_{%s}"%(shape.upper()),"l")
            tLeg.AddEntry(hDown,"-1#sigma_{%s}"%(shape.upper()),"l")            
            tLeg.Draw("same")
            
            l = rt.TLatex()
            l.SetTextAlign(11)
            l.SetTextSize(0.06)
            l.SetTextFont(62)
            l.SetNDC()
            l.DrawLatex(0.15,0.91,"CMS")
            l.SetTextSize(0.05)
            l.SetTextFont(52)
            l.DrawLatex(0.26,0.91,"Simulation")
            l.SetTextFont(42)
            l.DrawLatex(0.72,0.91,"%s"%lumiLabel)
            l.SetTextFont(52)
            l.SetTextSize(0.045)

            if rebin:
                c.Print(options.outDir+"/signal_rebinned_%s_%s.pdf"%(model,shape))
                c.Print(options.outDir+"/signal_rebinned_%s_%s.C"%(model,shape))
            else:
                c.Print(options.outDir+"/signal_%s_%s.pdf"%(model,shape))
                c.Print(options.outDir+"/signal_%s_%s.C"%(model,shape))

            
        #for shape in shapes:
            #histosByModel['gaus'][shape][0].Draw("c")
            #for model in reversed(models):
                #histosByModel[model][shape][0].Draw("csame")
                #histosByModel[model][shape][0].GetXaxis().SetRangeUser(0,1.49*int(massPoint))
                #for histo in histosByModel[model][shape][1:]:
                    #histo.Draw("csame")
                    
            tLeg = rt.TLegend(0.52,0.6,0.89,0.89)
            tLeg.SetLineColor(rt.kWhite)
            tLeg.SetLineWidth(0)
            tLeg.SetFillStyle(0)
            massString = ''
            for massPoint in massIterable(options.mass):
                massString += '%s, '%massPoint
            massString = massString[:-2]
            massString += ' GeV'
            #tLeg = rt.TLegend(0.52,0.6,0.89,0.89)
            tLeg = rt.TLegend(0.17,0.6,0.54,0.89)
            tLeg.SetLineColor(rt.kWhite)
            tLeg.SetLineWidth(0)
            tLeg.SetFillStyle(0)
            massString = ''
            for massPoint in massIterable(options.mass):
                massString += '%s, '%massPoint
            massString = massString[:-2]
            massString += ' GeV'
            for model in models:
                tLeg.AddEntry(histosByModel[model][shape][0],'%s #pm 1#sigma_{%s}'%(legendLabel[model],shape.upper()),"l")
                #tLeg.AddEntry(histosByModel[model][shape][0],'%s'%(legendLabel[model]),"l")
                
            tLeg.AddEntry(None,massString,"")        
            tLeg.Draw("same")
            
            l = rt.TLatex()
            l.SetTextAlign(11)
            l.SetTextSize(0.06)
            l.SetTextFont(62)
            l.SetNDC()
            l.DrawLatex(0.15,0.91,"CMS")
            l.SetTextSize(0.05)
            l.SetTextFont(52)
            l.DrawLatex(0.26,0.91,"Simulation")
            l.SetTextFont(42)
            l.DrawLatex(0.72,0.91,"%s"%lumiLabel)
            l.SetTextFont(52)
            l.SetTextSize(0.045)

            if rebin:
                c.Print(options.outDir+"/signal_rebinned_%s_%s.pdf"%(options.model,shape))
                c.Print(options.outDir+"/signal_rebinned_%s_%s.C"%(options.model,shape))
            else:
                c.Print(options.outDir+"/signal_%s_%s.pdf"%(options.model,shape))
                c.Print(options.outDir+"/signal_%s_%s.C"%(options.model,shape))

