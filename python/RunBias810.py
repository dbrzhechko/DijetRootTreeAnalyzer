from optparse import OptionParser
import ROOT as rt
import rootTools
from framework import Config
from array import *
import os
import sys
from RunCombine import massIterable


def submit_jobs_uzh(options,args):    
    pwd = os.environ['PWD']
    exec_me("mkdir -p %s"%(options.outDir),False)
    exec_me("mkdir -p submit_bias_study",False)
    exec_me("mkdir -p submit_bias_study/log",False)
    opts = sys.argv[:]
    idx = opts.index("--queue")
    del opts[idx]
    del opts[idx]
    idx = opts.index("--mass")
    del opts[idx]
    del opts[idx]
    if "--dry-run" in opts:
        idx = opts.index("--dry-run")
        del opts[idx]
    command = " ".join(opts)
    for massPoint in massIterable(options.mass):
        commandMass = "python " + command + " --mass "+str(massPoint)
        optString = ""
        if options.asymptoticFile is None:
            optString = "_bkgOnly"
        fileName = 'submit_bias_study/lauch%s_%s_%s_%s.sh'%(optString,str(massPoint),options.genPdf,options.fitPdf)
        pwd = os.environ['PWD']
        print('######### Creating %s ############'%fileName)
        txt = open(fileName,'w')
        txt.write("""
#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc530
cd %s
eval `scramv1 runtime -sh`
%s
"""%(pwd,commandMass))
        txt.close()
        exec_me("qsub -o %s/submit_bias_study/log -e %s/submit_bias_study/log -q %s.q %s"%(pwd,pwd,options.queue.replace(".q",""),fileName),options.dryRun)
# use /dev/null to avoid seg fault for mysterious reason...
#        exec_me("qsub -e %s/submit_bias_study/log -o /dev/null -q %s.q %s"%(pwd,options.queue.replace(".q",""),fileName),options.dryRun)


def exec_me(command,dryRun=True):
    print command
    if not dryRun: os.system(command)

def main(options,args):
    signalDsName = ''
    if box=='CaloDijet2016':
        signalDsName = '../inputs/ResonanceShapes_%s_13TeV_CaloScouting_Spring16.root'%model
    elif box=='PFDijet2016':
        signalDsName = '../inputs/ResonanceShapes_%s_13TeV_Spring16.root'%model
    elif box=='CaloTrijet2016':
        signalDsName = '../inputs/ResonanceShapes_%s_13TeV_CaloScouting_2016.root'%model


    signalSys = ''
    if not(options.noSignalSys):
        if box=='CaloDijet2016':
            signalSys  = '--jesUp ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_Spring16_JESUP.root --jesDown ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_Spring16_JESDOWN.root'%(model,model)
            signalSys += ' --jerUp ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_Spring16_JERUP.root --jerDown ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_Spring16_JERDOWN.root'%(model,model)
        elif box=='PFDijet2016':
            signalSys  =   '--jesUp ../inputs/ResonanceShapes_%s_13TeV_Spring16_JESUP.root --jesDown ../inputs/ResonanceShapes_%s_13TeV_Spring16_JESDOWN.root'%(model,model)
            signalSys += ' --jerUp ../inputs/ResonanceShapes_%s_13TeV_Spring16_JERUP.root'%(model)
        elif box=='CaloTrijet2016':
            signalSys  = ' --jesUp ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_2016_JESUP.root --jesDown ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_2016_JESDOWN.root'%(model,model)
            signalSys += ' --jerUp ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_2016_JERUP.root --jerDown ../inputs/ResonanceShapes_%s_13TeV_CaloScouting_2016_JERDOWN.root'%(model,model)


    xsecTree = None
    rDict = {}
    if options.asymptoticFile is not None:
        print "INFO: Input ref xsec file!"
        asymptoticRootFile = rt.TFile.Open(options.asymptoticFile,"READ")
        xsecTree = asymptoticRootFile.Get("xsecTree")
        xsecTree.Draw('>>elist','','entrylist')
        elist = rt.gDirectory.Get('elist')
        entry = -1
        while True:
            entry = elist.Next()
            if entry == -1: break
            xsecTree.GetEntry(entry)
            rDict[int(eval('xsecTree.mass'))] = eval('xsecTree.xsecULExp_%s'%box)/options.xsec * 5./2 # fact 5/2 is to pass from 2sigma exclusion to 5sigma excess 
    else:
        for massPoint in massIterable(options.mass):
            rDict[int(massPoint)] = options.r
    print rDict

    xsecString = '--xsec %f'%options.xsec
    rRangeString =  '--rMin %s --rMax %s'%(options.rMin,options.rMax)

    fixStringGen = '--setParameters pdf_index=%i'%(pdfIndexMap[options.genPdf])
    freezeStringGen = '--freezeParameters pdf_index'
#    if options.genPdf != 'fiveparam':
#        freezeStringGen += ',p51_CaloTrijet2016,p52_CaloTrijet2016,p53_CaloTrijet2016,p54_CaloTrijet2016'
#    if options.genPdf != 'modexp':
#        freezeStringGen += ',pm1_CaloTrijet2016,pm2_CaloTrijet2016,pm3_CaloTrijet2016,pm4_CaloTrijet2016'
#    if options.genPdf != 'atlas':
#        freezeStringGen += ',pa1_CaloTrijet2016,pa2_CaloTrijet2016,pa3_CaloTrijet2016,pa4_CaloTrijet2016'
#    if options.genPdf != 'atlas6':
#        freezeStringGen += ',pa61_CaloTrijet2016,pa62_CaloTrijet2016,pa63_CaloTrijet2016,pa64_CaloTrijet2016,pa65_CaloTrijet2016'
##    if options.genPdf != 'fourparam':
##        freezeStringGen += ',p1_CaloTrijet2016,p2_CaloTrijet2016,p3_CaloTrijet2016'
#    if options.fitPdf != 'silvio4':
#        freezeStringGen += ',p1s4_CaloTrijet2016,p2s4_CaloTrijet2016,p3s4_CaloTrijet2016'
#    if options.fitPdf != 'silvio5':
#        freezeStringGen += ',p1s5_CaloTrijet2016,p2s5_CaloTrijet2016,p3s5_CaloTrijet2016,p4s5_CaloTrijet2016'
#    if options.fitPdf != 'silvio6':
#        freezeStringGen += ',p1s6_CaloTrijet2016,p2s6_CaloTrijet2016,p3s6_CaloTrijet2016,p4s6_CaloTrijet2016,p5s6_CaloTrijet2016'
##    if options.fitPdf != 'silviobias4':
##        freezeStringGen += ',p1sb4_CaloTrijet2016,p2sb4_CaloTrijet2016,p3sb4_CaloTrijet2016'
#    if options.fitPdf != 'nom7':
#        freezeStringGen += ',p7nom1_CaloTrijet2016,p7nom2_CaloTrijet2016,p7nom3_CaloTrijet2016,p7nom4_CaloTrijet2016,p7nom5_CaloTrijet2016,p7nom6_CaloTrijet2016'
#    if options.fitPdf != 'nom6':
#        freezeStringGen += ',p6nom1_CaloTrijet2016,p6nom2_CaloTrijet2016,p6nom3_CaloTrijet2016,p6nom4_CaloTrijet2016,p6nom5_CaloTrijet2016'
#    if options.fitPdf != 'nom5':
#        freezeStringGen += ',p5nom1_CaloTrijet2016,p5nom2_CaloTrijet2016,p5nom3_CaloTrijet2016,p5nom4_CaloTrijet2016'
#    if options.fitPdf != 'nom4':
#        freezeStringGen += ',p4nom1_CaloTrijet2016,p4nom2_CaloTrijet2016,p4nom3_CaloTrijet2016'
#    if options.fitPdf != 'nom3':
#        freezeStringGen += ',p3nom1_CaloTrijet2016,p3nom2_CaloTrijet2016'
#    if options.fitPdf != 'alt7':
#        freezeStringGen += ',p7alt1_CaloTrijet2016,p7alt2_CaloTrijet2016,p7alt3_CaloTrijet2016,p7alt4_CaloTrijet2016,p7alt5_CaloTrijet2016,p7alt6_CaloTrijet2016'
#    if options.fitPdf != 'alt6':
#        freezeStringGen += ',p6alt1_CaloTrijet2016,p6alt2_CaloTrijet2016,p6alt3_CaloTrijet2016,p6alt4_CaloTrijet2016,p6alt5_CaloTrijet2016'
#    if options.fitPdf != 'alt5':
#        freezeStringGen += ',p5alt1_CaloTrijet2016,p5alt2_CaloTrijet2016,p5alt3_CaloTrijet2016,p5alt4_CaloTrijet2016'
#    if options.fitPdf != 'alt4':
#        freezeStringGen += ',p4alt1_CaloTrijet2016,p4alt2_CaloTrijet2016,p4alt3_CaloTrijet2016'
#    if options.fitPdf != 'alt3':
#        freezeStringGen += ',p3alt1_CaloTrijet2016,p3alt2_CaloTrijet2016'


    fixStringFit = '--setParameters pdf_index=%i'%(pdfIndexMap[options.fitPdf])
    freezeStringFit = '--freezeParameters pdf_index'
    if options.fitPdf != 'fiveparam':
        freezeStringFit += ',p51_CaloTrijet2016,p52_CaloTrijet2016,p53_CaloTrijet2016,p54_CaloTrijet2016'
    if options.fitPdf != 'modexp':
        freezeStringFit += ',pm1_CaloTrijet2016,pm2_CaloTrijet2016,pm3_CaloTrijet2016,pm4_CaloTrijet2016'
    if options.fitPdf != 'atlas':
        freezeStringFit += ',pa1_CaloTrijet2016,pa2_CaloTrijet2016,pa3_CaloTrijet2016,pa4_CaloTrijet2016'
    if options.fitPdf != 'atlas6':
        freezeStringFit += ',pa61_CaloTrijet2016,pa62_CaloTrijet2016,pa63_CaloTrijet2016,pa64_CaloTrijet2016,pa65_CaloTrijet2016'
#    if options.fitPdf != 'fourparam':
#        freezeStringFit += ',p1_CaloTrijet2016,p2_CaloTrijet2016,p3_CaloTrijet2016'
    if options.fitPdf != 'silvio4':
        freezeStringFit += ',p1s4_CaloTrijet2016,p2s4_CaloTrijet2016,p3s4_CaloTrijet2016'
    if options.fitPdf != 'silvio5':
        freezeStringFit += ',p1s5_CaloTrijet2016,p2s5_CaloTrijet2016,p3s5_CaloTrijet2016,p4s5_CaloTrijet2016'
    if options.fitPdf != 'silvio6':
        freezeStringFit += ',p1s6_CaloTrijet2016,p2s6_CaloTrijet2016,p3s6_CaloTrijet2016,p4s6_CaloTrijet2016,p5s6_CaloTrijet2016'
    if options.fitPdf != 'polext7':
        freezeStringFit += ',p7p1_CaloTrijet2016,p7p2_CaloTrijet2016,p7p3_CaloTrijet2016,p7p4_CaloTrijet2016,p7p5_CaloTrijet2016,p7p6_CaloTrijet2016'
    if options.fitPdf != 'pol8':
        freezeStringFit += ',p8p1_CaloTrijet2016,p8p2_CaloTrijet2016,p8p3_CaloTrijet2016,p8p4_CaloTrijet2016,p8p5_CaloTrijet2016,p8p6_CaloTrijet2016,p8p7_CaloTrijet2016'
    if options.fitPdf != 'nom7':
        freezeStringFit += ',p7nom1_CaloTrijet2016,p7nom2_CaloTrijet2016,p7nom3_CaloTrijet2016,p7nom4_CaloTrijet2016,p7nom5_CaloTrijet2016,p7nom6_CaloTrijet2016'
    if options.fitPdf != 'nom6':
        freezeStringFit += ',p6nom1_CaloTrijet2016,p6nom2_CaloTrijet2016,p6nom3_CaloTrijet2016,p6nom4_CaloTrijet2016,p6nom5_CaloTrijet2016'
    if options.fitPdf != 'nom5':
        freezeStringFit += ',p5nom1_CaloTrijet2016,p5nom2_CaloTrijet2016,p5nom3_CaloTrijet2016,p5nom4_CaloTrijet2016'
    if options.fitPdf != 'nom4':
        freezeStringFit += ',p4nom1_CaloTrijet2016,p4nom2_CaloTrijet2016,p4nom3_CaloTrijet2016'
    if options.fitPdf != 'nom3':
        freezeStringFit += ',p3nom1_CaloTrijet2016,p3nom2_CaloTrijet2016'
    if options.fitPdf != 'alt7':
        freezeStringFit += ',p7alt1_CaloTrijet2016,p7alt2_CaloTrijet2016,p7alt3_CaloTrijet2016,p7alt4_CaloTrijet2016,p7alt5_CaloTrijet2016,p7alt6_CaloTrijet2016'
    if options.fitPdf != 'alt6':
        freezeStringFit += ',p6alt1_CaloTrijet2016,p6alt2_CaloTrijet2016,p6alt3_CaloTrijet2016,p6alt4_CaloTrijet2016,p6alt5_CaloTrijet2016'
    if options.fitPdf != 'alt5':
        freezeStringFit += ',p5alt1_CaloTrijet2016,p5alt2_CaloTrijet2016,p5alt3_CaloTrijet2016,p5alt4_CaloTrijet2016'
    if options.fitPdf != 'alt4':
        freezeStringFit += ',p4alt1_CaloTrijet2016,p4alt2_CaloTrijet2016,p4alt3_CaloTrijet2016'
    if options.fitPdf != 'alt3':
        freezeStringFit += ',p3alt1_CaloTrijet2016,p3alt2_CaloTrijet2016'

    pwd = os.environ['PWD']
#    toysOptions = "--toysFrequentist --bypassFrequentistFit " #non fitta
    toysOptions = "--toysFrequentist" #fitta
#    toysOptions = "" #non fitta
#    toysOptions = "--toysNoSystematics" #1fit
#    toysOptions = "--toysNoSystematics --bypassFrequentistFit" #1fit
    for massPoint in massIterable(options.mass):
#        rDict[int(massPoint)] = -0.1
        #exec_me('python python/WriteDataCard.py -m %s --mass %s -i %s -l %f -c %s -b %s -d %s %s %s %s %s --multi'%(model, massPoint, options.inputFitFile,1000*lumi,options.config,box,options.outDir,signalDsName,backgroundDsName[box],xsecString,signalSys),options.dryRun)
        #exec_me('combine -M GenerateOnly %s/dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s %s %s %s --toysFrequentist --saveToys --expectSignal %.3f -t %i'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,rRangeString,fixStringGen,freezeStringGen,rDict[int(massPoint)],options.toys),options.dryRun)
        #exec_me('combine  -v1 -M MaxLikelihoodFit --robustFit=1  %s/dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s --toysFile higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.GenerateOnly.mH120.123456.root -t %i %s %s %s --minimizerTolerance 1 --minimizerStrategy 2  --saveWorkspace'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.toys,rRangeString,fixStringFit,freezeStringFit),options.dryRun)
#        exec_me('mv higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.GenerateOnly.mH120.123456.root %s/'%(model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.outDir),options.dryRun)
#        exec_me('mv higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.MaxLikelihoodFit.mH120.123456.root %s/'%(model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.outDir),options.dryRun)
#        exec_me('mv mlfit%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.root %s/'%(model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.outDir),options.dryRun)
        exec_me('cd %s && python ../python/WriteDataCard.py -m %s --mass %s -i ../%s -l %f -c ../%s -b %s -d %s %s ../%s %s %s --multi'%(options.outDir, model, massPoint, options.inputFitFile,1000*lumi,options.config,box,".",signalDsName,backgroundDsName[box],xsecString,signalSys),options.dryRun)
#        exec_me('cp dijet_combine_%s_%s_lumi-%.3f_%s.* %s'%(model,massPoint,lumi,box,options.outDir),options.dryRun)
        if options.step=="all" or options.step=="generator":
            if (rDict[int(massPoint)]!=0):
                exec_me('cd %s && combine -M GenerateOnly dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s %s %s %s --saveToys %s --expectSignal %.3f -t %i'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,rRangeString,fixStringGen,freezeStringGen,toysOptions,rDict[int(massPoint)],options.toys),options.dryRun)
            else:
                exec_me('cd %s && combine -M GenerateOnly dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s %s %s %s --saveToys %s --expectSignal 1E-20 -t %i'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,rRangeString,fixStringGen,freezeStringGen,toysOptions,options.toys),options.dryRun)
        
        if options.step=="all" or options.step=="fit":
            exec_me('cd %s && combine -M FitDiagnostics --robustFit=1 --cminDefaultMinimizerStrategy 0 dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s --toysFile higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.GenerateOnly.mH120.123456.root -t %i %s %s %s --saveWorkspace'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.toys,rRangeString,fixStringFit,freezeStringFit),options.dryRun)
        
        
#        exec_me('python python/WriteDataCard.py -m %s --mass %s -i %s -l %f -c %s -b %s -d %s %s %s %s %s --multi'%(model, massPoint, options.inputFitFile,1000*lumi,options.config,box,".",signalDsName,backgroundDsName[box],xsecString,signalSys),options.dryRun)
#        exec_me('mv dijet_combine_%s_%s_lumi-%.3f_%s.* %s'%(model,massPoint,lumi,box,options.outDir),options.dryRun)
#        exec_me('cd %s && combine -M GenerateOnly dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s %s %s %s --toysFrequentist --saveToys --expectSignal %.3f -t %i'%(options.outDir,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,rRangeString,fixStringGen,freezeStringGen,rDict[int(massPoint)],options.toys),options.dryRun)
#        exec_me('cd %s && combine  -v1 -M MaxLikelihoodFit --robustFit=1  dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s --toysFile higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.GenerateOnly.mH120.123456.root -t %i %s %s %s --minimizerTolerance 1 --minimizerStrategy 2  --saveWorkspace'%(options.outDir ,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.toys,rRangeString,fixStringFit,freezeStringFit),options.dryRun)
#        exec_me('cd %s && combine  -v1 -M MaxLikelihoodFit dijet_combine_%s_%s_lumi-%.3f_%s.txt -n %s_%s_lumi-%.3f_r-%.3f_%s_%s_%s --toysFile higgsCombine%s_%s_lumi-%.3f_r-%.3f_%s_%s_%s.GenerateOnly.mH120.123456.root -t %i %s %s %s  --minimizerStrategy 0 --saveWorkspace'%(options.outDir ,model,massPoint,lumi,box,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,model,massPoint,lumi,rDict[int(massPoint)],box,options.genPdf,options.fitPdf,options.toys,rRangeString,fixStringFit,freezeStringFit),options.dryRun)
        exec_me('cd %s'%(pwd),options.dryRun)

#--robustFit=1

if __name__ == '__main__':
    parser = OptionParser()
    parser.noSignalSys=False
    parser.add_option('-c','--config',dest="config",type="string",default="config/dijet_bias.config",
                  help="Name of the config file to use")
    parser.add_option('-b','--box',dest="box", default="CaloTrijet2016",type="string",
                  help="box name")
    parser.add_option('-m','--model',dest="model", default="qq",type="string",
                  help="signal model name")
    parser.add_option('--mass',dest="mass", default='300',type="string",
                  help="mass of resonance")
    parser.add_option('-l','--lumi',dest="lumi", default="35.9",type="string",
                  help="lumi in fb^-1, e.g.: 12.910")
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")
    parser.add_option('--rMax',dest="rMax",default="10.0",type="string",
                  help="maximum r value (for better precision)")
    parser.add_option('-r',dest="r",default=1,type="float",
                  help="expect signal r value")
    parser.add_option('--rMin',dest="rMin",default="-10.0",type="string",
                  help="minimum r value (for better precision)")
    parser.add_option('--xsec',dest="xsec",default=10,type="float",
                  help="xsec for signal in pb (r = 1)")
    parser.add_option('-i','--input-fit-file',dest="inputFitFile", default="fits_trijet_2018/DijetFitResults_CaloTrijet2016.root",type="string",
                  help="input fit file")
    parser.add_option('-d','--dir',dest="outDir",default="./",type="string",
                  help="Output directory to store everything")
    parser.add_option('-t','--toys',dest="toys",default=1000,type="int",
                  help="number of toys")
    parser.add_option('--gen-pdf',dest="genPdf", default="fiveparam", choices=['modexp','fiveparam','atlas','atlas6','silvio4','silvio5','silvio6','nom3','alt3','nom4','alt4','nom5','alt5','nom6','alt6','nom7','alt7','polext7','pol8'],
                  help="pdf for generating")
    parser.add_option('--fit-pdf',dest="fitPdf", default="fiveparam", choices=['modexp','fiveparam','atlas','atlas6','silvio4','silvio5','silvio6','nom3','alt3','nom4','alt4','nom5','alt5','nom6','alt6','nom7','alt7','polext7','pol8'],
                  help="pdf for fitting")
    parser.add_option('--asymptotic-file',dest="asymptoticFile",default=None,type="string",
                  help="load asymptotic cross section results file")
    parser.add_option('--queue',dest="queue",default=None,type="string",
                  help="submit on a T3 queue")
    parser.add_option('--step',dest="step", default="all", choices=['all','generator','fit'],
                  help="which step to run: all, generator, or fit")
    parser.add_option("--no-signalSys", action="store_true", dest="noSignalSys")

    (options,args) = parser.parse_args()
    exec_me("mkdir -p %s"%options.outDir,options.dryRun)

    pdfIndexMap = {#'fourparam': 0,
                   'modexp': 0,
                   'fiveparam': 1,
                   'atlas': 2,
                   'atlas6': 3,
                   'silvio4': 4,
                   'silvio5': 5,
                   'silvio6': 6,
                   'nom3': 7,
                   'nom4': 8,
                   'nom5': 9,
                   'nom6': 10,
                   'nom7': 11,
                   'alt3': 12,
                   'alt4': 13,
                   'alt5': 14,
                   'alt6': 15,
                   'alt7': 16,
                   'polext7': 17,
                   'pol8': 18,
                   }

    box = options.box
    lumi = float(options.lumi)
    model = options.model

    backgroundDsName = {'CaloDijet2015':'inputs/data_CaloScoutingHT_Run2015D_BiasCorrected_CaloDijet2015.root',
                        #'CaloDijet2016':'inputs/data_CaloScoutingHT_Run2016BCD_NewBiasCorrectedFlat_Golden12910pb_CaloDijet2016.root',
                        'CaloDijet2016':'inputs/data_CaloScoutingHT_Run2016BCDEFG_BiasCorrected_Mjj300_Golden27637pb_CaloDijet2016.root',
                        'CaloTrijet2016':'inputs/full.root',
                        'PFDijet2016':'inputs/data_PFRECOHT_Run2016BCD_Golden12910pb_PFDijet2016.root',
                        'CaloDijet20152016':'inputs/data_CaloScoutingHT_Run2015D2016B_CaloDijet20152016.root'
                        }
    
    if options.queue:
        submit_jobs_uzh(options,args)
    else:
        main(options,args)
