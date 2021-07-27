import pandas as pd

from siminf import analysisutil

THRESHOLD = 5e-2

(args, setup, file_util) = analysisutil.init(use_base_dir=True)

data = file_util.load_pandas_csv('natural_data.csv').drop(columns = "Unnamed: 0")
languages = file_util.read_stringlist("{0}/languages.txt".format(setup.natural_name))
data["language"] = languages
print(data)

close_data = data[data["pareto_closeness"] < THRESHOLD]

# Naturalness is just to get a dataframe here, could be any column
close_data['occurrences']=close_data.groupby('language')['naturalness'].transform('count')
close_data = close_data.drop_duplicates()
print(close_data)



file_util.save_pandas_csv(close_data, "close_languages")
