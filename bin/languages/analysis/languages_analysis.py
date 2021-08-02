import pandas as pd
import re

from siminf import analysisutil


THRESHOLD = 2e-2

(args, setup, file_util) = analysisutil.init(use_base_dir=True)

data = file_util.load_pandas_csv('natural_data.csv').drop(columns = "Unnamed: 0")
languages = file_util.read_stringlist("{0}/languages.txt".format(setup.natural_name))
data["language"] = languages
data["language_size"]= data["language"].apply(lambda s: len(re.split("'\S+'", s))-1)

# Naturalness is just to get a dataframe here, could be any column
data['occurrences']=data.groupby('language')['naturalness'].transform('count')
data = data.drop_duplicates()
print(data)

close_data = data[data["pareto_closeness"] < THRESHOLD]

#close_data['occurrences']=close_data.groupby('language')['naturalness'].transform('count')
#close_data = close_data.drop_duplicates()
print("# CLOSE DATA")
print(close_data)
print("")

file_util.save_pandas_csv(close_data, "close_languages.csv")

best_n_data = data.sort_values("pareto_closeness", ascending = True).head(12)
print("# BEST DATA")
print(best_n_data)
print("")

print("# LANGUAGE SAMPLE")
print(data["language"][79437])
print("")

best_n_size_2_data = data[data["language_size"] == 2].sort_values("pareto_closeness", ascending = True).head(12)
print("# BEST SIZE 2 DATA")
print(best_n_size_2_data)
print("")

print("# LANGUAGE SAMPLE")
print(data[data["language"] == "['subset(A,B)', '>(card(intersection(A,B)),0)']"])
print("")

only = "'subset(B,A)'"
all = "'subset(A,B)'"
no = "'=(card(intersection(A,B)),0)'"
not_all = "'not(subset(A,B))'"



# large_lexicons = data[data["language_size"] == 10]
# print(large_lexicons)

# for i in range(1,11):
#     sized_languages =  data[data["language_size"] == i].iloc[0:2]
#     print(sized_languages)
#     for language in sized_languages["language"]:
#         print(language)
#     print("")
