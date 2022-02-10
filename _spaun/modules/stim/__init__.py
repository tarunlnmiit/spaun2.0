import importlib

from ...configurator import cfg
# cfg.stim_module is MNIST by default
stim_module = importlib.import_module('_spaun.modules.stim.' + cfg.stim_module)
# Object of Dataset class based on cfg.stim_module
stim_data = stim_module.DataObject()
