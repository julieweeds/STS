__author__ = 'juliewe'
#to convert vector file from frequencies into PPMI
from featuretotals import Totals

###filenames local
#dirname = "/Volumes/research/calps/data3/juliewe/exp6-12/"
### apollo
dirname = "/mnt/lustre/scratch/inf/juliewe/FeatureExtractionToolkit/Byblo-2.1.0/giga_t100f100_nouns_deps/"
filename = "vectors"

inputname = dirname + filename

mytotals = Totals()
mytotals.readfile(inputname)
#mytotals.output()
