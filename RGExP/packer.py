import os
import sys
import json
from datetime import datetime
import pickle
import main as ma

from operator import attrgetter

gname = input("> Type the filename of the data you would like to read without the .json extension: ")

ma.picklepack(gname)