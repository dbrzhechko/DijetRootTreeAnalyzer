from optparse import OptionParser
import os
import BinnedFitMod
import ROOT
import re
#import th3fToth1f
signal_mjj_binning = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]

#cutBinning = [40,50,60,70,80,90]
def takeValues(keyType, array):
    out=[]
    if keyType == "trigger":
        out = range(0,len(array))
    else:
        out = array
    cutBins=options.cutBins
    return [out,cutBins]

def findLines(lines, findString, box):

    output = ""
    startIndex = lines.index("["+box+"]"+'\n')
    br_match = 0

    for line in lines[startIndex:]:
        if findString in line and '#' not in line[0:5]:
            br_match=line.count("[")
            br_match-=line.count("]")
            output = line
            break
        startIndex+=1

    if br_match is not 0:
        for line in lines[(startIndex+1):]:
            if '#' not in line[0:5]:
                br_match+=line.count("[")
                br_match-=line.count("]")
                output+=line
            # print br_match
            if br_match == 0:
                break
    return output

def signal_mjj_function(minBin, maxBin):
    signal_mjj = [minBin]
    signal_mjj_indecies = [i for i in range(len(signal_mjj_binning)) if signal_mjj_binning[i] > minBin and signal_mjj_binning[i] < maxBin]
    for i in signal_mjj_indecies:
        mjj = signal_mjj_binning[i]
        signal_mjj.append(mjj)
    # for mjj in signal_mjj_binning[signal_mjj_binning.index(minBin):signal_mjj_binning.index(maxBin)+1]:
    #     signal_mjj.append(mjj)
    signal_mjj.append(maxBin)
    return signal_mjj

def histoNamesIsrPtCut(isrPtCut):
#    isrPtCut = int(isrPtCut)
    print("isrPtCut = ",isrPtCut)
    output='['
    if int(isrPtCut) < 300:
        output += "'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_%s_%s'"%(int(isrPtCut), cutBinning[cutBinning.index(int(isrPtCut))+1])
        for isrBinLeftEdge in cutBinning[cutBinning.index(int(isrPtCut))+1:-1]:
            output += ", 'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_%s_%s'"%(isrBinLeftEdge, cutBinning[cutBinning.index(isrBinLeftEdge)+1])
        output += ", "
    output += "'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_300']"
    return output

def histoNamesIsrPtCutTh3f(isrPtCut):
#    isrPtCut = int(isrPtCut)
    print("isrPtCut = ",isrPtCut)
    output='['
    if int(isrPtCut) < 150:
        output += "'dijetMassHisto_isrptcut_%s'"%(int(isrPtCut))
        # output += "'dijetMassHisto_isrptcut_%s_%s'"%(int(isrPtCut), cutBinning[cutBinning.index(int(isrPtCut))+1])
    #     for isrBinLeftEdge in cutBinning[cutBinning.index(int(isrPtCut))+1:-1]:
    #         output += ", 'dijetMassHisto_isrptcut_%s_%s'"%(isrBinLeftEdge, cutBinning[cutBinning.index(isrBinLeftEdge)+1])
    #     output += ", "
    # output += "'dijetMassHisto_isrptcut_150']"
    output += "]"
    return output


def histoNameFunc(keyType, keyValue):
    if keyType == "isrPtCut":
        output = histoNamesIsrPtCut(keyValue)
    elif keyType == "trigger":
        output = trigger_histo_map[keyValue]
    elif keyType == "th3f":
        output = histoNamesIsrPtCutTh3f(keyValue)
    return output

def writeConfigFile(configFileTemplateName,box,inpuHistoNameDict,fitRanges,variables_range):
    output_string = {}
    keys = []
    keys.append('box')
    output_string['box'] = "["+box+"]" # '[CaloTrijet2016]'

    minDrawRange,minFitRange,maxFitRange=fitRanges
    mjjLowLeft,mjjLowRight,mjjBlindLeft,mjjBlindRight,mjjHighLeft,mjjHighRight = variables_range

    keys.append('variables')
    output_string['variables'] = "variables = ['mjj[%s.,%s.,%s.]','th1x[0,0,1000]']"%(minDrawRange,minFitRange,maxFitRange)

    keys.append('histoName')
    # output_string['histoName'] ='histoName = "dijetMassHisto_isrptcut_%s"'%(int(isrPtCut))
    histoNameOutput = histoNameFunc(inpuHistoNameDict["keyType"], inpuHistoNameDict["keyValue"])
    output_string['histoName'] ="histoName = %s"%(histoNameOutput)

    # output_string['histoName'] += "]"

    keys.append('variables_range')
    output_string['variables_range'] = "variables_range = ['mjj_Low[%s.,%s.]', 'mjj_Blind[%s.,%s.]', 'mjj_High[%s.,%s.]']"%(mjjLowLeft,mjjLowRight,mjjBlindLeft,mjjBlindRight,mjjHighLeft,mjjHighRight)

    configFileTemplate = open(configFileTemplateName,'r')
    lines = configFileTemplate.readlines()
    # print lines

    keys.append('combine_pdfs')
    output_string['combine_pdfs'] = findLines(lines, 'combine_pdfs', box)

    keys.append('combine_parameters')
    output_string['combine_parameters'] = findLines(lines, 'combine_parameters', box)
    # output_string['combine_parameters'] = "combine_parameters = [\n\'Ntot_bkg_CaloTrijet2016[3e+07]\',\n\'p0_CaloTrijet2016[1]\',\n"
    # parNames,parValue=regions(func,float(inpuHistoNameDict["keyValue"]),minDrawRange)
    # for i,par in enumerate(parNames):
    #     output_string['combine_parameters'] += "\'%s[%s]\',\n"%(par,parNames[i])
    # output_string['combine_parameters'] += "sqrts[13000]\',\n\'CaloTrijet2016_bkg_norm[1]\',\n\'meff_CaloTrijet2016[-1]\',\n\'seff_CaloTrijet2016[-1]\']"

    # if change_p2:
    #     output_string['combine_parameters'].find("p2_CaloTrijet2016[75]")#,"p2_CaloTrijet2016[85]")
    #     print True
    signal_mjj = signal_mjj_function(minDrawRange, maxFitRange)
    keys.append('signal_mjj')
    output_string['signal_mjj'] = "signal_mjj = "+str(signal_mjj)
    configText = ""
    for k in keys:
        configText += output_string[k] + "\n"
    # print "change_p2 = %s"%change_p2
    # if change_p2[0]:
    #     configText=configText.replace("p2_CaloTrijet2016[75]","p2_CaloTrijet2016[85]")
    #     configText=configText.replace("p2_CaloTrijet2016[70]","p2_CaloTrijet2016[55]")
    # if change_p2[1]:
    #     configText=configText.replace("p2_CaloTrijet2016[70]","p2_CaloTrijet2016[85]")
        # configText.find("p2_CaloTrijet2016[75]")#,"p2_CaloTrijet2016[85]")
    return configText

def createConfigFile(configPath, configFileName, text):
    configFile = open(configPath+configFileName,'w')
    configFile.write(text)
    print "Config file %s/%s was created!"%(configPath, configFileName)

def writeLaTeXTable(outputFileName, chiSquare_dict, xCutArray, minBinArr, maxBin):
    outFile = open(outputFileName,"w")
    output = "\\begin{table}[h]\n \\begin{tabular}{|l||"+"c|"*(len(minBinArr)+1)+"}\n"
    # output+="\\textbf{Fit range / isr pT cut}"
    output+="\\textbf{Trigger/ fit range}"
    for i,minBin in enumerate(minBinArr):
        # output+= " & $p_{T,ISR} > %s $"%(cut)
        output+=" & $%s < m_{jj} < %s$"%(minBin, maxBin)
    output+=" \\\\\n"
    output+="\\hline\n \\hline\n"
    print("chiSquare_dict:",chiSquare_dict)
    for j,cut in enumerate(xCutArray):
        output+= " \\verb|%s|"%(cut)
        for i,minBin in enumerate(minBinArr):
            output+=" & %4.2f"%(chiSquare_dict[str(cut)][int(minBin)])
        output+=" \\\\\n \\hline\n"

    output+= " \\end{tabular}"
    output+="\n\\end{table}"
    outFile.write(output)
    return output

def main(options,args):
    configFileTemplateName = options.config
    box = options.box
    isCreateConfigFile = options.isCreateConfigFile
    isCreateChi2Table = options.isCreateChi2Table
    isrPtCutArray=[]
    for pt in range(options.isrPtLow,options.isrPtHigh+1,options.cutBins):
        isrPtCutArray.append(pt)
#    isrPtCutArray   = [70]
    triggerArray = ["L1_HTT240", "L1_HTT240 && HT270", "L1_HTT240 && L1_HTT270", "L1_HTT240 && L1_HTT320", "L1_HTT_240..270_or", "L1_HTT_240..280_or", "L1_HTT_240..300_or", "L1_HTT_240..320_or"]
    minBinArr = [220, 244, 270, 290, 296, 325]
    # minBinArr=[]
    # for bin in range(options.mjjLow,options.mjjHigh+1,options.mjjBinning):
    #     minBinArr.append(bin)
    # minBinArr = [240,250,260,270,280,290,300,310]

    cutDict = {"trigger":  triggerArray,
               "isrPtCut": isrPtCutArray,
               "th3f": isrPtCutArray}
    keyType = options.cutType
    # isrPtCutArray   = [70.]
    # minBinArr = [296.]
    cutDictNumArray = takeValues(keyType,cutDict[keyType])[0]
    cutBins = takeValues(keyType,cutDict[keyType])[1]
    chiSquareHisto  = ROOT.TH2F("chi2_profile", "Chi2 profile", len(cutDict[keyType]), cutDictNumArray[0], cutDictNumArray[-1], len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    NtotHisto       = ROOT.TH2F("NtotHisto",    "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p0Histo         = ROOT.TH2F("p0Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p1Histo         = ROOT.TH2F("p1Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p2Histo         = ROOT.TH2F("p2Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p3Histo         = ROOT.TH2F("p3Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p4Histo         = ROOT.TH2F("p4Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p5Histo         = ROOT.TH2F("p5Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    p6Histo         = ROOT.TH2F("p6Histo",      "Chi2 profile", len(cutDict[keyType]), 0.5, len(cutDict)+0.5, len(minBinArr), minBinArr[0], signal_mjj_binning[signal_mjj_binning.index(minBinArr[-1])+1])
    #chiSquareHisto.GetYaxis().Set
    c1 = ROOT.TCanvas("chi2_profile","chi2/ndof", 0,0,2000,900)
    chiSquare_dict = {}
    # for i,isrPtCut in enumerate(isrPtCutArray):
    if keyType == "isrPtCut" or keyType == "th3f":
        chiSquareHisto.GetXaxis().SetTitle("ISR pT cut")
    elif keyType == "trigger":
        chiSquareHisto.GetXaxis().SetTitle("Trigger")
    chiSquareHisto.GetYaxis().SetTitle("Fit Range")
    for i,keyValue in enumerate(cutDict[keyType]):
        # chiSquare_dict[int(isrPtCut)] = {}
        if keyType == "isrPtCut" or keyType == "th3f":
            keyValue = str(int(keyValue))
            chiSquareHisto.GetXaxis().SetBinLabel(i+1, "p_{T,ISR} > " + keyValue)
            NtotHisto.GetYaxis().SetBinLabel(i+1,      "p_{T,ISR} > " + keyValue)
            p0Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p1Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p2Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p3Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p4Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p5Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            p6Histo.GetXaxis().SetBinLabel(i+1,        "p_{T,ISR} > " + keyValue)
            #if keyType == "th3f":
                #print "args = %s"%args[0]
                #th3fToth1f.th3ftoth1fWrite(options.th3fFile, args[0], int(keyValue), -1, 0, 1.1)
        elif keyType == "trigger":
            chiSquareHisto.GetXaxis().SetBinLabel(i+1, keyValue)

        chiSquare_dict[keyValue] = {}

        for j,minBin in enumerate(minBinArr):
            # isrPtCut = isrPtCut
            fitRanges = minBin,minBin,1000.
            variables_range = minBin,1000,minBin,1000,minBin,1000
            configText = writeConfigFile(configFileTemplateName,box,{"keyType": keyType, "keyValue": keyValue},fitRanges,variables_range)
            # print configText
            # exit()
            configPath = '%s/%s/'%(os.getcwd(),options.configFolder)
            configFileName = "%s_isrpt_%s_minBin_%s.config"%(re.split("\.|/",options.config)[1], keyValue.replace(' ', '_').replace('&&','and'),int(minBin))
            if isCreateConfigFile:
                createConfigFile(configPath, configFileName, configText)
            if isCreateChi2Table:
                print("BinnedFitMod.BinnedFitMod(%s, %s, %s, %s, %s)"%(str(options),str(args),str(configPath+configFileName),str(keyValue.replace(' ', '_').replace('&&','and')),str(int(minBin))))
                chiSquare = BinnedFitMod.BinnedFitMod(options, args, configPath+configFileName, keyValue.replace(' ', '_').replace('&&','and'), str(int(minBin)))[0]
                parDict = BinnedFitMod.BinnedFitMod(options, args, configPath+configFileName, keyValue.replace(' ', '_').replace('&&','and'), str(int(minBin)))[1]
                print("chiSquare = %s"%chiSquare)
                chiSquare_dict[keyValue][int(minBin)] = chiSquare
                chiSquareHisto.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                chiSquareHisto.SetBinContent(i+1,j+1,chiSquare)
                NtotHisto.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                NtotHisto.SetBinContent(i+1,j+1,parDict["Ntot_bkg_CaloTrijet2016"])
                p0Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p0Histo.SetBinContent(i+1,j+1,parDict["p0_CaloTrijet2016"])
                p1Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p1Histo.SetBinContent(i+1,j+1,parDict["p1_CaloTrijet2016"])
                p2Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p2Histo.SetBinContent(i+1,j+1,parDict["p2_CaloTrijet2016"])
                p3Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p3Histo.SetBinContent(i+1,j+1,parDict["p3_CaloTrijet2016"])
                p4Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p4Histo.SetBinContent(i+1,j+1,parDict["p4_CaloTrijet2016"])
                p5Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p5Histo.SetBinContent(i+1,j+1,parDict["p5_CaloTrijet2016"])
                p6Histo.GetYaxis().SetBinLabel(j+1, str(int(minBin)) + " < m_{jj} < " + str(int(fitRanges[2])))
                p6Histo.SetBinContent(i+1,j+1,parDict["p6_CaloTrijet2016"])

    if isCreateChi2Table:
        #latexText = writeLaTeXTable("chi2_table_blind_deta1.3.tex", chiSquare_dict, isrPtCutArray, minBinArr, 1000)
        latexText = writeLaTeXTable(options.latexOut, chiSquare_dict, cutDict[keyType], minBinArr, 1000)
    # print latexText
    # exit()
    if isCreateChi2Table:
        #outputFile = ROOT.TFile.Open("chi2_profile_blind_deta1.3.root","RECREATE")
        outputFile = ROOT.TFile.Open(options.rootOut,"RECREATE")
        chiSquareHisto.SetMaximum(10)
        chiSquareHisto.Draw("COLZ TEXT")
        chiSquareHisto.Write()
        NtotHisto.Draw("COLZ TEXT")
        NtotHisto.Write()
        p0Histo.Draw("COLZ TEXT")
        p0Histo.Write()
        p1Histo.Draw("COLZ TEXT")
        p1Histo.Write()
        p2Histo.Draw("COLZ TEXT")
        p2Histo.Write()
        p3Histo.Draw("COLZ TEXT")
        p3Histo.Write()
        p4Histo.Draw("COLZ TEXT")
        p4Histo.Write()
        p5Histo.Draw("COLZ TEXT")
        p5Histo.Write()
        p6Histo.Draw("COLZ TEXT")
        p6Histo.Write()
    # c1.Write()
    # print chiSquare_dict
    # raw_input("Press enter...")



if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default="config/run2.config",
                  help="Name of the config file to use")
    parser.add_option('','--cut-type',dest="cutType",type="string",default="isrPtCut",
                  help="Cut variable for x-axis")
    parser.add_option('','--latex-out',dest="latexOut",type="string",default="output_chi2.tex",
                  help="Name of the output file with chi square table")
    parser.add_option('','--root-out',dest="rootOut",type="string",default="output_chi2.root",
                  help="Name of the output root file with chi square histogram")
    parser.add_option('','--config-create',dest="isCreateConfigFile",type="string",
                  help="Create config file")
    parser.add_option('','--chi2table-create',dest="isCreateChi2Table",type="string",
                  help="Create chi2 table results")
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
    parser.add_option('--th3f-inputfile',dest="th3fFile",type="string",
                  help="TH3F input file")
    parser.add_option('--mjj-low',dest="mjjLow",type="int",
                  help="mjj minimal lower bound",default=220)
    parser.add_option('--mjj-high',dest="mjjHigh",type="int",
                  help="mjj maximal lower bound",default=320)
    parser.add_option('--mjj-binning',dest="mjjBinning",type="int",
                  help="mjj binning", default=10)
    parser.add_option('--isrpt-low',dest="isrPtLow",type="int",
                  help="isr Pt minimal lower bound",default=40)
    parser.add_option('--isrpt-high',dest="isrPtHigh",type="int",
                  help="isr Pt maximal lower bound",default=90)
    parser.add_option('--isrpt-binning',dest="cutBins",type="int",
                  help="isr Pt binning",default=2)
    parser.add_option('--config-folder',dest="configFolder",type="string",
                  help="folder to store config files",default="")
    (options,args) = parser.parse_args()

    cutBinning = [40,50,60,70,80,90,100,150,200,300]
    # cutBinning=[]
    # for i in range (40,151,1):
    #     cutBinning.append(i)

    # signal_mjj_binning=[]
    # for mjj in range(100,1201,options.mjjBinning):
    #     signal_mjj_binning.append(mjj)
    trigger_histo_map = {
        "L1_HTT240": "'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_70'",
        "L1_HTT240 && HT270": "'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_70_HT_270'",
        "L1_HTT240 && L1_HTT270": "'DijetFilter/dijetMassHisto/dijetMassHisto_isrptcut_70_L1_HTT240_L1_HTT270'",
        "L1_HTT240 && L1_HTT320":"'DijetFilter/dijetMassHisto/dijetMassHisto_70_L1_HTT240_L1_HTT320'",
        "L1_HTT_240..270_or":"'DijetFilter/dijetMassHisto/dijetMassHisto_L1_HTT_240_270_or'",
        "L1_HTT_240..280_or":"'DijetFilter/dijetMassHisto/dijetMassHisto_L1_HTT_240_270_280_or'",
        "L1_HTT_240..300_or":"'DijetFilter/dijetMassHisto/dijetMassHisto_L1_HTT_240_270_280_300_or'",
        "L1_HTT_240..320_or":"'DijetFilter/dijetMassHisto/dijetMassHisto_L1_HTT_240_270_280_300_320_or'",
    }

    main(options,args)
