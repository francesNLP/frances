
## Generating the dataframes from defoe extracted data
'''
>> cd defoe_postprocessing
'''
1. python Merging_EB_Terms_1stEd.py ---> results_eb_1_edition_dataframe
2. python Merging_EB_Terms_2to8Eds.py --> results_eb_<2|8>_edition_dataframe
3. python Metadata_EB.py --> metadata_eb_dataframe             
4. python FINAL_DATAFRAME_EB.py --> final_eb_<1|8>_dataframe.

## Creating the KG from the final dataframes
5. python Dataframe2RDF.py --> total_eb.ttl / we will store it in APACHE FUSEKI

## Generating TXT files from querying SPARQL (KG)
'''
>> cd ..
>> cd transformers
'''
6. python EB_Create_Articles_TextFiles.py --> terms_definitions.txt ; terms_uris.txt ; terms_details.txt
7. python EB_Create_Topics_TextFiles.py --> topics_definitions.txt ; topics_uris.txt ; topics_details.txt ; indices_<1|8>.txt

## Applying Transformers using the TXT FILES
8. python EB_Sumarizing.py --> topics_summary_<1|8>.txt / we wont use them in the web-app
9. python EB_Create_New_Docs.py --> topics_summaries_total.txt /we wont use it in the web-app
10. python EB_Fixing_Summary_Documents.py -> terms_definitions_final.txt
11. python EB_Embeddings.py --> embeddings_mpnet.npy
12. python EB_Similar.py ---> paraphrases_mpnet.txt , paraphrases_index_first.txt, paraphrases_index_second.txt
13. python EB_TopicModelling.py ---> BerTopic_Model_mpnet ; lda_topics_mpnet.txt (lda_topic per term) ; lda_t_names_mpnet.txt (all the names of lda_topics) ; lda_topics_names_mpnet.txt (lda_topic per term)
14. python EB_Sentiment_Analyses.py --> terms_sentiments.txt
15. python EB_Correct_OCR_BERT_ELMO.py --> clean_terms_definitions_final.txt

NOTE about LDA topics
'''
>>> lda_topics_mpnet[-1] : Just the number of the lda topic per term
5
>>> lda_topics_names_mpnet[-1]: The names of the lda topic per term
'5_empty definition_definition for_empty_definition'

>>lda_t_names_mpnet[ .... '3909_sometimes we_nature_nature sometimes_by nature', '3480_miracle_of nature_deviation_anointing his']: All the names of all possible lda_topics
'''
