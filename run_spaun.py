from packages import *
from presets.stimulus import *
from presets.configuration import *
from arguments import *


# ----- Nengo RC Cache settings -----
# Disable cache unless seed is set (i.e. seed > 0) or if the '--enable_cache'
# option is given
# RC = Resistor-Capacitor TODO: Not sure?
if args.seed > 0 or args.enable_cache:
    print("USING CACHE")
    nengo.rc.set("decoder_cache", "enabled", "True")
else:
    print("NOT USING CACHE")
    nengo.rc.set("decoder_cache", "enabled", "False")

# ----- Backend Configurations -----
# cfg = Spaun Configurator class by the name SpaunConfig
cfg.backend = args.b  # default backend is nengo reference simulator | Use ocl with GPU systems
if args.ocl:
    cfg.backend = 'ocl'
if args.mpi:
    cfg.backend = 'mpi'
if args.spinn:
    cfg.backend = 'spinn'

print("BACKEND: %s" % cfg.backend.upper())
print("STIM MODULE: %s" % cfg.stim_module.upper())

# ----- Stimulus sequence settings -----
if args.stim_preset in stim_presets:
    stim_seq_str, instr_seq_str = stim_presets[args.stim_preset]
else:
    stim_seq_str = args.s
    instr_seq_str = args.i

# ----- Gather configuration (from --config and --config_presets) settings ----
# Probably won't be using this argument ????
config_list = []
if args.config is not None:
    config_list += args.config

if args.config_presets is not None:
    for preset_name in args.config_presets:
        if preset_name in cfg_presets:
            config_list += cfg_presets[preset_name]

# ----- Batch runs -----
for n in range(args.n):
    print("\n======================== RUN %i OF %i ========================" %
          (n + 1, args.n))

    # ----- Seeeeeeeed -----
    if args.seed < 0:
        seed = int(time.time())
    else:
        seed = args.seed

    cfg.set_seed(seed)
    print("MODEL SEED: %i" % cfg.seed)

    # ----- Model Configurations -----
    vocab.sp_dim = args.d
    cfg.data_dir = args.data_dir

    # Parse --config options
    if len(config_list) > 0:
        print("USING CONFIGURATION OPTIONS: ")
        for cfg_options in config_list:
            cfg_opts = cfg_options.split('=')
            cfg_param = cfg_opts[0]
            cfg_value = cfg_opts[1]
            if hasattr(cfg, cfg_param):
                print("  * cfg: " + str(cfg_options))
                setattr(cfg, cfg_param, eval(cfg_value))
            elif hasattr(experiment, cfg_param):
                print("  * experiment: " + str(cfg_options))
                setattr(experiment, cfg_param, eval(cfg_value))
            elif hasattr(vocab, cfg_param):
                print("  * vocab: " + str(cfg_options))
                setattr(vocab, cfg_param, eval(cfg_value))

    # ----- Check if data folder exists -----
    if not(os.path.isdir(cfg.data_dir) and os.path.exists(cfg.data_dir)):
        raise RuntimeError('Data directory "%s"' % (cfg.data_dir) +
                           ' does not exist. Please ensure the correct path' +
                           ' has been specified.')

    # ----- Enable debug logging -----
    if args.debug:
        logging.debug('debug')

    # ----- Experiment and vocabulary initialization -----
    experiment.initialize(stim_seq_str, stim_data.get_image_ind,
                          stim_data.get_image_label,
                          cfg.mtr_est_digit_response_time, instr_seq_str,
                          cfg.rng)
    vocab.initialize(stim_data.stim_SP_labels, experiment.num_learn_actions,
                     cfg.rng)
    vocab.initialize_mtr_vocab(mtr_data.dimensions, mtr_data.sps)
    vocab.initialize_vis_vocab(vis_data.dimensions, vis_data.sps)

    # ----- Spaun module configuration -----
    if args.modules is not None:
        used_modules = cfg.spaun_modules
        arg_modules = args.modules.upper()

        if arg_modules[0] == '-':
            used_modules = ''.join([s if s not in arg_modules else ''
                                    for s in used_modules])
        else:
            used_modules = arg_modules

        cfg.spaun_modules = used_modules

    # ----- Configure output log files -----
    if cfg.use_mpi:
        sys.path.append('C:\\Users\\xchoo\\GitHub\\nengo_mpi')

        mpi_save = args.mpi_save.split('.')
        mpi_savename = '.'.join(mpi_save[:-1])
        mpi_saveext = mpi_save[-1]

        cfg.probe_data_filename = get_probe_data_filename(mpi_savename,
                                                          suffix=args.tag)
    else:
        cfg.probe_data_filename = get_probe_data_filename(suffix=args.tag)

    # ----- Initalize looger and write header data -----
    logger.initialize(cfg.data_dir, cfg.probe_data_filename[:-4] + '_log.txt')

    logger.write('# Spaun Command Line String:\n')
    logger.write('# -------------------------\n')
    logger.write('# python ' + ' '.join(sys.argv) + '\n')
    logger.write('#\n')

    cfg.write_header()
    experiment.write_header()
    vocab.write_header()
    logger.flush()

    # ----- Raw stimulus seq -----
    print("RAW STIM SEQ: %s" % (str(experiment.raw_seq_str)))

    # ----- Spaun proper -----
    model = Spaun()

    # ----- Display stimulus seq -----
    print("PROCESSED RAW STIM SEQ: %s" % (str(experiment.raw_seq_list)))
    print("STIMULUS SEQ: %s" % (str(experiment.stim_seq_list)))

    # ----- Calculate runtime -----
    # Note: Moved up here so that we have data to disable probes if necessary
    runtime = args.t if args.t > 0 else experiment.get_est_simtime()

    make_probes = not args.noprobes
    if runtime > max_probe_time and make_probes:
        print(">>> !!! WARNING !!! EST RUNTIME > %0.2fs - DISABLING PROBES" %
              max_probe_time)
        make_probes = False

    if make_probes:
        print("PROBE FILENAME: %s" % cfg.probe_data_filename)
        default_probe_config = getattr(probe_module, cfg.probe_graph_config)
        probe_cfg = default_probe_config(model, vocab, cfg.sim_dt,
                                         cfg.data_dir,
                                         cfg.probe_data_filename)

    # ----- Set up animation probes -----
    if args.showanim or args.showiofig or args.probeio:
        anim_probe_data_filename = cfg.probe_data_filename[:-4] + '_anim.npz'
        default_anim_config = getattr(probe_module, cfg.probe_anim_config)
        print("ANIM PROBE FILENAME: %s" % anim_probe_data_filename)
        probe_anim_cfg = default_anim_config(model, vocab,
                                             cfg.sim_dt, cfg.data_dir,
                                             anim_probe_data_filename)

    # ----- Neuron count debug -----
    print("MODEL N_NEURONS:  %i" % (get_total_n_neurons(model)))
    if hasattr(model, 'vis'):
        print("- vis   n_neurons: %i" % (get_total_n_neurons(model.vis)))
    if hasattr(model, 'ps'):
        print("- ps    n_neurons: %i" % (get_total_n_neurons(model.ps)))
    if hasattr(model, 'reward'):
        print("- rewrd n_neurons: %i" % (get_total_n_neurons(model.reward)))
    if hasattr(model, 'bg'):
        print("- bg    n_neurons: %i" % (get_total_n_neurons(model.bg)))
    if hasattr(model, 'thal'):
        print("- thal  n_neurons: %i" % (get_total_n_neurons(model.thal)))
    if hasattr(model, 'enc'):
        print("- enc   n_neurons: %i" % (get_total_n_neurons(model.enc)))
    if hasattr(model, 'mem'):
        print("- mem   n_neurons: %i" % (get_total_n_neurons(model.mem)))
    if hasattr(model, 'trfm'):
        print("- trfm  n_neurons: %i" % (get_total_n_neurons(model.trfm)))
    if hasattr(model, 'instr'):
        print("- instr n_neurons: %i" % (get_total_n_neurons(model.instr)))
    if hasattr(model, 'dec'):
        print("- dec   n_neurons: %i" % (get_total_n_neurons(model.dec)))
    if hasattr(model, 'mtr'):
        print("- mtr   n_neurons: %i" % (get_total_n_neurons(model.mtr)))

    # ----- Connections count debug -----
    print("MODEL N_CONNECTIONS: %i" % (len(model.all_connections)))

    # ----- Spaun simulation build -----
    print("START BUILD")
    timestamp = time.time()

    if args.nengo_gui:
        # Set environment variables (for nengo_gui)
        if cfg.use_opencl:
            if args.ocl_platform >= 0 and args.ocl_device >= 0:
                os.environ['PYOPENCL_CTX'] = '%s:%s' % (args.ocl_platform,
                                                        args.ocl_device)
            else:
                raise RuntimeError('Error - OCL platform and device must be' +
                                   'specified when using ocl with nengo_gui.' +
                                   ' Use the --ocl_platform and --ocl_device' +
                                   ' argument options to set.')

        print("STARTING NENGO_GUI")
        nengo_gui.GUI(__file__, model=model, locals=locals(),
                      editor=False).start()
        print("NENGO_GUI STOPPED")
        sys.exit()

    if cfg.use_opencl:
        print("------ OCL ------")
        print("AVAILABLE PLATFORMS:")
        print('  ' + '\n  '.join(map(str, cl.get_platforms())))

        if args.ocl_platform >= 0:
            pltf = cl.get_platforms()[args.ocl_platform]
            print("USING PLATFORM:")
            print('  ' + str(pltf))

            print("AVAILABLE DEVICES:")
            print('  ' + '\n  '.join(map(str, pltf.get_devices())))
            if args.ocl_device >= 0:
                ctx = cl.Context([pltf.get_devices()[args.ocl_device]])
                print("USING DEVICE:")
                print('  ' + str(pltf.get_devices()[args.ocl_device]))
            else:
                ctx = cl.Context(pltf.get_devices())
                print("USING DEVICES:")
                print('  ' + '\n  '.join(map(str, pltf.get_devices())))
            sim = nengo_ocl.Simulator(model, dt=cfg.sim_dt, context=ctx,
                                      profiling=args.ocl_profile)
        else:
            sim = nengo_ocl.Simulator(model, dt=cfg.sim_dt,
                                      profiling=args.ocl_profile)
    elif cfg.use_mpi:
        import nengo_mpi

        mpi_savefile = \
            ('+'.join([cfg.get_probe_data_filename(mpi_savename)[:-4],
                      ('%ip' % args.mpi_p if not args.mpi_p_auto else 'autop'),
                      '%0.2fs' % experiment.get_est_simtime()]) + '.' +
             mpi_saveext)
        mpi_savefile = os.path.join(cfg.data_dir, mpi_savefile)

        print("USING MPI - Saving to: %s" % (mpi_savefile))

        if args.mpi_p_auto:
            assignments = {}
            for n, module in enumerate(model.modules):
                assignments[module] = n
            sim = nengo_mpi.Simulator(model, dt=cfg.sim_dt,
                                      assignments=assignments,
                                      save_file=mpi_savefile)
        else:
            partitioner = nengo_mpi.Partitioner(args.mpi_p)
            sim = nengo_mpi.Simulator(model, dt=cfg.sim_dt,
                                      partitioner=partitioner,
                                      save_file=mpi_savefile)
    else:
        sim = nengo.Simulator(model, dt=cfg.sim_dt)

    t_build = time.time() - timestamp
    timestamp = time.time()
    print("BUILD FINISHED - build time: %fs" % t_build)

    # ----- Spaun simulation run -----
    experiment.reset()
    if cfg.use_opencl or cfg.use_ref:
        print("START SIM - est_runtime: %f" % runtime)
        sim.run(runtime)

        # Close output logging file
        logger.close()

        if args.ocl_profile:
            sim.print_plans()
            sim.print_profiling()

        t_simrun = time.time() - timestamp
        print("MODEL N_NEURONS: %i" % (get_total_n_neurons(model)))
        print("FINISHED! - Build time: %fs, Sim time: %fs" % (t_build,
                                                              t_simrun))
    else:
        print("MODEL N_NEURONS: %i" % (get_total_n_neurons(model)))
        print("FINISHED! - Build time: %fs" % (t_build))

        if args.mpi_compress_save:
            print("COMPRESSING net file to '%s'" % (mpi_savefile + '.gz'))

            with open(mpi_savefile, 'rb') as f_in:
                with gzip.open(mpi_savefile + '.gz', 'wb') as f_out:
                    f_out.writelines(f_in)

            os.remove(mpi_savefile)

            print("UPLOAD '%s' to MPI cluster and decompress to run" %
                  (mpi_savefile + '.gz'))
        else:
            print("UPLOAD '%s' to MPI cluster to run" % mpi_savefile)
        t_simrun = -1

    # ----- Generate debug printouts -----
    n_bytes_ev = 0
    n_bytes_gain = 0
    n_bytes_bias = 0
    n_ens = 0
    for ens in sim.model.toplevel.all_ensembles:
        n_bytes_ev += sim.model.params[ens].eval_points.nbytes
        n_bytes_gain += sim.model.params[ens].gain.nbytes
        n_bytes_bias += sim.model.params[ens].bias.nbytes
        n_ens += 1

    if args.debug:
        print("## DEBUG: num bytes used for eval points: %s B" %
              ("{:,}".format(n_bytes_ev)))
        print("## DEBUG: num bytes used for gains: %s B" %
              ("{:,}".format(n_bytes_gain)))
        print("## DEBUG: num bytes used for biases: %s B" %
              ("{:,}".format(n_bytes_bias)))
        print("## DEBUG: num ensembles: %s" % n_ens)

    # ----- Close simulator -----
    if hasattr(sim, 'close'):
        sim.close()

    # ----- Write probe data to file -----
    logger.write("\n\n# Command line options for displaying recorded probed " +
                 "data:")
    logger.write("\n# ------------------------------------------------------" +
                 "---")
    if make_probes and not cfg.use_mpi:
        print("WRITING PROBE DATA TO FILE")
        probe_cfg.write_simdata_to_file(sim, experiment)

        # Assemble graphing subprocess call string
        subprocess_call_list = ["python",
                                os.path.join(cur_dir,
                                             'disp_probe_data.py'),
                                '"' + cfg.probe_data_filename + '"',
                                '--data_dir', '"' + cfg.data_dir + '"',
                                '--showgrph']

        # Log subprocess call
        logger.write("\n#\n# To display graphs of the recorded probe data:")
        logger.write("\n# > " + " ".join(subprocess_call_list))

        if args.showgrph:
            # Open subprocess
            print("CALLING: \n%s" % (" ".join(subprocess_call_list)))
            subprocess.Popen(subprocess_call_list)

    if (args.showanim or args.showiofig or args.probeio) and not cfg.use_mpi:
        print("WRITING ANIMATION PROBE DATA TO FILE")
        probe_anim_cfg.write_simdata_to_file(sim, experiment)

        # Assemble graphing subprocess call string
        subprocess_call_list = ["python",
                                os.path.join(cur_dir,
                                             'disp_probe_data.py'),
                                '"' + anim_probe_data_filename + '"',
                                '--data_dir', '"' + cfg.data_dir + '"']

        # Log subprocess call
        logger.write("\n#\n# To display Spaun's input/output plots:")
        logger.write("\n# > " + " ".join(subprocess_call_list +
                                         ['--showiofig']))
        logger.write("\n#\n# To display Spaun's input/output animation:")
        logger.write("\n# > " + " ".join(subprocess_call_list +
                                         ['--showanim']))
        logger.write("\n# (Flags can be combined to display both plots and" +
                     " animations)")

        if args.showanim:
            subprocess_call_list += ['--showanim']
        if args.showiofig:
            subprocess_call_list += ['--showiofig']

        if args.showanim or args.showiofig:
            # Open subprocess
            print("CALLING: \n%s" % (" ".join(subprocess_call_list)))
            subprocess.Popen(subprocess_call_list)

    if not (make_probes or args.showanim or args.showiofig or args.probeio):
        logger.write("\n# run_spaun.py was not instructed to record probe " +
                     "data.")

    # ----- Write runtime data -----
    runtime_filename = os.path.join(cfg.data_dir, 'runtimes.txt')
    rt_file = open(runtime_filename, 'a')
    rt_file.write('# ---------- TIMESTAMP: %i -----------\n' % timestamp)
    rt_file.write('Backend: %s | Num neurons: %i | Tag: %s | Seed: %i\n' %
                  (cfg.backend, get_total_n_neurons(model), args.tag,
                   cfg.seed))
    if args.config is not None:
        rt_file.write('Config options: %s\n' % (str(args.config)))
    rt_file.write('Build time: %fs | Model sim time: %fs | ' % (t_build,
                                                                runtime))
    rt_file.write('Sim wall time: %fs\n' % (t_simrun))
    rt_file.close()

    # ----- Cleanup -----
    model = None
    sim = None
    probe_data = None
