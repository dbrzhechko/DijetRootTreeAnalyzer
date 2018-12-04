import ROOT
import array
fullRatioPlot = False
ROOT.gStyle.SetOptFit(1111)

varX_min,  varX_max = 100,1000
fitX_min,  fitX_max = 300,700


massBoundaries = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838,  890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808,  7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]
massBoundaries = [i*5 for i in range(1000)]


newHisto = ROOT.TH1F("histo", "", len(massBoundaries)-1, array.array('f',massBoundaries))


#function = "exp([0]) / pow(x + [2] , 5 + [3] * log(x/13000) ) / ( exp([1]/(x+[3])) - 1) * (1+0*TMath::Erf((x - [4])/[5]))"
function = "(1 - exp(-(x - [0])/[1]))"



funct = ROOT.TF1("f", function, fitX_min,  fitX_max)

Npar = funct.GetNpar()
funct.FixParameter(Npar-2,-200)
funct.FixParameter(Npar-1,10)

funct.Draw()

