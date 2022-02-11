import nengo

from ...._networks import AssociativeMemory as AM


def LIFVisionClassifier(vis_data, concept_sps, net=None, **args):
    vis_args = dict(args)
    n_neurons_vis = vis_args.get('n_neurons', 50)
    if net is None:
        net = nengo.Network(label="LIF Vision Classifier")

    with net:
        am_net = AM(vis_data.sps, concept_sps, threshold=vis_data.am_threshold,
                    n_neurons=n_neurons_vis, inhibitable=True)

        am_net.add_wta_network(3.5)
        am_net.add_cleanup_output(replace_output=True, n_neurons=n_neurons_vis)

        # --- Set up input and outputs to the LIF vision system
        net.input = am_net.input
        net.inhibit = am_net.inhibit
        net.output = am_net.cleaned_output
        net.output_utilities = am_net.cleaned_output_utilities

    return net
