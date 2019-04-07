import pandas as pd
from glob import glob
import os.path

# this will not work in the public repo
full_results_path = '../../../EntailmentData/Results/'

out_path = 'Results_Anon'

for this_csv in glob(full_results_path + '*.csv'):
    this_df = pd.read_csv(this_csv)
    diff_workers = this_df['WorkerId'].unique()
    worker2id = dict(zip(diff_workers, range(len(diff_workers))))
    this_df['WorkerId'] = this_df['WorkerId'].apply(lambda x: worker2id[x])
    basename = os.path.basename(this_csv)
    filename = os.path.splitext(basename)[0]
    this_df.to_csv(os.path.join(out_path, filename + '_anon.csv'))
