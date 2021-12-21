import argparse
import os

# ----- Defaults -----
def_dim = 512
def_seq = 'A'
def_i = ''
def_mpi_p = 128

# ----- Definite maximum probe time (if est_sim_time > max_probe_time,
#       disable probing)
max_probe_time = 80

# ----- Add current directory to system path ---
cur_dir = os.getcwd()


# ----- Parse arguments -----
parser = argparse.ArgumentParser(description='Script for running Spaun.')

parser.add_argument(
    '-d', type=int, default=def_dim,
    help='Number of dimensions to use for the semantic pointers.')
parser.add_argument(
    '--modules', type=str, default=None,
    help='A string of characters that determine what Spaun modules to ' +
         'include when building Spaun: \n' +
         'S: Stimulus and monitor modules\n' +
         'V: Vision module\n' +
         'P: Production system module\n' +
         'R: Reward system module\n' +
         'E: Encoding system module\n' +
         'W: Working memory module\n' +
         'T: Transformation system module\n' +
         'D: Decoding system module\n' +
         'M: Motor system module\n' +
         'I: Instruction processing module\n' +
         'E.g. For all modules, provide "SVPREWTDMI". Note: Provide a "-" ' +
         'as the first character to exclude all modules listed. E.g. To ' +
         'exclude instruction processing module, provide "-I". ')

parser.add_argument(
    '-t', type=float, default=-1,
    help=('Simulation run time in seconds. If undefined, will be estimated' +
          ' from the stimulus sequence.'))
parser.add_argument(
    '-n', type=int, default=1,
    help='Number of batches to run (each batch is a new model).')

parser.add_argument(
    '-s', type=str, default=def_seq,
    help='Stimulus sequence. Use digits to use canonical digits, prepend a ' +
         '"#" to a digit to use handwritten digits, a "[" for the open ' +
         'bracket, a "]" for the close bracket, and a "X" for each expected ' +
         'motor response. e.g. A3[1234]?XXXX or A0[#1]?X')
# Stimulus formats:
# Special characters - A [ ] ?
# To denote Spaun stereotypical numbers: 0 1 2 3 4 5 6 7 8 9
# To denote spaces for possible answers: X
# To denote specific image classes: #0 or #100, (either a # or non-digit will
#                                                partition numbers)
# To denote a image chosen using an array index: <1000>
# To denote random numbers chosen without replacement: N
# To denote random numbers chosen with replacement: R
# To denote 'reverse' option for memory task: B
# To denote matched random digits (with replacement): a - z (lowercase char)
# To denote forced blanks: .
# To denote changes in given instructions (see below): %INSTR_STR%
# Note:
#     Stimulus string can be duplicated using the curly braces in the format:
#     {<STIM_STR>:<DUPLICATION AMOUNT>}, e.g.,
#     {A3[RRR]?XXX:10}
parser.add_argument(
    '-i', type=str, default=def_i,
    help='Instructions event sequence. Use the following format to provide ' +
         'customized instructions to spaun (which can then be put into the ' +
         'stimulus string using %%INSTR_KEYN+INSTR_KEYM%%": ' +
         '"INSTR_KEY: ANTECEDENT_SP_STR, CONSEQUENCE_SP_STR; ..."' +
         'e.g. "I1: TASK*INSTR + VIS*ONE, TRFM*POS1*THR", and the stimulus ' +
         'string: "%%I1+I2%%A0[0]?XX"')
# Note: For sequential position instructions, instruction must be encoded with
#       POS sp. E.g. I1: POS1+VIS*ONE, TASK*C
parser.add_argument(
    '--stim_preset', type=str, default='',
    help='Stimulus (stimulus sequence and instruction sequence pairing) to ' +
         'use for Spaun stimulus. Overrides -s and -i command line options ' +
         'if they are provided.')

parser.add_argument(
    '-b', type=str, default='ref',
    help='Backend to use for Spaun. One of ["ref", "ocl", "mpi", "spinn"]')
parser.add_argument(
    '--data_dir', type=str, default=os.path.join(cur_dir, 'data'),
    help='Directory to store output data.')
parser.add_argument(
    '--noprobes', action='store_true',
    help='Supply to disable probes.')
parser.add_argument(
    '--probeio', action='store_true',
    help='Supply to generate probe data for spaun inputs and outputs.' +
         '(recorded in a separate probe data file)')
parser.add_argument(
    '--seed', type=int, default=-1,
    help='Random seed to use.')
parser.add_argument(
    '--showgrph', action='store_true',
    help='Supply to show graphing of probe data.')
parser.add_argument(
    '--showanim', action='store_true',
    help='Supply to show animation of probe data.')
parser.add_argument(
    '--showiofig', action='store_true',
    help='Supply to show Spaun input/output figure.')
parser.add_argument(
    '--tag', type=str, default="",
    help='Tag string to apply to probe data file name.')
parser.add_argument(
    '--enable_cache', action='store_true',
    help='Supply to use nengo caching system when building the nengo model.')

parser.add_argument(
    '--ocl', action='store_true',
    help='Supply to use the OpenCL backend (will override -b).')
parser.add_argument(
    '--ocl_platform', type=int, default=-1,
    help=('OCL Only: List index of the OpenCL platform to use. OpenCL ' +
          ' backend can be listed using "pyopencl.get_platforms()"'))
parser.add_argument(
    '--ocl_device', type=int, default=-1,
    help=('OCL Only: List index of the device on the OpenCL platform to use.' +
          ' OpenCL devices can be listed using ' +
          '"pyopencl.get_platforms()[X].get_devices()" where X is the index ' +
          'of the plaform to use.'))
parser.add_argument(
    '--ocl_profile', action='store_true',
    help='Supply to use NengoOCL profiler.')

parser.add_argument(
    '--mpi', action='store_true',
    help='Supply to use the MPI backend (will override -b).')
parser.add_argument(
    '--mpi_save', type=str, default='spaun.net',
    help=('MPI Only: Filename to use to write the generated Spaun network ' +
          'to. Defaults to "spaun.net". *Note: Final filename includes ' +
          'neuron type, dimensionality, and stimulus information.'))
parser.add_argument(
    '--mpi_p', type=int, default=def_mpi_p,
    help='MPI Only: Number of processors to use.')
parser.add_argument(
    '--mpi_p_auto', action='store_true',
    help='MPI Only: Use the automatic partitioner')
parser.add_argument(
    '--mpi_compress_save', action='store_true',
    help='Supply to compress the saved net file with gzip.')

parser.add_argument(
    '--spinn', action='store_true',
    help='Supply to use the SpiNNaker backend (will override -b).')

parser.add_argument(
    '--nengo_gui', action='store_true',
    help='Supply to use the nengo_viz vizualizer to run Spaun.')

parser.add_argument(
    '--config', type=str, nargs='*',
    help="Use to set the various parameters in Spaun's configuration. Takes" +
         " arguments in list format. Each argument should be in the format" +
         " ARG_NAME=ARG_VALUE. " +
         "\nE.g. --config sim_dt=0.002 mb_gate_scale=0.8 " +
         "\"raw_seq_str='A1[123]?XX'\"" +
         "\nNOTE: Will override all other options that set configuration" +
         " options (i.e. --seed, --d, --s)" +
         '\nNOTE: Use quotes (") to encapsulate strings if you encounter' +
         ' problems.')
parser.add_argument(
    '--config_presets', type=str, nargs='*',
    help="Use to provide preset configuration options (which can be " +
         "individually provided using --config). Appends to list of " +
         "configuration options provided through --config.")

parser.add_argument(
    '--debug', action='store_true',
    help='Supply to output debug stuff.')

args = parser.parse_args()