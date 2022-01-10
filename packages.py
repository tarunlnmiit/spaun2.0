from __future__ import print_function

import os
import sys
import time
import gzip
import subprocess
import logging

import nengo
import nengo_gui
import nengo_ocl

import pyopencl as cl

# ----- Spaun imports -----
from _spaun.configurator import cfg
from _spaun.vocabulator import vocab
from _spaun.experimenter import experiment
from _spaun.loggerator import logger
from _spaun.utils import get_probe_data_filename

from _spaun.utils import get_total_n_neurons
from _spaun.spaun_main import Spaun

from _spaun.modules.stim import stim_data
from _spaun.modules.vision import vis_data
from _spaun.modules.motor import mtr_data

# ----- Set up probes -----
from _spaun import probes as probe_module