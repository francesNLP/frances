set -x 

###### Cleaning and Creating the UPDATED TXT FILES and DATAFRAMES #####
python postprocess_eb.py results_eb_1_edition 
python postprocess_eb.py results_eb_2_edition 
python postprocess_eb.py results_eb_3_edition 
python postprocess_eb.py results_eb_4_edition 
python postprocess_eb.py results_eb_5_edition 
python postprocess_eb.py results_eb_6_edition 
python postprocess_eb.py results_eb_7_edition 
python postprocess_eb.py results_eb_8_edition 
python postprocess_eb.py results_eb_4_5_6_suplement 

#### Process METADATA
python process_metadata_eb.py

