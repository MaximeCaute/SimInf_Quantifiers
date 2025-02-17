export PYTHONPATH=$PYTHONPATH:./

FILE=metagrammar.json

python bin/individual_quantifiers/generate.py --setup experiment_setups/$FILE
python bin/individual_quantifiers/measure_expression_complexity.py --setup experiment_setups/$FILE
python bin/individual_quantifiers/measure_expression_monotonicity.py --setup experiment_setups/$FILE
python bin/individual_quantifiers/measure_expression_conservativity.py --setup experiment_setups/$FILE

python bin/individual_quantifiers/generate_natural_expressions.py --setup experiment_setups/$FILE

python bin/languages/generate_evolutionary.py --setup=experiment_setups/$FILE --lang_size 10 --sample_size 2000 --generations 30 --max_mutations 3

# generate languages with varying degrees of naturalness
python bin/languages/sample_indexset_degrees.py --setup experiment_setups/$FILE --indices natural --sample 8000

# measure complexity and informativeness
python bin/languages/measure.py --setup experiment_setups/$FILE --name natural_gradual

# measure monotonicity and conservativity
python bin/languages/measure_monotonicity.py --setup experiment_setups/$FILE --name natural_gradual
python bin/languages/measure_conservativity.py --setup experiment_setups/$FILE --name natural_gradual

# generate "random" languages
#python bin/languages/languages.py --setup experiment_setups/$FILE --sample 2000

# measure complexity and informativeness
#python bin/languages/measure.py --setup experiment_setups/$FILE --name random

# measure monotonicity and conservativity
#python bin/languages/measure_monotonicity.py --setup experiment_setups/$FILE --name random
#python bin/languages/measure_conservativity.py --setup experiment_setups/$FILE --name random

# analysis
python bin/languages/analysis/estimate_pareto.py --setup experiment_setups/$FILE
python bin/languages/analysis/analyze.py --setup experiment_setups/$FILE
