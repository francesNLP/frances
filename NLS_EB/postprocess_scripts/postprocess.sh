set -x 


###### Cleaning and Creaating the UPDATED TXT FILES #####
python post_process_eb.py results_eb_1_edition 
python post_process_eb.py results_eb_2_edition 
python post_process_eb.py results_eb_3_edition 
python post_process_eb.py results_eb_4_edition 
python post_process_eb.py results_eb_5_edition 
python post_process_eb.py results_eb_6_edition 
python post_process_eb.py results_eb_7_edition 
python post_process_eb.py results_eb_8_edition 
python post_process_eb.py results_eb_4_5_6_suplement 

###### Create dataframes FILES ########
python dataframe_eb.py results_eb_1_edition_update 
python dataframe_eb.py results_eb_2_edition_update
python dataframe_eb.py results_eb_3_edition_update 
python dataframe_eb.py results_eb_4_edition_update 
python dataframe_eb.py results_eb_5_edition_update 
python dataframe_eb.py results_eb_6_edition_update 
python dataframe_eb.py results_eb_7_edition_update 
python dataframe_eb.py results_eb_8_edition_update 
