"""
This is a script to analyze languages obtained,
e.g. checking which are the closest, if they contain specific quantifiers...
"""

import pandas as pd
import re

from siminf import analysisutil


THRESHOLD = 2e-2

def replace_expressions(macro_dict, language):
    for macro in macro_dict.keys():
        for expression in macro_dict[macro]:
            language = language.replace(expression, macro)

    return language

macro_color= '\033[92m'
end_color = '\033[0m'

def color_word(word, start_color=macro_color, end_color=end_color):
    return macro_color+word+end_color

macro_dict = {
    "only" : ["subset(B,A)"],#{}, "empty(diff(A,B))"],
    "all" : ["subset(A,B)"],#{}, "empty(diff(B,A))"],
    "no" : ["=(card(intersection(A,B)),0)", 'subset(A,diff(A,B))'],#{}, "empty(intersection(A,B))"],
    "not_all" : ["not(subset(A,B))", "nonempty(diff(A,B))"],
    "some" : [">(card(intersection(A,B)),0)", "nonempty(intersection(A,B))"],
    "not_only": ["not(subset(A,B))", "nonempty(diff(B,A))"]
}
macro_dict = {color_word(key):macro_dict[key] for key in macro_dict.keys()}
################################################################################

(args, setup, file_util) = analysisutil.init(use_base_dir=True)

data = file_util.load_pandas_csv('natural_data.csv').drop(columns = "Unnamed: 0")
languages = file_util.read_stringlist("{0}/languages.txt".format(setup.natural_name))
data["language"] = languages
data["language_size"]= data["language"].apply(lambda s: len(re.split("'\S+'", s))-1)

# Naturalness is just to get a dataframe here, could be any column
data['occurrences']=data.groupby('language')['naturalness'].transform('count')
data = data.drop_duplicates()
print(data)

########################

print("# Replaced with macros!")
data["language"] = data["language"].apply(lambda l : replace_expressions(macro_dict,l))
print(data)
print(end_color)
###########################

print("# CLOSE DATA")
close_data = data[data["pareto_closeness"] < THRESHOLD]
print(close_data)
print(end_color)

file_util.save_pandas_csv(close_data, "close_languages.csv")

best_n_data = data.sort_values("pareto_closeness", ascending = True).head(12)
print("# BEST DATA")
print(best_n_data)
print(end_color)

for l in best_n_data["language"].values:
    print(l)
print(end_color)

best_n_size_2_data = data[data["language_size"] == 2]\
    .sort_values("pareto_closeness", ascending = True)\
    .head(24)
print("# BEST SIZE 2 DATA")
print(best_n_size_2_data)
print(end_color)

best_n_size_3_data = data[data["language_size"] == 3]\
    .sort_values("pareto_closeness", ascending = True)\
    .head(24)
print("# BEST SIZE 3 DATA")
print(best_n_size_3_data)
print(end_color)

print("# LANGUAGE SAMPLE: SQUARE_QUANTIFIERS")

SQUARE_QUANTIFIERS = ["some", "all", "not_all", "no"]
for i,q1 in enumerate(SQUARE_QUANTIFIERS):
    for q2 in SQUARE_QUANTIFIERS[i:]:
        if q1 == q2:
            continue
        print(data[ [   "'"+color_word(q1)+"'" in l and
                        "'"+color_word(q2)+"'" in l
                        for l in data["language"]]].iloc[0])

for q in SQUARE_QUANTIFIERS:
    print(data[ [   "'"+color_word(q)+"'" in l
                    for l in data["language"]]].iloc[0])
