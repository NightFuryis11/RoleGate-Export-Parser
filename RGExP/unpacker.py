import os
import sys
import json
from datetime import datetime
import pickle
import main as ma

from operator import attrgetter

dname = input("> Type the filename of the data you would like to read without the .pkl extension: ")

ma.pickleunpack(dname)