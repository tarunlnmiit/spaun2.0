# ----- Configuration presets -----
cfg_presets = {}
cfg_presets['mtr_adapt_qvelff'] = ["mtr_dyn_adaptation=True",
                                   "mtr_forcefield='QVelForcefield'"]
cfg_presets['mtr_adapt_constff'] = ["mtr_dyn_adaptation=True",
                                    "mtr_forcefield='ConstForcefield'"]

cfg_presets['vis_imagenet'] = ["stim_module='imagenet'",
                               "vis_module='lif_imagenet'"]
cfg_presets['vis_imagenet_wta'] = ["stim_module='imagenet'",
                                   "vis_module='lif_imagenet_wta'"]

# Darpa adaptive motor demo configs
cfg_presets['darpa_adapt_qvelff_demo'] = \
    ["mtr_dyn_adaptation=True", "mtr_forcefield='QVelForcefield'",
     "probe_graph_config='ProbeCfgDarpaMotor'"]
cfg_presets['darpa_adapt_constff_demo'] = \
    ["mtr_dyn_adaptation=True", "mtr_forcefield='ConstForcefield'",
     "probe_graph_config='ProbeCfgDarpaMotor'"]

# Darpa imagenet demo configs
cfg_presets['darpa_vis_imagenet'] = \
    ["stim_module='imagenet'", "vis_module='lif_imagenet'",
     "probe_graph_config='ProbeCfgDarpaVisionImagenet'"]
cfg_presets['darpa_vis_imagenet_wta'] = \
    ["stim_module='imagenet'", "vis_module='lif_imagenet_wta'",
     "probe_graph_config='ProbeCfgDarpaVisionImagenet'"]

# Darpa imagenet + instruction following + adaptive motor configs
cfg_presets['darpa_combined_demo'] = \
    ["mtr_dyn_adaptation=True", "mtr_forcefield='QVelForcefield'",
     "stim_module='imagenet'", "vis_module='lif_imagenet'",
     "probe_graph_config='ProbeCfgDarpaImagenetAdaptMotor'"]
cfg_presets['darpa_combined_noadapt_demo'] = \
    ["mtr_dyn_adaptation=False", "mtr_forcefield='QVelForcefield'",
     "stim_module='imagenet'", "vis_module='lif_imagenet'",
     "probe_graph_config='ProbeCfgDarpaImagenetAdaptMotor'"]
cfg_presets['cbc_combined_noadapt_demo'] = \
    ["mtr_dyn_adaptation=False",
     "stim_module='imagenet'", "vis_module='lif_imagenet'",
     "probe_graph_config='ProbeCfgVisMtrMemSpikes'"]