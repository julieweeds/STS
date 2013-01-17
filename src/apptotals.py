__author__ = 'juliewe'
from featuretotals import Totals

###filenames local
dirname = "/Volumes/research/calps/data3/juliewe/exp6-12/"
filename = "vectors"

inputname = dirname + filename

mytotals = Totals()
mytotals.readfile(inputname)
#mytotals.output()
