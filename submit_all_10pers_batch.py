from optparse import OptionParser
import os

batchOut="/mnt/t3nfs01/data01/shome/dbrzhech/DijetScouting/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer_silvio/batch_output"
parser = OptionParser()
parser.add_option('-f','--function',dest="function",choices=["Alt","Nom"],
              help="functions: alt, nom")
parser.add_option('--mjj-binning',dest="mjjBinning",type="int",
              help="mjj binning", default=10)
parser.add_option('-i','--input',dest="inputFile",type="string",
              help="input file")
parser.add_option('-d','--data-tag',dest="dataTag",type="string",
              help="data tag")
parser.add_option('-o','--run-option',dest="runOption",type="string",
            help="data tag")
parser.add_option('-c','--count-cut',dest="countCut",type="string",
            help="data tag")
(options,args) = parser.parse_args()
#inputDataFile=options.inputFile

if not os.path.isdir(batchOut):
    os.system("mkdir %s"%batchOut)

isrPtCutArray=[]
for pt in range(40,91,2):
    isrPtCutArray.append(pt)
funcType="Nom"
parNumber=5
if options.runOption == "createBatch":
    for i,inputDataFile in enumerate(options.inputFile.split(",")):
        mjjBinning = 5
        minBinArr=[]
        for m in range(220,311,mjjBinning):
            minBinArr.append(m)
        configFolder="config/forChi2Th2fMjj%sGeV%s_%s_batch"%(mjjBinning,options.dataTag,i)
        outputFolder="chi2th2fAllFunctions%sGeVBinning%s_%s_batch"%(mjjBinning,options.dataTag,i)
        if not os.path.isdir(configFolder):
            os.system("mkdir %s"%configFolder)
        if not os.path.isdir(outputFolder):
            os.system("mkdir %s"%outputFolder)
        print "%s%s_mjjBinning%s"%(funcType,parNumber,mjjBinning)
        for isrPtCut in isrPtCutArray:
            for minBin in minBinArr:
                func="%s%s"%(funcType,parNumber)
                configFileName="config/dijet_isr_DijetFisher%s.config"%func
                logFile="%s/logs/log_%s_minBin%s_isrpt%s_mjjbinning%sGeV%s.log"%(batchOut,func.lower(),minBin,isrPtCut,mjjBinning,options.dataTag)
                outputFitDirectory="chi2_studies_deta1.1_%s/%s%s_mjjBinning%s_isrpt%s_minBin%s_%s_batch"%(options.dataTag,funcType,parNumber,mjjBinning,isrPtCut,minBin,i)
                if not os.path.isdir(outputFitDirectory.split("/")[0]):
                    os.system("mkdir %s"%outputFitDirectory.split("/")[0])
                if not os.path.isdir(outputFitDirectory):
                    os.system("mkdir %s"%outputFitDirectory)
                outputRootFile="%s/isrPt_%s_mjjBinning%s_isrpt%s_minBin%s_studies.root"%(outputFolder,func,mjjBinning,isrPtCut,minBin)
                outputLaTeXFile="%s/isrPt_%s_mjjBinning%s_isrpt%s_minBin%s_studies.tex"%(outputFolder,func,mjjBinning,isrPtCut,minBin)
                fout=open("batch_jobs/batch_mjjBinning%s_%s_%s_%s_%s_%s_%s.sh"%(mjjBinning,funcType,parNumber,isrPtCut,minBin,options.dataTag,i), "w+")
                fout.write("#!/bin/bash\n")
                fout.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
                fout.write("export SCRAM_ARCH=slc6_amd64_gcc530\n")
                fout.write("cd /mnt/t3nfs01/data01/shome/dbrzhech/DijetScouting/CMSSW_7_4_14/src/CMSDIJET/DijetRootTreeAnalyzer_silvio\n")
                fout.write("eval `scramv1 runtime -sh`\n")
                fout.write("python python/chisquareTable.py -c %s -l 1000 -b CaloTrijet2016 -d %s --fit-spectrum %s --chi2table-create True --root-out %s --latex-out %s --cut-type th3f --mjj-binning %s --mjj-low %s --mjj-high %s --isrpt-low %s --isrpt-high %s --config-create True --config-folder %s/ > %s"%(configFileName,outputFitDirectory,inputDataFile,outputRootFile,outputLaTeXFile,mjjBinning,minBin,minBin+1,isrPtCut,isrPtCut+1,configFolder,logFile))
#exit()
elif options.runOption == "submitBatch":
    count=0
    # print options.countCut.split(",")
    # exit()
    mincut,maxcut=options.countCut.split(",")
    for i,inputDataFile in enumerate(options.inputFile.split(",")):
        mjjBinning =5 
        minBinArr=[]
        for m in range(220,311,mjjBinning):
            minBinArr.append(m)
        for isrPtCut in isrPtCutArray:
            for minBin in minBinArr:
                # print count
                if count>=int(mincut) and count<int(maxcut):
                    os.system("qsub -q short.q batch_jobs/batch_mjjBinning%s_%s_%s_%s_%s_%s_%s.sh -o %s -e %s"%(mjjBinning,funcType,parNumber,isrPtCut,minBin,options.dataTag,i,batchOut,batchOut))
                count+=1

elif options.runOption == "catFiles":
    # print "In progress..."
    for i,inputDataFile in enumerate(options.inputFile.split(",")):
        mjjBinning = 5
        outputFolder="chi2th2fAllFunctions%sGeVBinning%s_%s_batch"%(mjjBinning,options.dataTag,i)
        os.system("hadd -f %s/isrPt_%s%s_mjjBinning%s_studies.root %s/isrPt_%s%s_mjjBinning%s_isrpt*_minBin*_studies.root"%(outputFolder,funcType,parNumber,mjjBinning,outputFolder,funcType,parNumber,mjjBinning))
