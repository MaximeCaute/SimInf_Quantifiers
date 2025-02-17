import argparse
from pathos.pools import ProcessPool
from siminf import generator
from siminf import analysisutil
from siminf import experiment_setups
from siminf import fileutil
from siminf.fileutil import FileUtil
from siminf.languages import language_loader
from siminf.languages.informativeness_measurer import SimMaxInformativenessMeasurer, InformativenessMeasurer, BrochhagenInformativenessMeasurer

def main(args):
    setup = experiment_setups.parse(args.setup)
    dirname = fileutil.run_dir(args.dest_dir, setup.name, args.max_quantifier_length, args.model_size, args.name)
    file_util = FileUtil(dirname)

    languages = language_loader.load_languages(file_util)

    universe = generator.generate_simplified_models(args.model_size)

    if args.inf_strat == 'exact':
        informativeness_measurer = InformativenessMeasurer(len(universe))
    elif args.inf_strat == 'simmax':
        informativeness_measurer = SimMaxInformativenessMeasurer(universe)
    elif args.inf_strat == "brochhagen":
        informativeness_measurer = BrochhagenInformativenessMeasurer(universe)
    else:
        raise ValueError('{0} is not a valid informativeness strategy.'.format(args.inf_strat))

    with ProcessPool(nodes=args.processes) as pool:
        informativeness = pool.map(informativeness_measurer, languages)

    file_util.dump_dill(informativeness, 'informativeness_{0}.dill'.format(args.inf_strat))

    print("measure_informativeness.py finished.");


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze")
    #common arguments
    parser.add_argument('--setup', help='Path to the setup json file.', required=True)
    parser.add_argument('--max_quantifier_length', type=int, required=True)
    parser.add_argument('--model_size', type=int, required=True)
    parser.add_argument('--dest_dir', default='results')
    parser.add_argument('--processes', default=4, type=int)
    parser.add_argument('--name', default='run_0')
    #additional arguments
    parser.add_argument('--inf_strat', required=True)
    #parse
    args = parser.parse_args()
    main(args)
