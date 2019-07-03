#! /usr/bin/env python
import ROOT as rt
import os.path
import sys, glob, re
from array import *
from optparse import OptionParser
from inputAcceptance import acc_dict


q_qsim_withDM = 0.25
def g_qsim(Mres):
    C_M = 0
    for mq in [2.2E-3, 4.7E-3, 95E-3, 1.275, 4.18, 173.0]:
        if Mres>2*mq:
            C_M += (1 - 4*(mq/Mres)**2 )**0.5 * (1 + 2*(mq/Mres)**2 )
    g_qsim = q_qsim_withDM * (1./(1.+1./(3*C_M*q_qsim_withDM**2)))**0.5
    return g_qsim


#acceptance from 300 to 1000 GeV with 50 GeV step
# def acceptance_func(matching):
#     acceptance_arr={
#                    "jets01":[0.09986057132482529, 0.12167418003082275, 0.14348779618740082, 0.16123375296592712, 0.17897969484329224, 0.19408614933490753, 0.20919260382652283, 0.22077441215515137, 0.2323562204837799, 0.24393802881240845, 0.255519837141037, 0.26391077041625977, 0.27230167388916016, 0.28069260716438293, 0.2890835404396057],
#                    "jets02": [0.08887774497270584, 0.10269524157047272, 0.11651274561882019, 0.12764838337898254, 0.1387840211391449, 0.14709563553333282, 0.15540724992752075, 0.16193723678588867, 0.1684672236442566, 0.1749972254037857, 0.18152721226215363, 0.18580299615859985, 0.1900787651538849, 0.19435453414916992, 0.19863031804561615],
#                    "jets12":[0.07388336956501007, 0.08556313812732697, 0.09724291414022446, 0.10732652992010117, 0.11741014569997787, 0.12459999322891235, 0.13178983330726624, 0.1376211792230606, 0.14345252513885498, 0.14928387105464935, 0.15511521697044373, 0.1591583788394928, 0.16320154070854187, 0.16724470257759094, 0.17128786444664001]}
#                    "jets01":[0.05082365870475769, 0.05800797417759895, 0.06519228965044022, 0.07220619916915894, 0.07922010123729706, 0.08558467030525208, 0.0919492319226265, 0.09663685411214828, 0.10132447630167007, 0.10601209849119186, 0.11069972068071365, 0.11389292031526566, 0.11708611249923706, 0.12027931213378906, 0.12347251176834106],
#                    "jets02": [0.04628361761569977, 0.05583023279905319, 0.06537684798240662, 0.07513462007045746, 0.0848923921585083, 0.09355735778808594, 0.10222231596708298, 0.10948159545660019, 0.1167408674955368, 0.12400014698505402, 0.13125942647457123, 0.13676966726779938, 0.14227992296218872, 0.14779016375541687, 0.15330040454864502],
#                    "jets12":[0.04330157861113548, 0.05111993849277496, 0.058938298374414444, 0.06681650876998901, 0.07469471544027328, 0.08232658356428146, 0.08995845168828964, 0.09613728523254395, 0.10231612622737885, 0.10849495977163315, 0.11467379331588745, 0.11936256289482117, 0.12405133992433548, 0.1287401169538498, 0.1334288865327835]}

#                    "jets01":[0.07915464043617249, 0.10350766032934189, 0.1278606802225113, 0.14949233829975128, 0.17112399637699127, 0.1860898733139038, 0.20105573534965515, 0.20988702774047852, 0.21871832013130188, 0.22754961252212524, 0.2363809049129486, 0.21971969306468964, 0.20305848121643066, 0.18639728426933289, 0.1697360724210739],
#                    "jets02":[0.0477960966527462, 0.06157104671001434, 0.07534599304199219, 0.09082856774330139, 0.1063111424446106, 0.11975476890802383, 0.13319839537143707, 0.14259710907936096, 0.15199583768844604, 0.16139455139636993, 0.17079326510429382, 0.17365822196006775, 0.17652316391468048, 0.1793881058692932, 0.18225306272506714],
#                    "jets12":[0.017758427187800407, 0.023944348096847534, 0.03013027086853981, 0.03781476244330406, 0.045499254018068314, 0.05433296412229538, 0.06316667795181274, 0.07405373454093933, 0.08494079113006592, 0.09582784026861191, 0.1067148968577385, 0.11593275517225266, 0.12515060603618622, 0.13436846435070038, 0.14358632266521454]}

#                    "jets01":[0.10564551502466202, 0.1401125192642212, 0.17457953095436096, 0.20535123348236084, 0.23612292110919952, 0.2581591010093689, 0.28019529581069946, 0.2923034131526947, 0.30441153049468994, 0.3165196180343628, 0.32862773537635803, 0.3121080696582794, 0.2955883741378784, 0.2790687084197998, 0.2625490427017212],
#                    "jets02":[0.061017073690891266, 0.08204822242259979, 0.10307937860488892, 0.13073471188545227, 0.15839004516601562, 0.18517938256263733, 0.21196870505809784, 0.23502488434314728, 0.2580810487270355, 0.28113722801208496, 0.3041934072971344, 0.31888043880462646, 0.33356744050979614, 0.3482544720172882, 0.3629415035247803],
#                    "jets12":[0.021207377314567566, 0.02998185344040394, 0.03875632956624031, 0.05044207349419594, 0.062127817422151566, 0.07637734711170197, 0.09062688052654266, 0.110112264752388, 0.12959764897823334, 0.14908303320407867, 0.168568417429924, 0.18704909086227417, 0.20552974939346313, 0.2240104079246521, 0.24249108135700226]}

##### CORRECT USING #####
# selection    = "isr_pt > 70 && jet2_pt>70 && jet1_pt>70 && abs(jet1_eta)<2.5 && abs(jet2_eta)<2.5 && abs(isr_eta)<2.5 && abs(dijet_deta) < 1.1 && dijet_mass > 296 && dijet_mass < 1000"
# preselection = "abs(jet1MC_eta)<2.5 && abs(jet2MC_eta)<2.5 && abs(dijetMC_deta) < 1.1"
    #
    #                 "jets01":[0.08613815158605576, 0.12388591468334198, 0.1616336703300476, 0.1943456530570984, 0.22705763578414917, 0.25112384557724, 0.2751900851726532, 0.2879217267036438, 0.3006533682346344, 0.313385009765625, 0.3261166512966156, 0.3097951114177704, 0.29347360134124756, 0.27715206146240234, 0.26083052158355713],
    #                 "jets02":[0.04338094964623451, 0.06488171219825745, 0.08638247102499008, 0.10870857536792755, 0.13103467226028442, 0.15795621275901794, 0.18487773835659027, 0.20962266623973846, 0.23436760902404785, 0.25911253690719604, 0.28385746479034424, 0.30010485649108887, 0.3163522481918335, 0.3325996696949005, 0.34884706139564514],
    #                 "jets12":[0.013208746910095215, 0.02198096737265587, 0.03075318969786167, 0.03928264603018761, 0.04781210049986839, 0.0598108172416687, 0.07180953025817871, 0.08896364271640778, 0.10611775517463684, 0.1232718676328659, 0.14042598009109497, 0.15801012516021729, 0.1755942702293396, 0.19317841529846191, 0.21076256036758423]}
    # acc_dict = {}
    # i = 0
    # if matching == "jetsij":
    #     for m in range(300,1001,50):
    #         acc_dict[m]=(acceptance_arr["jets01"][i]+acceptance_arr["jets02"][i]+acceptance_arr["jets12"][i])/3.
    #         i+=1
    # elif matching:
    #     for m in range(300,1001,50):
    #         acc_dict[m]=acceptance_arr[matching][i]
    #         i+=1
    # else:
    #     for m in range(300,1001,50):
    #         acc_dict[m]=0
    #
    # return acc_dict

# table_xsec = {300: 230.825913,
#               350: 142.662564,
#               400: 99.2772,
#               450: 71.095808,
#               500: 50.43832,
#               550: 35.570286,
#               600: 26.435848,
#               650: 19.6472704,
#               700: 15.38133,
#               750: 11.8963518,
#               800: 9.2019888,
#               850: 7.394698,
#               900: 5.8131824,
#               950: 4.7036696,
#               1000: 3.759,}

# matching = "jets12"

def getThyXsecDict():
    thyXsecDict = {}
    xsecFiles = ['data/dm_xsec_interp.txt']
#    xsecFiles = ['data/all_lowmass_lhc13TeV.txt','data/rsg_gg_lhc13TeV.txt','data/S8_13TeV_narrow.txt','data/string_total_13TeV.txt','data/axi_lhc13TeV_NLO.txt','data/dm_xsec.txt','data/Zprimebb_xsec.txt','data/dmbb_xsec.txt']
    print xsecFiles
    for xsecFile in xsecFiles:
        moreThyModels = []
        f = open(xsecFile)
        for i,line in enumerate(f.readlines()):
            if line[0]=='#': continue
            line = line.replace('\n','')
            line = line.replace('\t','')
            line = line.replace('\r','')
            lineList = [l for l in line.split(" ") if l!='']

            if lineList[0]=='Mass':
                for l in lineList:
                    if l=='Mass': continue
                    thyXsecDict[l] = {}
                    moreThyModels.append(l)
            else:
                for j, thyModel in enumerate(moreThyModels):
                    thyXsecDict[thyModel][int(float(lineList[0]))] = float(lineList[j+1])
        f.close()

#        thyXsecDict['AxigluonkNLO'] = {}
#    for (mass,thyXsec) in thyXsecDict['Axigluon'].iteritems():
#        thyXsecDict['AxigluonkNLO'][mass] = 1.08 * thyXsec
    print(thyXsecDict)
    for (mass,thyXsec) in thyXsecDict['DM1GeV'].iteritems():
         thyXsecDict['DM1GeV'][mass] = (5./6.) * thyXsec
         thyXsecDict['DM1GeV'][mass] = thyXsec
#    for (mass,thyXsec) in thyXsecDict['DMbb1GeV'].iteritems():
#        thyXsecDict['DMbb1GeV'][mass] = (5./6.) * thyXsec
    return thyXsecDict


def file_key(filename):
    massPoint = re.findall("[0-9]+.000000",filename)
    gluinoMass    = massPoint[0]
    LSPMass  = massPoint[1]
    return float(gluinoMass)

def getHybridCLsArrays(directory, model, Box, bayes):
    if bayes:
        tfile = rt.TFile.Open("%s/xsecUL_MarkovChainMC_%s_%s.root"%(directory,model,Box))
    else:
        tfile = rt.TFile.Open("%s/xsecUL_Asymptotic_%s_%s.root"%(directory,model,Box))
    xsecTree = tfile.Get("xsecTree")
    gluinoMassArray = array('d')
    gluinoMassArray_er = array('d')
    observedLimit = array('d')
    observedLimit_er = array('d')
    expectedLimit = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_plus2sigma = array('d')

    xsecTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = -1
    table_xsec = getThyXsecDict()
    acceptance = 1
    xsec_table = 1

    # for key in sorted(acc_dict.iterkeys()):
    #     print "%s: %s" % (key, acc_dict[key])
    while True:
        entry = elist.Next()
        if entry == -1: break
        xsecTree.GetEntry(entry)

        gluinoMassArray.append(xsecTree.mass)
        gluinoMassArray_er.append(0.0)

        exec 'xsecULObs = xsecTree.xsecULObs_%s'%Box
        exec 'xsecULExp = xsecTree.xsecULExp_%s'%Box
        exec 'xsecULExpPlus = xsecTree.xsecULExpPlus_%s'%Box
        exec 'xsecULExpMinus = xsecTree.xsecULExpMinus_%s'%Box
        exec 'xsecULExpPlus2 = xsecTree.xsecULExpPlus2_%s'%Box
        exec 'xsecULExpMinus2 = xsecTree.xsecULExpMinus2_%s'%Box


        xsecULObs = xsecULObs
        xsecULExp = xsecULExp
        if options.noData: xsecULObs = 0

        if isCouplingLimit:
            acceptance = acc_dict[matching][int(xsecTree.mass)]
        xsec_table = table_xsec['DM1GeV'][int(xsecTree.mass)]

        if isCouplingLimit:
            gqULObs = rt.TMath.Sqrt(xsecULObs/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            observedLimit.append(gqULObs)
        else:
            observedLimit.append(xsecULObs)#*crossSections[i])

        observedLimit_er.append(0.0)#*crossSections[i])

        if isCouplingLimit:
            gqULExp = rt.TMath.Sqrt(xsecULExp/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            expectedLimit.append(gqULExp)
        else:
            expectedLimit.append(xsecULExp)#*crossSections[i])

        print("%s\tMass %s\tLimit %s\tAcceptance %s\tXsect %s"%(matching, int(xsecTree.mass), xsecULExp, acceptance, xsec_table))

        xsecULExpPlus = max(xsecULExpPlus,xsecULExp)
        xsecULExpMinus = min(xsecULExpMinus,xsecULExp)
        xsecULExpPlus2 = max(xsecULExpPlus2,xsecULExpPlus)
        xsecULExpMinus2 = min(xsecULExpMinus2,xsecULExpMinus)

        if isCouplingLimit:
            gqULExpPlus = rt.TMath.Sqrt(max(xsecULExpPlus,xsecULExp)/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            gqULExpMinus = rt.TMath.Sqrt(min(xsecULExpMinus,xsecULExp)/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            gqULExpPlus2 = rt.TMath.Sqrt(max(xsecULExpPlus2,xsecULExpPlus)/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            gqULExpMinus2 = rt.TMath.Sqrt(min(xsecULExpMinus2,xsecULExpMinus)/acceptance/xsec_table)*g_qsim(int(xsecTree.mass))
            expectedLimit_minus1sigma.append(gqULExp - gqULExpMinus)
            expectedLimit_plus1sigma.append(gqULExpPlus - gqULExp)
            expectedLimit_minus2sigma.append(gqULExp - gqULExpMinus2)
            expectedLimit_plus2sigma.append(gqULExpPlus2 - gqULExp)
        else:
            expectedLimit_minus1sigma.append(xsecULExp - xsecULExpMinus)#*crossSections[i])
            expectedLimit_plus1sigma.append(xsecULExpPlus - xsecULExp)#*crossSections[i])
            expectedLimit_minus2sigma.append(xsecULExp - xsecULExpMinus2)#*crossSections[i])
            expectedLimit_plus2sigma.append(xsecULExpPlus2 - xsecULExp)#*crossSections[i])

    #return gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma

    # sort arrays first by gluino mass (in case tree entries are out of order)
    allTuples = zip(*sorted(zip(gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma)))
    allArrays = []
    for t in allTuples:
        allArrays.append(array('d',t))
    return tuple(allArrays)

def getHybridCLsArraysRSG(directory, Box):

    tfileqq = rt.TFile.Open("%s/qq/xsecUL_Asymptotic_qq_%s.root"%(directory,Box))
    tfilegg = rt.TFile.Open("%s/gg/xsecUL_Asymptotic_gg_%s.root"%(directory,Box))
    xsecTreeqq = tfileqq.Get("xsecTree")
    xsecTreegg = tfilegg.Get("xsecTree")

    dict_RSG_BR_qq = {}
    dict_RSG_BR_gg = {}
    rsg_br_file = open("data/rsg_lhc13TeV.out")
    for line in rsg_br_file:
      if not line.startswith("#"):
        massRSG = float(line.split()[0])
        RSG_BR_qqbar = float(line.split()[2]) + float(line.split()[4])
        RSG_BR_gg = float(line.split()[3]) + float(line.split()[5])
        dict_RSG_BR_qq[massRSG] = RSG_BR_qqbar
        dict_RSG_BR_gg[massRSG] = RSG_BR_gg

    gluinoMassArray = array('d')
    gluinoMassArray_er = array('d')
    observedLimit_qq = array('d')
    observedLimit_er_qq = array('d')
    expectedLimit_qq = array('d')
    expectedLimit_minus1sigma_qq = array('d')
    expectedLimit_plus1sigma_qq = array('d')
    expectedLimit_minus2sigma_qq = array('d')
    expectedLimit_plus2sigma_qq = array('d')
    observedLimit_gg = array('d')
    observedLimit_er_gg = array('d')
    expectedLimit_gg = array('d')
    expectedLimit_minus1sigma_gg = array('d')
    expectedLimit_plus1sigma_gg = array('d')
    expectedLimit_minus2sigma_gg = array('d')
    expectedLimit_plus2sigma_gg = array('d')
    observedLimit = array('d')
    observedLimit_er = array('d')
    expectedLimit = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_plus2sigma = array('d')


    xsecTreeqq.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = -1
    while True:
        entry = elist.Next()
        if entry == -1: break
        xsecTreeqq.GetEntry(entry)

	mass = xsecTreeqq.mass
        gluinoMassArray.append(xsecTreeqq.mass)
        gluinoMassArray_er.append(0.0)

        exec 'xsecULObs_qq = xsecTreeqq.xsecULObs_%s'%Box
        exec 'xsecULExp_qq = xsecTreeqq.xsecULExp_%s'%Box
        exec 'xsecULExpPlus_qq = xsecTreeqq.xsecULExpPlus_%s'%Box
        exec 'xsecULExpMinus_qq = xsecTreeqq.xsecULExpMinus_%s'%Box
        exec 'xsecULExpPlus2_qq = xsecTreeqq.xsecULExpPlus2_%s'%Box
        exec 'xsecULExpMinus2_qq = xsecTreeqq.xsecULExpMinus2_%s'%Box

	xsecTreegg.GetEntry(entry)
        exec 'xsecULObs_gg = xsecTreegg.xsecULObs_%s'%Box
        exec 'xsecULExp_gg = xsecTreegg.xsecULExp_%s'%Box
        exec 'xsecULExpPlus_gg = xsecTreegg.xsecULExpPlus_%s'%Box
        exec 'xsecULExpMinus_gg = xsecTreegg.xsecULExpMinus_%s'%Box
        exec 'xsecULExpPlus2_gg = xsecTreegg.xsecULExpPlus2_%s'%Box
        exec 'xsecULExpMinus2_gg = xsecTreegg.xsecULExpMinus2_%s'%Box



        xsecULObs_qq = xsecULObs_qq
        xsecULExp_qq = xsecULExp_qq
        observedLimit_qq.append(xsecULObs_qq)#*crossSections[i])
        observedLimit_er_qq.append(0.0)#*crossSections[i])
        expectedLimit_qq.append(xsecULExp_qq)#*crossSections[i])

        xsecULObs_gg = xsecULObs_gg
        xsecULExp_gg = xsecULExp_gg
        observedLimit_gg.append(xsecULObs_gg)#*crossSections[i])
        observedLimit_er_gg.append(0.0)#*crossSections[i])
        expectedLimit_gg.append(xsecULExp_gg)#*crossSections[i])

        xsecULObs = xsecULObs_qq*dict_RSG_BR_qq[mass] + xsecULObs_gg*dict_RSG_BR_gg[mass]
        xsecULExp = xsecULExp_qq*dict_RSG_BR_qq[mass] + xsecULExp_gg*dict_RSG_BR_gg[mass]
        observedLimit.append(xsecULObs)#*crossSections[i])
        observedLimit_er.append(0.0)#*crossSections[i])
        expectedLimit.append(xsecULExp)#*crossSections[i])

        xsecULExpPlus_qq = max(xsecULExpPlus_qq,xsecULExp_qq)
        xsecULExpMinus_qq = min(xsecULExpMinus_qq,xsecULExp_qq)
        xsecULExpPlus2_qq = max(xsecULExpPlus2_qq,xsecULExpPlus_qq)
        xsecULExpMinus2_qq = min(xsecULExpMinus2_qq,xsecULExpMinus_qq)
        xsecULExpPlus_gg = max(xsecULExpPlus_gg,xsecULExp_gg)
        xsecULExpMinus_gg = min(xsecULExpMinus_gg,xsecULExp_gg)
        xsecULExpPlus2_gg = max(xsecULExpPlus2_gg,xsecULExpPlus_gg)
        xsecULExpMinus2_gg = min(xsecULExpMinus2_gg,xsecULExpMinus_gg)
        xsecULExpPlus = xsecULExpPlus_qq*dict_RSG_BR_qq[mass] + xsecULExpPlus_gg*dict_RSG_BR_gg[mass]
        xsecULExpMinus = xsecULExpMinus_qq*dict_RSG_BR_qq[mass] + xsecULExpMinus_gg*dict_RSG_BR_gg[mass]
        xsecULExpPlus2 = xsecULExpPlus2_qq*dict_RSG_BR_qq[mass] + xsecULExpPlus2_gg*dict_RSG_BR_gg[mass]
        xsecULExpMinus2 = xsecULExpMinus2_qq*dict_RSG_BR_qq[mass] +xsecULExpMinus2_gg*dict_RSG_BR_gg[mass]

        expectedLimit_minus1sigma.append(xsecULExp - xsecULExpMinus)#*crossSections[i])
        expectedLimit_plus1sigma.append(xsecULExpPlus - xsecULExp)#*crossSections[i])
        expectedLimit_minus2sigma.append(xsecULExp - xsecULExpMinus2)#*crossSections[i])
        expectedLimit_plus2sigma.append(xsecULExpPlus2 - xsecULExp)#*crossSections[i])


    return gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma


def getSignificanceArrays(directory, model, Box):
    tfile = rt.TFile.Open("%s/xsecUL_ProfileLikelihood_%s_%s.root"%(directory,model,Box))
    xsecTree = tfile.Get("xsecTree")

    gluinoMassArray = array('d')
    gluinoMassArray_er = array('d')
    observedLimit = array('d')
    observedLimit_er = array('d')
    expectedLimit = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_plus2sigma = array('d')


    xsecTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = -1
    while True:
        entry = elist.Next()
        if entry == -1: break
        xsecTree.GetEntry(entry)

        gluinoMassArray.append(xsecTree.mass)
        gluinoMassArray_er.append(0.0)

        exec 'xsecULObs = xsecTree.xsecULObs_%s'%Box
        exec 'xsecULExp = xsecTree.xsecULExp_%s'%Box
        exec 'xsecULExpPlus = xsecTree.xsecULExpPlus_%s'%Box
        exec 'xsecULExpMinus = xsecTree.xsecULExpMinus_%s'%Box
        exec 'xsecULExpPlus2 = xsecTree.xsecULExpPlus2_%s'%Box
        exec 'xsecULExpMinus2 = xsecTree.xsecULExpMinus2_%s'%Box



        xsecULObs = xsecULObs
        xsecULExp = xsecULExp
        observedLimit.append(xsecULObs)#*crossSections[i])
        observedLimit_er.append(0.0)#*crossSections[i])

        expectedLimit.append(xsecULExp)#*crossSections[i])



        xsecULExpPlus = max(xsecULExpPlus,xsecULExp)
        xsecULExpMinus = min(xsecULExpMinus,xsecULExp)
        xsecULExpPlus2 = max(xsecULExpPlus2,xsecULExpPlus)
        xsecULExpMinus2 = min(xsecULExpMinus2,xsecULExpMinus)

        expectedLimit_minus1sigma.append(xsecULExp - xsecULExpMinus)#*crossSections[i])
        expectedLimit_plus1sigma.append(xsecULExpPlus - xsecULExp)#*crossSections[i])
        expectedLimit_minus2sigma.append(xsecULExp - xsecULExpMinus2)#*crossSections[i])
        expectedLimit_plus2sigma.append(xsecULExpPlus2 - xsecULExp)#*crossSections[i])


    #return gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma
    # sort arrays first by gluino mass (in case tree entries are out of order)
    allTuples = zip(*sorted(zip(gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma)))
    allArrays = []
    for t in allTuples:
        allArrays.append(array('d',t))
    return tuple(allArrays)

def setstyle():
    # For the canvas:
    rt.gStyle.SetCanvasBorderMode(0)
    rt.gStyle.SetCanvasColor(rt.kWhite)
    rt.gStyle.SetCanvasDefH(400) #Height of canvas
    rt.gStyle.SetCanvasDefW(600) #Width of canvas
    rt.gStyle.SetCanvasDefX(0)   #POsition on screen
    rt.gStyle.SetCanvasDefY(0)

    # For the Pad:
    rt.gStyle.SetPadBorderMode(0)
    # rt.gStyle.SetPadBorderSize(Width_t size = 1)
    rt.gStyle.SetPadColor(rt.kWhite)
    rt.gStyle.SetPadGridX(False)
    rt.gStyle.SetPadGridY(False)
    rt.gStyle.SetGridColor(0)
    rt.gStyle.SetGridStyle(3)
    rt.gStyle.SetGridWidth(1)

    # For the frame:
    rt.gStyle.SetFrameBorderMode(0)
    rt.gStyle.SetFrameBorderSize(1)
    rt.gStyle.SetFrameFillColor(0)
    rt.gStyle.SetFrameFillStyle(0)
    rt.gStyle.SetFrameLineColor(1)
    rt.gStyle.SetFrameLineStyle(1)
    rt.gStyle.SetFrameLineWidth(1)

    # set the paper & margin sizes
    rt.gStyle.SetPaperSize(20,26)
    rt.gStyle.SetPadTopMargin(0.09)
    rt.gStyle.SetPadRightMargin(0.065)
    rt.gStyle.SetPadBottomMargin(0.15)
    rt.gStyle.SetPadLeftMargin(0.17)

    # use large Times-Roman fonts
    rt.gStyle.SetTitleFont(42,"xyz")  # set the all 3 axes title font
    rt.gStyle.SetTitleFont(42," ")    # set the pad title font
    rt.gStyle.SetTitleSize(0.06,"xyz") # set the 3 axes title size
    rt.gStyle.SetTitleSize(0.06," ")   # set the pad title size
    rt.gStyle.SetTitleSize(0.052,"y")   # set the pad title size
    rt.gStyle.SetTitleOffset(1.2,"y")   # set the pad title size
    rt.gStyle.SetLabelFont(42,"xyz")
    rt.gStyle.SetLabelSize(0.05,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(42)
    rt.gStyle.SetTextSize(0.08)
    rt.gStyle.SetStatFont(42)

    # use bold lines and markers
    rt.gStyle.SetMarkerStyle(8)
    rt.gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

    #..Get rid of X error bars
    rt.gStyle.SetErrorX(0.001)

    # do not display any of the standard histogram decorations
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptFit(11111111)

    # put tick marks on top and RHS of plots
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)

    ncontours = 999

    stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
    red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
    green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
    blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)

    npoints = len(s)
    rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    rt.gStyle.SetNumberContours(ncontours)

    rt.gStyle.cd()


if __name__ == '__main__':

    rt.gROOT.SetBatch()
    parser = OptionParser()
    parser.add_option('-b','--box',dest="box", default="CaloDijet",type="string",
                  help="box name")
    parser.add_option('-m','--model',dest="model", default="gg",type="string",
                  help="signal model name")
    parser.add_option('-d','--dir',dest="outDir",default="./",type="string",
                  help="Input/Output directory to store output")
    parser.add_option('-l','--lumi',dest="lumi", default=1.,type="float",
                  help="integrated luminosity in fb^-1")
    parser.add_option('--massMin',dest="massMin", default=500.,type="float",
                  help="minimum mass")
    parser.add_option('--massMax',dest="massMax", default=8000.,type="float",
                  help="maximum mass")
    parser.add_option('--xsecMin',dest="xsecMin", default=1e-4,type="float",
                  help="minimum mass")
    parser.add_option('--xsecMax',dest="xsecMax", default=1e4,type="float",
                  help="maximum mass")
    parser.add_option('--signif',dest="doSignificance",default=False,action='store_true',
                  help="for significance instead of limit")
    parser.add_option('--bayes',dest="bayes",default=False,action='store_true',
                  help="for bayesian limits")
    parser.add_option('--no-sys',dest="noSys",default=False,action='store_true',
                  help="for no systematics limits")
    parser.add_option('--coupling',dest="isCouplingLimit",default=False,type="string",
                  help="calculate coupling limits")
    parser.add_option('--no-data',dest="noData",default=False,action='store_true',
                  help="remove data plot")
#    parser.add_option('--matching',dest="matching",default="jets01",#type="string",
#                  help="apply matching", choices=["jets01", "jets02", "jets12", "jetsij"])


    (options,args) = parser.parse_args()
    Boxes = options.box.split('_')
    models = options.model.split('_')
    model = models[0]
    directory      = options.outDir
    Box = Boxes[0]
    box = Box.lower()
    isCouplingLimit = options.isCouplingLimit
    matching = options.isCouplingLimit
    if matching == False: matching = "jets01"
    # acc_dict = acceptance_func(matching)

    thyXsecDict = getThyXsecDict()
    thyModels = thyXsecDict.keys()

    thyModelsToDraw = []

    if options.model=='gg':
        if 'PF' in options.box:
            thyModelsToDraw = ['S8']
        else:
            thyModelsToDraw = []
    elif options.model=='qq':
        if 'PF' in options.box:
            thyModelsToDraw = ['AxigluonNLO','E6Diquark',"W'","Z'",'DM1GeV']
        if 'PF' in options.box and 'bb' in options.box:
            thyModelsToDraw = ["Zprimebb",'DMbb1GeV']
        else:
#            thyModelsToDraw = ['AxigluonkNLO','E6Diquark',"W'","Z'",'DM1GeV']
            thyModelsToDraw = ['DM1GeV']
    elif options.model=='qg':
        if 'PF' in options.box:
            thyModelsToDraw = ['String','q*']
        else:
            thyModelsToDraw = ['q*']
    elif options.model=='gg_qq_gaus' or options.model=='gg_qq_gaus10':
        thyModelsToDraw = ['AxigluonkNLO','E6Diquark',"W'","Z'"]
    elif options.model=='gg_qg_qq':
        thyModelsToDraw = ['String','q*','AxigluonNLO','E6Diquark','S8',"W'","Z'",'DM1GeV','RSGraviton']
    elif options.model=='gg_qg_qq_gaus' or options.model=='gg_qg_qq_gaus10':
        thyModelsToDraw = ['q*','AxigluonkNLO','E6Diquark','RSGraviton',"W'","Z'","DM1GeV"]
    elif options.model=='rsg':
        thyModelsToDraw = ['RSGraviton']

    if isCouplingLimit:
        thyModelsToDraw = ['DM1GeV']

    lineStyle = {'RSGravitonGG':4,
                 'RSGraviton':4,
                 'Axigluon':2,
                 'AxigluonkNLO':3,
                 'AxigluonNLO':3,
                 'E6Diquark':9,
                 'S8':1,
                 "W'":5,
                 "Z'":6,
                 "Zprimebb":6,
                 "String":7,
                 "q*":10,
                 "DM1GeV": 8,
                 "DMbb1GeV": 8,
                 'None':1
                 }

    lineColor = {'RSGravitonGG':rt.kGray+1,
                 'RSGraviton':rt.kAzure+3,
                 'Axigluon':rt.kBlue+1,
                 'AxigluonkNLO':rt.kBlue+1,
                 'AxigluonNLO':rt.kBlue+1,
                 'E6Diquark':rt.kOrange+2,
                 'S8':rt.kMagenta,
                 "W'":rt.kRed+1,
                 "Z'":rt.kBlue-1,
                 "Zprimebb":rt.kBlue-1,
                 "DM1GeV":rt.kViolet,
                 "DMbb1GeV":rt.kViolet,
                 "String":rt.kAzure-3,
                 "q*":rt.kBlack,
                 'None':1,
                 'gg':rt.kGreen+1,
                 'qq':rt.kRed,
                 'qg':rt.kBlue,
                 'gaus':rt.kCyan+1,
                 'gaus10':rt.kCyan+1
                 }

    markerStyle = {'gg':24,
                 'qq':20,
                 'qg':23,
                 'gaus':26,
                 'gaus10':26
                 }

    legendLabel = {'RSGravitonGG':'RS graviton (gg#rightarrowG#rightarrowgg)',
                   'RSGraviton':'RS graviton',
                   'Axigluon':     'Axiguon/coloron      ',
                   'AxigluonkNLO': 'Axiguon/coloron      ',
                   'AxigluonNLO':  'Axiguon/coloron      ',
                   'E6Diquark':'Scalar diquark',
                   'S8':'Color-octet scalar (k_{s}^{2} = 1/2) ',
                   #'S8':'Color-octet scalar',
                   'None': '',
                   "W'": "W'",
                   "Z'": "Z'",
                   "Zprimebb": "Z' to bb",
                   "DM1GeV": "DM mediator",
                   "DMbb1GeV": "DM mediator to bb",
                    "String": "String",
                    "q*": "Excited quark",
                   'gg':'gluon-gluon',
                   'qq':'quark-quark',
                   'qg':'quark-gluon',
                   'gaus':'Gaussian, 7% width',
                   'gaus10':'Gaussian, 10% width'
                   }

    mass_xsec = {}
    sig_xsec = {}
    N_g_xsec = {}
    xsec_gr_nom = {}
    for thyModel in thyModelsToDraw:
        mass_xsec[thyModel] = array('d')
        sig_xsec[thyModel] = array('d')
        for mg in sorted(thyXsecDict[thyModel].keys()):
            if not isCouplingLimit:
                mass_xsec[thyModel].append(mg)
                sig_xsec[thyModel].append(thyXsecDict[thyModel][mg] * acc_dict[matching][int(mg)] )
            else:
                mass_xsec[thyModel].append(mg)
                thyXsecDict[thyModel][mg] = g_qsim(mg)
                sig_xsec[thyModel].append(thyXsecDict[thyModel][mg])

        N_g_xsec[thyModel] = len(mass_xsec[thyModel])
        xsec_gr_nom[thyModel] = rt.TGraph(N_g_xsec[thyModel], mass_xsec[thyModel], sig_xsec[thyModel])
        xsec_gr_nom[thyModel].SetMarkerSize(0)
        xsec_gr_nom[thyModel].SetLineWidth(2)
        xsec_gr_nom[thyModel].SetLineStyle(lineStyle[thyModel])
        xsec_gr_nom[thyModel].SetLineColor(lineColor[thyModel])
    #print thyXsecDictmass_xsec
    setstyle()
    rt.gStyle.SetOptStat(0)
    c = rt.TCanvas("c","c",800,800)
    if options.doSignificance or options.isCouplingLimit:
#    if options.doSignificance:
        c.SetLogy(0)
    else:
        c.SetLogy()

    h_limit = rt.TMultiGraph()
    gr_observedLimit = {}
    gr_expectedLimit = {}
    gr_expectedLimit2sigma = {}
    gr_expectedLimit1sigma = {}
    gluinoMassArray = {}
    gluinoMassArray_er = {}
    observedLimit = {}
    observedLimit_er = {}
    expectedLimit = {}
    expectedLimit_minus1sigma = {}
    expectedLimit_plus1sigma = {}
    expectedLimit_minus2sigma = {}
    expectedLimit_plus2sigma = {}

    if options.doSignificance:
        h_limit.SetTitle(" ;Resonance mass [GeV];Local significance n#sigma")
    else:
        if isCouplingLimit:
            h_limit.SetTitle(" ;Resonance mass [GeV]; Coupling g'_{q}")
        else:
            h_limit.SetTitle(" ;Resonance mass [GeV]; #sigma #times #bf{#it{#Beta}} #times #bf{#it{#Alpha}} [pb]")

    for Box in Boxes:
        for model in models:
	    if not model=='rsg':
                if len(models)>1:
                    #directory =  options.outDir+'/%s_IntermediateRange'%model
                    directory =  options.outDir+'/%s'%model
                if options.doSignificance:
                    gluinoMassArray[(Box,model)], gluinoMassArray_er[(Box,model)], observedLimit[(Box,model)], observedLimit_er[(Box,model)], expectedLimit[(Box,model)], expectedLimit_minus1sigma[(Box,model)], expectedLimit_plus1sigma[(Box,model)], expectedLimit_minus2sigma[(Box,model)], expectedLimit_plus2sigma[(Box,model)] = getSignificanceArrays(directory, model, Box)
                else:
                    gluinoMassArray[(Box,model)], gluinoMassArray_er[(Box,model)], observedLimit[(Box,model)], observedLimit_er[(Box,model)], expectedLimit[(Box,model)], expectedLimit_minus1sigma[(Box,model)], expectedLimit_plus1sigma[(Box,model)], expectedLimit_minus2sigma[(Box,model)], expectedLimit_plus2sigma[(Box,model)] = getHybridCLsArrays(directory, model, Box, options.bayes)
	    else:
                    gluinoMassArray[(Box,model)], gluinoMassArray_er[(Box,model)], observedLimit[(Box,model)], observedLimit_er[(Box,model)], expectedLimit[(Box,model)], expectedLimit_minus1sigma[(Box,model)], expectedLimit_plus1sigma[(Box,model)], expectedLimit_minus2sigma[(Box,model)], expectedLimit_plus2sigma[(Box,model)] = getHybridCLsArraysRSG(directory,  Box)


            nPoints = len(observedLimit[(Box,model)])

            gr_observedLimit[(Box,model)] = rt.TGraph(nPoints, gluinoMassArray[(Box,model)], observedLimit[(Box,model)])
            gr_observedLimit[(Box,model)].SetMarkerColor(1)
            gr_observedLimit[(Box,model)].SetMarkerStyle(22)
            gr_observedLimit[(Box,model)].SetMarkerSize(1)
            gr_observedLimit[(Box,model)].SetLineWidth(3)
            gr_observedLimit[(Box,model)].SetLineColor(rt.kBlack)
            gr_observedLimit[(Box,model)].SetMarkerStyle(20)
            if len(models)>1:
                gr_observedLimit[(Box,model)].SetLineColor(lineColor[model])
                gr_observedLimit[(Box,model)].SetMarkerStyle(markerStyle[model])
                gr_observedLimit[(Box,model)].SetMarkerColor(lineColor[model])


            gr_expectedLimit[(Box,model)] = rt.TGraph(nPoints, gluinoMassArray[(Box,model)], expectedLimit[(Box,model)])
            gr_expectedLimit[(Box,model)].SetLineWidth(3)
            gr_expectedLimit[(Box,model)].SetLineStyle(2)
            if len(models)>1:
                gr_expectedLimit[(Box,model)].SetLineColor(lineColor[model])

            gr_expectedLimit2sigma[(Box,model)] = rt.TGraphAsymmErrors(nPoints, gluinoMassArray[(Box,model)], expectedLimit[(Box,model)], gluinoMassArray_er[(Box,model)], gluinoMassArray_er[(Box,model)], expectedLimit_minus2sigma[(Box,model)], expectedLimit_plus2sigma[(Box,model)])
            #gr_expectedLimit2sigma[(Box,model)].SetLineColor(5)
            #gr_expectedLimit2sigma[(Box,model)].SetFillColor(5)
            gr_expectedLimit2sigma[(Box,model)].SetLineColor(rt.kOrange)
            gr_expectedLimit2sigma[(Box,model)].SetFillColor(rt.kOrange)
            gr_expectedLimit2sigma[(Box,model)].SetFillStyle(1001)

            gr_expectedLimit1sigma[(Box,model)] = rt.TGraphAsymmErrors(nPoints, gluinoMassArray[(Box,model)], expectedLimit[(Box,model)], gluinoMassArray_er[(Box,model)], gluinoMassArray_er[(Box,model)], expectedLimit_minus1sigma[(Box,model)], expectedLimit_plus1sigma[(Box,model)])

            #gr_expectedLimit1sigma[(Box,model)].SetLineColor(rt.kGreen-7)
            #gr_expectedLimit1sigma[(Box,model)].SetFillColor(rt.kGreen-7)
            gr_expectedLimit1sigma[(Box,model)].SetLineColor(rt.kGreen+1)
            gr_expectedLimit1sigma[(Box,model)].SetFillColor(rt.kGreen+1)

            if len(models)==1:
                h_limit.Add(gr_expectedLimit2sigma[(Box,model)])
                h_limit.Add(gr_expectedLimit1sigma[(Box,model)])
            h_limit.Add(gr_observedLimit[(Box,model)])


    for thyModel in thyModelsToDraw:
        h_limit.Add(xsec_gr_nom[thyModel])

    h_limit.Draw("a3")
    if 'PF' in Box:
        h_limit.GetXaxis().SetLimits(options.massMin,options.massMax)
    else:
        h_limit.GetXaxis().SetLimits(options.massMin,options.massMax)
    if options.doSignificance:
        h_limit.SetMaximum(4)
        h_limit.SetMinimum(0)
    else:
        if 'PF' in Box:
            h_limit.SetMaximum(options.xsecMax)
            h_limit.SetMinimum(options.xsecMin)
        else:
            h_limit.SetMaximum(options.xsecMax)
            h_limit.SetMinimum(options.xsecMin)

    h_limit.Draw("a3")
    if options.doSignificance:
        h_limit.GetYaxis().SetNdivisions(405,True)

    for Box in Boxes:
        for model in models:
            if options.doSignificance:
                gr_observedLimit[(Box,model)].SetMarkerStyle(21)
                gr_observedLimit[(Box,model)].SetMarkerSize(1)
                gr_observedLimit[(Box,model)].SetLineColor(rt.kRed)
                gr_observedLimit[(Box,model)].SetMarkerColor(rt.kBlue)
                gr_observedLimit[(Box,model)].Draw("lp SAME")
            else:
                if len(models)==1:
                    gr_expectedLimit[(Box,model)].Draw("c same")
                for thyModel in thyModelsToDraw:
                    xsec_gr_nom[thyModel].Draw("c same")
                gr_observedLimit[(Box,model)].Draw("lp SAME")

            gr_expectedLimit1sigma[(Box,model)].SetLineStyle(2)
            gr_expectedLimit1sigma[(Box,model)].SetLineWidth(3)
            gr_expectedLimit1sigma[(Box,model)].SetLineColor(rt.kBlack)
            gr_expectedLimit2sigma[(Box,model)].SetLineStyle(2)
            gr_expectedLimit2sigma[(Box,model)].SetLineWidth(3)
            gr_expectedLimit2sigma[(Box,model)].SetLineColor(rt.kBlack)

    l = rt.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetNDC()
    l.SetTextFont(62)
    #l.DrawLatex(0.17,0.92,"CMS")
    if len(Boxes)>1 and len(models)>1:
        l.DrawLatex(0.3,0.77,"CMS")
    elif len(Boxes)>1:
        l.DrawLatex(0.41,0.835,"CMS")
    else:
        l.DrawLatex(0.2,0.835,"CMS")

    l.SetTextFont(52)
    #l.DrawLatex(0.28,0.92,"Preliminary")
    l.SetTextFont(42)
    #l.DrawLatex(0.65,0.92,"%.0f pb^{-1} (13 TeV)"%(options.lumi*1000))
    l.DrawLatex(0.63,0.92,"%.1f fb^{-1} (13 TeV)"%(options.lumi))

    if options.model=="gg":
        if len(Boxes)>1:
            l.DrawLatex(0.3,0.77,"gluon-gluon")
        else:
            l.DrawLatex(0.3,0.77,"gluon-gluon")
    elif options.model=="qg":
        if len(Boxes)>1:
            l.DrawLatex(0.3,0.77,"quark-gluon")
        else:
            l.DrawLatex(0.3,0.77,"quark-gluon")
    elif options.model=="qq":
        if len(Boxes)>1:
            l.DrawLatex(0.3,0.77,"quark-quark")
        else:
            l.DrawLatex(0.3,0.77,"quark-quark")
    elif options.model=="gaus":
        l.SetTextSize(0.04)
        if len(Boxes)>1:
            l.DrawLatex(0.24,0.79,"Gaussian, 7% width")
        else:
            l.DrawLatex(0.24,0.835,"Gaussian, 7% width")
        l.SetTextSize(0.045)
    elif options.model=="gaus10":
        l.SetTextSize(0.04)
        if len(Boxes)>1:
            l.DrawLatex(0.3,0.79,"#splitline{Gaussian}{10% width}")
        else:
            l.DrawLatex(0.3,0.77,"#splitline{Gaussian}{10% width}")
        l.SetTextSize(0.045)

    #if options.bayes:
    #    if options.noSys:
    #        l.DrawLatex(0.2,0.85,"Bayesian, no syst.")
    #    else:
    #        l.DrawLatex(0.2,0.85,"Bayesian, with syst.")
    #else:
    #    if options.noSys:
    #        l.DrawLatex(0.2,0.85,"Frequentist, no syst.")
    #    else:
    #        l.DrawLatex(0.2,0.85,"Frequentist, with syst.")

    if options.doSignificance:
        c.SetGridy()
        leg = rt.TLegend(0.55,0.79,0.92,0.87)
    elif options.model =="gg_qg_qq" and options.box=="CaloDijet2016_PFDijet2016":
        leg = rt.TLegend(0.19,0.17,0.57,0.35)
    else:
        leg = rt.TLegend(0.55,0.68,0.92,0.87)

    leg.SetTextFont(42)
    leg.SetFillColorAlpha(0,0)
    leg.SetLineColor(0)
    if not options.doSignificance:
        leg.SetHeader("95% CL limits")
    if len(models)==1:
        if options.doSignificance:
            leg.AddEntry(gr_observedLimit[(Box,model)], "Observed","lp")
        else:
            #leg.AddEntry(None,"95% CL limits","")
            #leg.AddEntry(None,"90% CL limits","")
            leg.AddEntry(gr_observedLimit[(Box,model)], "Observed","lp")
        if not options.doSignificance:
            leg.AddEntry(gr_expectedLimit1sigma[(Box,model)], "Expected #pm 1 s.d.","lf")
        if not options.doSignificance:
            leg.AddEntry(gr_expectedLimit2sigma[(Box,model)], "Expected #pm 2 s.d.","lf")
    else:
        #leg.AddEntry(None,"95% CL limits","")
        #leg.AddEntry(None,"90% CL limits","")
        for model in models:
            leg.AddEntry(gr_observedLimit[(Box,model)], legendLabel[model],"lp")

    leg.Draw("SAME")

    if len(thyModelsToDraw)>0 and not options.doSignificance:
        if options.model =="gg_qg_qq" and options.box=="CaloDijet2016_PFDijet2016":
            #legThyModel = rt.TLegend(0.2,0.17,0.55,0.45)
            legThyModel = rt.TLegend(0.45,0.7,0.9,0.92)
            legThyModel2 = rt.TLegend(0.55,0.54,0.9,0.7)
            legThyModel2.SetTextFont(42)
            legThyModel2.SetFillColor(rt.kWhite)
            legThyModel2.SetLineColor(rt.kWhite)
            legThyModel2.SetFillColorAlpha(0,0)
            legThyModel2.SetLineColorAlpha(0,0)
        elif options.model =="gg":
            #legThyModel = rt.TLegend(0.2,0.17,0.6,0.4)
            legThyModel = rt.TLegend(0.2,0.17,0.7,0.4)
        else:
            legThyModel = rt.TLegend(0.2,0.17,0.55,0.4)
        legThyModel.SetTextFont(42)
        legThyModel.SetFillColor(rt.kWhite)
        legThyModel.SetLineColor(rt.kWhite)
        legThyModel.SetFillColorAlpha(0,0)
        legThyModel.SetLineColorAlpha(0,0)

        if model=='qq':
            legThyModel.AddEntry(None,"","")
        elif model=='gg':
            legThyModel.AddEntry(None,"","")

        for i, thyModel in enumerate(thyModelsToDraw):
            if i>4:
                try:
                    legThyModel2.AddEntry(xsec_gr_nom[thyModel], legendLabel[thyModel],'l')
                except:
                    pass
            else:
                legThyModel.AddEntry(xsec_gr_nom[thyModel], legendLabel[thyModel],'l')
        legThyModel.Draw("same")
        try:
            legThyModel2.Draw("same")
        except:
            pass


    for Box in Boxes:
        for model in models:
            if options.doSignificance:
                gr_observedLimit[(Box,model)].Draw("lp SAME")
            else:
                if len(models)==1:
                    gr_expectedLimit[(Box,model)].Draw("c same")
                for thyModel in thyModelsToDraw:
                    xsec_gr_nom[thyModel].Draw("c same")
                gr_observedLimit[(Box,model)].Draw("lp SAME")


    if 'PF' in Box or options.massMax>1600:
        if model=='rsg':
            h_limit.GetXaxis().SetTitle('RS Graviton mass [TeV]')
        else:
	    h_limit.GetXaxis().SetTitle('Resonance mass [TeV]')
	h_limit.GetXaxis().SetLabelOffset(1000)
        #h_fit_residual_vs_mass.GetXaxis().SetNoExponent()
        #h_fit_residual_vs_mass.GetXaxis().SetMoreLogLabels()
        xLab = rt.TLatex()
        xLab.SetTextAlign(22)
        xLab.SetTextSize(0.05)
        xLab.SetTextFont(42)
        xLab.SetTextSize(0.05)
        if options.doSignificance:
            yOffset = -0.138
        else:
            #yOffset = 6.5e-5 # for 1e-4 min
            #yOffset = 5.25e-6 # for 1e-5 min
            yOffset = 5.25e-8 # for 1e-5 min
        for i in range(1,10):
            if i*1000>=options.massMin:
                xLab.DrawLatex(i*1000, yOffset, "%g"%i)

    else:
        if model=='rsg':
            h_limit.GetXaxis().SetTitle('RS Graviton mass [TeV]')
        else:
            h_limit.GetXaxis().SetTitle('Resonance mass [GeV]')
        h_limit.GetXaxis().SetNdivisions(408,True)

    if options.box=="CaloDijet2016_PFDijet2016":
        #line1 = rt.TLine(1600,1e4,1600,options.xsecMax)
        line1 = rt.TLine(1600,1e-1,1600,options.xsecMax)
        line1.SetLineStyle(2)
        line1.SetLineWidth(2)
        line1.SetLineColor(rt.kGray+1)
        line1.Draw()
        #line2 = rt.TLine(1600,1e-1,1600,2)
        #line2.SetLineStyle(2)
        #line2.SetLineWidth(2)
        #line2.SetLineColor(rt.kGray+1)
        #line2.Draw()


        lab = rt.TLatex()
        lab.SetTextSize(0.035)
        lab.SetTextFont(42)
        lab.SetTextColor(rt.kGray+1)
        lab.SetTextAlign(33)
        lab.DrawLatex(1600-10,6e4,"#leftarrow")
        lab.SetTextAlign(13)
        lab.DrawLatex(1600+10,6e4,"#rightarrow")
        lab.SetTextAlign(23)
        lab.DrawLatex(1600-400,3.5e4,"Low")
        lab.DrawLatex(1600-400,1.2e4,"mass")
        lab.DrawLatex(1600+400,3.5e4,"High")
        lab.DrawLatex(1600+400,1.2e4,"mass")


    if options.isCouplingLimit:
        options.model = options.model + "_couplings"

    #c.SetLogx()
    c.RedrawAxis() # request from David
    if options.doSignificance:
        c.SaveAs(options.outDir+"/signif_"+options.model+"_"+options.box.lower()+".pdf")
        c.SaveAs(options.outDir+"/signif_"+options.model+"_"+options.box.lower()+".C")
    else:
        if options.bayes:
            if options.noSys:
                c.SaveAs(options.outDir+"/limits_bayes_nosys_"+options.model+"_"+options.box.lower()+".pdf")
                c.SaveAs(options.outDir+"/limits_bayes_nosys_"+options.model+"_"+options.box.lower()+".C")
            else:
                c.SaveAs(options.outDir+"/limits_bayes_"+options.model+"_"+options.box.lower()+".pdf")
                c.SaveAs(options.outDir+"/limits_bayes_"+options.model+"_"+options.box.lower()+".C")
        else:
            if options.noSys:
                c.SaveAs(options.outDir+"/limits_freq_nosys_"+options.model+"_"+options.box.lower()+".pdf")
                c.SaveAs(options.outDir+"/limits_freq_nosys_"+options.model+"_"+options.box.lower()+".C")
            else:
                c.SaveAs(options.outDir+"/limits_freq_"+options.model+"_"+options.box.lower()+".pdf")
                c.SaveAs(options.outDir+"/limits_freq_"+options.model+"_"+options.box.lower()+".C")
                outFile = rt.TFile.Open(options.outDir+"/limits_freq_"+options.model+"_"+options.box.lower()+".root","recreate")
                outFile.cd()
                c.Write()
                graphDict = {}
                graphDict['obs'] = gr_observedLimit
                graphDict['exp'] = gr_expectedLimit
                graphDict['exp1sigma'] = gr_expectedLimit1sigma
                graphDict['exp2sigma'] = gr_expectedLimit2sigma
                for limitType, graphs in graphDict.iteritems():
                    for (Box,model), graph in graphs.iteritems():
                        graph.SetName('%s_%s_%s'%(limitType,model,Box.lower()))
                        graph.Write()
