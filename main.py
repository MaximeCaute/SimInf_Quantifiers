import numpy as np
import matplotlib.pyplot as plt
import json
import Generator
import Parser
import Measurer

# Parameters
model_size = 7
designated_quantifier_lengths = [2,3,4,5,6,7,8]
generate_new_quantifiers = True

universe = Generator.generate_models(model_size)

# Read lexicalized quantifiers from data file
with open('EnglishQuantifiers.json') as json_file:
    data = json.load(json_file)

quantifier_specs = data['quantifiers']
quantifier_expressions = Parser.parse_quantifiers(quantifier_specs)

# Generate quantifiers
if generate_new_quantifiers:
    generated_quantifier_expressions = \
        Generator.generate_unique_expressions(designated_quantifier_lengths, 20, model_size, universe)

    with open('results/GeneratedQuantifiers.json', 'w') as file:
        gq_dict = {"{0}".format(i): expression.to_name_structure() for (i,expression) in enumerate(generated_quantifier_expressions)}
        json.dump({'quantifiers': gq_dict}, file, indent=4)

else:
    with open('results/GeneratedQuantifiers.json') as json_file:
        data = json.load(json_file)

    generated_quantifier_specs = data['quantifiers']
    generated_quantifier_expressions = Parser.parse_quantifiers(generated_quantifier_specs).values()

# Measure cost and complexity for non-generated quantifiers

cost = {}
complexity = {}
for name, expression in quantifier_expressions.items():
    cost[name] = Measurer.measure_communicative_cost(expression,universe)
    complexity[name] = Measurer.measure_complexity(expression)
    plt.annotate(name,(cost[name],complexity[name]))

# Measure cost and complexity for generated quantifiers
generated_cost = []
generated_complexity = []
for expression in generated_quantifier_expressions:
    generated_cost.append(Measurer.measure_communicative_cost(expression,universe))
    generated_complexity.append(Measurer.measure_complexity(expression))


# Write results
with open('./results/lexicalized_quantifiers_cost.txt', 'w') as f:
    for (name,value) in cost.items():
        f.write("{0}: {1}\n".format(name, value))

with open('./results/lexicalized_quantifiers_complexity.txt', 'w') as f:
    for (name,value) in complexity.items():
        f.write("{0}: {1}\n".format(name, value))

with open('./results/generated_quantifiers.txt', 'w') as f:
    for expression in generated_quantifier_expressions:
        f.write("{0}\n".format(expression.to_string()))

np.savetxt('./results/generated_quantifiers_cost.txt',generated_cost)
np.savetxt('./results/generated_quantifiers_complexity.txt',generated_complexity)

# Plot
plt.plot(generated_cost,generated_complexity,'o',color='grey')
plt.plot(cost.values(),complexity.values(),'o')

# for i in range(len(generated_quantifier_expressions)):
#     plt.annotate(str(i),(generated_cost[i],generated_complexity[i]))

plt.axis([0,1,0,1])
plt.show()