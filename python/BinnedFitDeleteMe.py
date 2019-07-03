from optparse import OptionParser
import ROOT as rt
import rootTools
from framework import Config
from array import *
from itertools import *
from operator import *
from WriteDataCard import initializeWorkspace,convertToTh1xHist,convertToMjjHist,applyTurnonFunc,applyTurnonGraph
import os
import random
import sys
import math
import re

densityCorr = False

#def binnedFit(pdf, data, fitRange='Full',useWeight=False):
#    print("######################### HELLO ###############")
#    pdf.Print()
#    data.Print()
#    if useWeight:
#        fr = pdf.fitTo(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.SumW2Error(True),rt.RooFit.Save(),rt.RooFit.Minimizer('Minuit2','migrad'),rt.RooFit.Strategy(2))
#        migrad_status = fr.status()
#        hesse_status = -1
#    else:
#        nll = pdf.createNLL(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.Offset(True))
#        m2 = rt.RooMinimizer(nll)

#        m2.setPrintLevel(0)
#        m2.setPrintEvalErrors(0)
#        m2.setStrategy(2)
#        m2.setMaxFunctionCalls(100000 * 10000)
#        m2.setMaxIterations(100000 * 10000)
#        migrad_status = m2.minimize('Minuit2','scan')
#        migrad_status = m2.minimize('Minuit2','migrad')
#        improve_status = m2.minimize('Minuit2','improve')
#        hesse_status = m2.minimize('Minuit2','hesse')
#        minos_status = m2.minos()
#        if hesse_status != 3 :
#            hesse_status = m2.minimize('Minuit2','hesse')
#        fr = m2.save()
#    return fr

def rescaleaxis(h,scale=1000):
    """This function rescales the x-axis on a TGraph."""
    N = h.GetXaxis().GetXbins().GetSize()
    x = h.GetXaxis().GetXbins()
    for i in range(N):
        x[i] *= scale
    # h.Delete()
    # h.SetHistogram(0)
    return
#
# def scaleY(x):
#     return x*1000
#
# def scaleAxis(a, Scale):
#     if a.GetXbins().GetSize():
#         X=a.GetXbins()
#         for i in range(0,X.GetSize()):
#             X[i] = Scale(X[i])
#         a.Set((X.GetSize() - 1), X.GetArray())
#     else:
#         a.Set( a.GetNbins(), Scale(a.GetXmin()), Scale(a.GetXmax()) )
#     # return a
#
# def scaleXaxis(h, Scale):
#     scaleAxis(h.GetXaxis(), Scale);
#     return h

def effFit(pdf, data, conditionalObs):
    nll = pdf.createNLL(data,rt.RooFit.Range('Eff'),rt.RooFit.Offset(True),rt.RooFit.ConditionalObservables(conditionalObs))
    m2 = rt.RooMinimizer(nll)
    m2.setStrategy(2)
    m2.setMaxFunctionCalls(100000  * 10000)
    m2.setMaxIterations(100000  * 10000)
    migrad_status = m2.minimize('Minuit2','migrad')
    improve_status = m2.minimize('Minuit2','improve')
    hesse_status = m2.minimize('Minuit2','hesse')
    minos_status = m2.minos()
    fr = m2.save()
    return fr



def simFit(pdf, data, fitRange, effPdf, effData, conditionalObs):

    effNll = effPdf.createNLL(effData,rt.RooFit.Range('Eff'),rt.RooFit.Offset(True),rt.RooFit.ConditionalObservables(conditionalObs))

    fitNll = pdf.createNLL(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.Offset(True))

    simNll = rt.RooAddition("simNll", "simNll", rt.RooArgList(fitNll, effNll))

    m2 = rt.RooMinimizer(simNll)
    m2.setStrategy(2)
    m2.setMaxFunctionCalls(100000  * 10000)
    m2.setMaxIterations(100000  * 10000)
    migrad_status = m2.minimize('Minuit2','migrad')
    improve_status = m2.minimize('Minuit2','improve')
    hesse_status = m2.minimize('Minuit2','hesse')
    minos_status = m2.minos()
    fr = m2.save()

    return fr

def convertSideband(name,w,x):
    if name=="Full":
        return "Full"
    names = name.split(',')
    nBins = (len(x)-1)
    iBinX = -1
    sidebandBins = []
    for ix in range(1,len(x)):
        iBinX+=1
        w.var('mjj').setVal((x[ix]+x[ix-1])/2.)
        inSideband = 0
        for fitname in names:
            inSideband += ( w.var('mjj').inRange(fitname) )
        if inSideband: sidebandBins.append(iBinX)

    sidebandGroups = []
    for k, g in groupby(enumerate(sidebandBins), lambda (i,x):i-x):
        consecutiveBins = map(itemgetter(1), g)
        sidebandGroups.append([consecutiveBins[0],consecutiveBins[-1]+1])

    newsidebands = ''
    nameNoComma = name.replace(',','')

    for iSideband, sidebandGroup in enumerate(sidebandGroups):
        if not w.var('th1x').hasRange('%s%i'%(nameNoComma,iSideband)):
            w.var('th1x').setRange("%s%i"%(nameNoComma,iSideband),sidebandGroup[0],sidebandGroup[1])
        newsidebands+='%s%i,'%(nameNoComma,iSideband)
    newsidebands = newsidebands[:-1]
    return newsidebands

def convertFunctionToHisto(background_,name_,N_massBins_,massBins_):

    background_hist_ = rt.TH1D(name_,name_,N_massBins_,massBins_)

    for bin in range (0,N_massBins_):
        xbinLow = massBins_[bin]
        xbinHigh = massBins_[bin+1]
        binWidth_current = xbinHigh - xbinLow
        value = background_.Integral(xbinLow , xbinHigh) / binWidth_current
        background_hist_.SetBinContent(bin+1,value)

    return background_hist_

def calculateChi2AndFillResiduals(data_obs_TGraph_,background_hist_,hist_fit_residual_vsMass_,workspace_,prinToScreen_=0,effFit_=False):

    N_massBins_ = data_obs_TGraph_.GetN()
    MinNumEvents = 10
    nParFit = 4
    if workspace_.var('meff_%s'%box).getVal()>0 and workspace_.var('seff_%s'%box).getVal()>0 :
        nParFit = 6
    if workspace_.var('p54_%s'%box) != None or workspace_.var('pm4_%s'%box) != None or workspace_.var('pa4_%s'%box) != None :
        if workspace_.var('pa4_%s'%box) != None and workspace_.var('pa4_%s'%box).getVal()==0:
            nParFit = 4
        elif workspace_.var('pm4_%s'%box) != None and workspace_.var('pm4_%s'%box).getVal()==0 and workspace_.var('pm3_%s'%box) != None and workspace_.var('pm3_%s'%box).getVal()==0:
            nParFit = 3
        elif workspace_.var('pm3_%s'%box) != None and workspace_.var('pm3_%s'%box).getVal()==0:
            nParFit = 4
        else:
            nParFit = 5

    chi2_FullRangeAll = 0
    chi2_PlotRangeAll = 0
    chi2_PlotRangeNonZero = 0
    chi2_PlotRangeMinNumEvents = 0

    N_FullRangeAll = 0
    N_PlotRangeAll = 0
    N_PlotRangeNonZero = 0
    N_PlotRangeMinNumEvents = 0

    for bin in range (0,N_massBins_):
        ## Values and errors
        value_data = data_obs_TGraph_.GetY()[bin]
        err_low_data = data_obs_TGraph_.GetEYlow()[bin]
        err_high_data = data_obs_TGraph_.GetEYhigh()[bin]
        xbinCenter = data_obs_TGraph_.GetX()[bin]
        xbinLow = data_obs_TGraph_.GetX()[bin]-data_obs_TGraph_.GetEXlow()[bin]
        xbinHigh = data_obs_TGraph_.GetX()[bin]+data_obs_TGraph_.GetEXhigh()[bin]
        binWidth_current = xbinHigh - xbinLow
        #value_fit = background_.Integral(xbinLow , xbinHigh) / binWidth_current
        value_fit = background_hist_.GetBinContent(bin+1)

        ## Fit residuals
        err_tot_data = 0
        if (value_fit > value_data):
            err_tot_data = err_high_data
        else:
            err_tot_data = err_low_data
        plotRegions = plotRegion.split(',')
        checkInRegions = [xbinCenter>workspace_.var('mjj').getMin(reg) and xbinCenter<workspace_.var('mjj').getMax(reg) for reg in plotRegions]
        if effFit_: checkInRegions = [xbinCenter>workspace_.var('mjj').getMin('Eff') and xbinCenter<workspace_.var('mjj').getMax('Eff')]
        if any(checkInRegions):
            fit_residual = (value_data - value_fit) / err_tot_data
            err_fit_residual = 1
        else:
            fit_residual = 0
            err_fit_residual = 0

        ## Fill histo with residuals

        hist_fit_residual_vsMass_.SetBinContent(bin+1,fit_residual)
        hist_fit_residual_vsMass_.SetBinError(bin+1,err_fit_residual)

        ## Chi2

        chi2_FullRangeAll += pow(fit_residual,2)
        N_FullRangeAll += 1
        plotRegions = plotRegion.split(',')
        checkInRegions = [xbinCenter>workspace_.var('mjj').getMin(reg) and xbinCenter<workspace_.var('mjj').getMax(reg) for reg in plotRegions]
        if effFit_: checkInRegions = [xbinCenter>workspace_.var('mjj').getMin('Eff') and xbinCenter<workspace_.var('mjj').getMax('Eff')]
        if any(checkInRegions):
            #print '%i: obs %.0f, exp %.2f, chi2 %.2f'%(bin, value_data* binWidth_current * lumi, value_fit* binWidth_current * lumi, pow(fit_residual,2))
            chi2_PlotRangeAll += pow(fit_residual,2)
            N_PlotRangeAll += 1
            if (value_data > 0):
                chi2_PlotRangeNonZero += pow(fit_residual,2)
                N_PlotRangeNonZero += 1
                if(value_data * binWidth_current * lumi > MinNumEvents):
                    chi2_PlotRangeMinNumEvents += pow(fit_residual,2)
                    N_PlotRangeMinNumEvents += 1

    #==================
    # Calculate chi2/ndf
    #==================

    # ndf
    ndf_FullRangeAll = N_FullRangeAll - nParFit
    ndf_PlotRangeAll = N_PlotRangeAll - nParFit
    ndf_PlotRangeNonZero = N_PlotRangeNonZero - nParFit
    ndf_PlotRangeMinNumEvents = N_PlotRangeMinNumEvents - nParFit

    chi2_ndf_FullRangeAll = chi2_FullRangeAll / ndf_FullRangeAll
    chi2_ndf_PlotRangeAll = chi2_PlotRangeAll / ndf_PlotRangeAll
    chi2_ndf_PlotRangeNonZero = chi2_PlotRangeNonZero / ndf_PlotRangeNonZero
    chi2_ndf_PlotRangeMinNumEvents = chi2_PlotRangeMinNumEvents / ndf_PlotRangeMinNumEvents

    return [chi2_FullRangeAll, ndf_FullRangeAll, chi2_PlotRangeAll, ndf_PlotRangeAll, chi2_PlotRangeNonZero, ndf_PlotRangeNonZero, chi2_PlotRangeMinNumEvents, ndf_PlotRangeMinNumEvents]


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default="config/run2.config",
                  help="Name of the config file to use")
    parser.add_option('-d','--dir',dest="outDir",default="./",type="string",
                  help="Output directory to store cards")
    parser.add_option('-l','--lumi',dest="lumi", default=1.,type="float",
                  help="integrated luminosity in pb^-1")
    parser.add_option('--run-min',dest="runMin", default=0,type="int",
                  help="minimum run to consider for trigger efficiency")
    parser.add_option('--run-max',dest="runMax", default=999999,type="int",
                  help="maximum run to consider for trigger efficiency")
    parser.add_option('-b','--box',dest="box", default="CaloDijet",type="string",
                  help="box name")
    parser.add_option('--no-fit',dest="noFit",default=False,action='store_true',
                  help="Turn off fit (useful for visualizing initial parameters)")
    parser.add_option('--fit-region',dest="fitRegion",default="Full",type="string",
                  help="Fit region")
    parser.add_option('--plot-region',dest="plotRegion",default="Full",type="string",
                  help="Plot region")
    parser.add_option('-i','--input-fit-file',dest="inputFitFile", default=None,type="string",
                  help="input fit file")
    parser.add_option('-w','--weight',dest="useWeight",default=False,action='store_true',
                  help="use weight")
    parser.add_option('-s','--signal',dest="signalFileName", default=None,type="string",
                  help="input dataset file for signal pdf")
    parser.add_option('-m','--model',dest="model", default="gg",type="string",
                  help="signal model")
    parser.add_option('--mass',dest="mass", default="750",type="string",
                  help="mgluino")
    parser.add_option('--xsec',dest="xsec", default="1",type="string",
                  help="cross section in pb")
    parser.add_option('-t','--trigger',dest="triggerDataFile", default=None,type="string",
                  help="trigger data file")
    parser.add_option('--l1',dest="l1Trigger", default=False,action='store_true',
                  help="level-1 trigger")
    parser.add_option('--fit-trigger',dest="doTriggerFit", default=False,action='store_true',
                  help="fit trigger")
    parser.add_option('--fit-spectrum',dest="doSpectrumFit", default=False,action='store_true',
                  help="fit spectrum")
    parser.add_option('--sim',dest="doSimultaneousFit", default=False,action='store_true',
                  help="do simultaneous trigger fit")
    parser.add_option('--multi',dest="multi", default=True,action='store_true',
                  help="multiple background pdfs")
    parser.add_option('--linearX',dest="linearX", default=False,action='store_true',
                  help="linear X axis")

    rt.RooMsgService.instance().setGlobalKillBelow(rt.RooFit.FATAL)
    rt.gStyle.SetPaintTextFormat('+.2f')

    (options,args) = parser.parse_args()

    cfg = Config.Config(options.config)

    box = options.box
    lumi = options.lumi
    noFit = options.noFit
    fitRegion = options.fitRegion
    plotRegion = options.plotRegion
    histoName = cfg.getVariables(box, "histoName")



    myTH1 = rt.TH1F("myTH1","",100,0,1)

    w = rt.RooWorkspace("w"+box)

    paramNames, bkgs = initializeWorkspace(w,cfg,box,multi=options.multi)

    x = array('d', cfg.getBinning(box)[0]) # mjj binning
    myTH1.Rebin(len(x)-1,'data_obs_rebin',x)
    myRebinnedTH1 = rt.gDirectory.Get('data_obs_rebin')
    getattr(w,'import')(myRebinnedTH1)


    print("check3")
#    w.clearStudies()
    print("check2")
    del w
    print("check1")

