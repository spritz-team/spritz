# spritz framework


### Steps
1. get_data.py: get all data needed for a year / era
2. fileset.py: get the list of all files (replicas and nevents) for each dataset defined in `data/{year}/samples/active_samples.py` (user has to write this file)
3. create a config directory with a config.py and a script_worker.py
3. run chunks.py to create all the chunks and their metadata
4. run batch.py to submit on condor
5. check_errors.py to check which job failed (should resubmit manually)
6. merge_results.py will merge all the results into a pickle file (removing all metadata and old errors)
7. post_process.py will take the pickle file and output a root file with simple directories and TH1s 
8. plot.py
9. make_cards.py
