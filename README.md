# frances

## 1. Extracting automatically EB_Articles with defoe

We have created a [new defoe query for extracting automatically articles](https://github.com/francesNLP/defoe/blob/master/defoe/nlsArticles/queries/write_articles_pages_df_yaml.py) from the EB. The articles are stored per edition in YAML files.  

Here we have the command for running this query for extracting the articles of the first edition, assuming that we are located in the [defoe](https://github.com/francesNLP/defoe) directory. 

```
spark-submit --py-files defoe.zip defoe/run_query.py nls_first_edition.txt nlsArticles defoe.nlsArticles.queries.write_articles_pages_df_yaml queries/write_to_yml.yml -r frances/ results_NLS/results_eb_1_edition] -n 34 
```

Note that for running this query you need configuration file for specifying the operating system and the defoe path for the *long_s fix*:
- [configuration_file](https://github.com/francesNLP/defoe/blob/master/queries/write_to_yml.yml)

We have stored these data stored in [NLS_EB/results_NLS](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)/results_eb_<1|2|3|4>_edition.

We have **8 EB editions**, meaning that we have 8 extracted YAML files in total!! 

## 2. EB_Articles metadata 

Each YAML file has a row per article found within a page ([Example](https://github.com/francesNLP/frances/blob/main/NLS_EB/results_NLS/results_eb_1_edition)), with the following columns (being the most important **term** , **definition** and **type_page**):
 
 - title: title of the book (e.g. Encyclopaedia Britannica)
 - edition: edition of the book (e.g Eighth edition, Volume 2, A-Anatomy)
 - year: year of publication/edition (e.g. 1853)
 - place: place (e.g. Edinburgh)      
 - archive_filename: directory path of the book (e.g. /home/rosa_filgueira_vicente/datasets/single_EB/193322698/)     
 - source_text_filename: directory Path of the page (e.g. alto/193403113.34.xml)
 - text_unit: unit that represent each ALTO XML. These could be Page or Issue. 
 - text_unit_id: id of the page (e.g. Page704)
 - num_text_unit: number of pages (e.g. 904)
 - type_archive: type of archive. Thse could be book or newspapers. 
 - model: defoe model used for ingesting this dataset (nlsArticles)
 - type_page: the page classification that has been done by defoe. These could be Topic, Articles, Mix or Full Page. 
 - header: the header of the page (e.g. AMERICA)
 - **term**: term that is going to be described (e.g. AMERICA)
 - **definition**: words describing an article / topic/ full page: ( e.g. “AMERICA. being inhabited. The Aleutian ….”)
 - num_articles: number of articles per page. In case a page has been classified as Topic or FullPage, the number of articles is 1.
 - num_page_words: number of words per page (e.g. 1373)
 - num_article_words: number of words of an article (e.g. 1362)
 - **type_page**: Type of Page. 
 
We have detected two types of articles with two different patterns at “page” level:
  - **Short articles** (named as **articles**): Usually presented by a TERM in the main text in uppercase,  followed by a “,”  (e.g. ALARM, ) and then a DESCRIPTION of the TERM (similar to an entry in a dictionary). This description normally is one or two paragraphs, but of course there are exceptions.  	
	- Term: ALARM
	- Definition: in the Military Art, denotes either the apprehension of being suddenly attacked, or the notice thereof signified by firing a cannon, firelock, or the like. False alarms are frequently made use of to harass the enemy, by keeping them constantly under arms. , ….
 
- **Long articles** (named as **topics**): In this is the case, the Encyclopaedia introduces a TERM in the header of a page (which is not the case for the short articles), and then it normally uses several pages to describe that topic (and very often it uses a combination of text, pictures, tables, etc.). For example, the “topic” AMERICA goes from page 677 to 724 (47 pages!)


We have also detected that some pages (e.g. Preface, FrontPage, List of Authors) do not contain articles nor topics. We classify those pages as "Full_Page". And we also have noticed that there are some pages that have a "Mix" of articles and topics - we classify those pages as "Mix".

Therefore a page can be classified (this information is stored in **type_page**) as:
 - Article: If it has several short articles
 - Topic: If it has a topic
 - Mix: If it has a mix of Articles and Topics
 - Full_Page: If it hasnt have Articles nor Topics. 

 
Important: **Topic** is just the way we named the *long articles* that expands more than a page. It does not refer to “NLP topic”.


## 3. PostProcessing EB_Articles 

We have realised that those articles/topics need additional postprocess treatments before peforming futher analyses with them. For example, we need to merge articles and topics that are split across pages. We have also noticed that some pages have wrongly been classified as "Topic", since they should be classified as articles. And the first pages very often get confused as topics or articles - they should classified as "Full_Page". 

Therefore, we have created [Merging_EB_Terms.ipynb](https://github.com/francesNLP/frances/blob/main/NLS_EB/Merging_EB_Terms.ipynb), a notebook that cleans each of the files obtained with defoe (applying different cleaning treatments). And it creates a new "clean" version of each them: [NLS_EB/results_NLS](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)/results_eb_<1|2|3|4...>edition_updated. 

Here we have an [example](https://github.com/francesNLP/frances/blob/main/NLS_EB/results_NLS/results_eb_1_edition_updated) of the results of the 1st edition cleaned. 

## 4. NEW EB_Articles Clean Metadata

Furthermore, this notebook also re-arranges the updated information (and drops some metada) to create a **NEW dataframe per file/edition**, with the following **METADATA/COLUMNS/PROPERTIES**:

	- term:                 Article/Topic name 
	- definition:           Definition of the article/topic
	- edition_num:          1,2,3,4,5,6,7,8
	- header:               Header of the page's article/topic                                  
	- num_article_words:    Number of words per article/topic
	- place:                Place where the volume was edited (e.g. Edinburgh)                                    
	- related_terms:        Related articles/topics (e.g. see X article)  
	- source_text_file:     File Path of the XML file from which the article/topic belongs                             
	- term_id_in_page:      Number of article/topic in the page     
	- start_page:           Number page in which the article/topic starts 
	- end_page:             Number page in which the article/topic ends 
	- title:                Title of the Volume
	- type_article:         Type of Page [Full Page| Topic| Mix | Article]                                       
	- year:                 Year of the Volume
	- volume:               Volume (e.g. 1)
	- letters:              Leters of the volume (e.g. A-B)
	
We have a row per TERM. Note, that a TERM can appear several times per edition. That is the case when we have several definitions per term.

``` EXAMPLE: ABACUS
ABACUS - Definition: a table strewed over with dust or sand, upon which the ancient mathematicians drew their figures, It also signified a cupboard, or buffet.
---
ABACUS - Definition: in architeflure, signifies the superior part or member of the capital of a column, and serves as a kind of crowning to both. It was originally intended to represent a square tile covering a basket. The form of the abacus is not the same in all orders: in the Tuscan, Doric, and Ionic, it‘is generally square; but in the Corinthian and Compofite, its four sides are arched ir Avards, and embellilhed in the middle withornament, as a rose or other flower, Scammozzi uses abacus for a concave moulding on the capital of the Tuscan pedefial; and Palladio calls the plinth above the echinus, or boultin, in the Tufean and Doric orders, by the same name. See plate I. fig. i. and
---
ABACUS - Definition: is also the name of an ancient instrument for facilitating operations in arithmetic. It is vadoully contrived. That chiefly used in Europe is made by drawing any number of parallel lines at the di(lance of two diameters of one of the counters used in the calculation. A counter placed on.the lowed line, signifies r; on the sd, 10; on the 3d, 100; on the 4th, 1000, &c. In the intermediate spaces, the same counters are eflimated at one Jialf of the value of the line immediately superior, viz. between the id and 2d, 5; between the 2d and 3d, 50, &c. See plate I. fig. 2. A B, where the same number, 1768 for example, is represented under both by different dispositions of the counters.
---
ABACUS - Definition: logijlicus, a right-angled triangle, whose sides forming the right angle contain the numbers from 1 to 60, and its area the fafta of every two of the numbers perpendicularly opposite. This is also called a canon Jk^&cus Pythagvricus, the multiplication-table, or any table of numbers that facilitates operations in arith-
---
```
**THESE METADATA/COLUMNS/PROPERTIES ARE THE ONES THAT WE ARE GOING TO USE FROM NOW ON**

**VERY IMPORTANT**
These dataframes are stored as JSON files (using orient="index") in [NLS_EB/results_NLS/](https://github.com/francesNLP/frances/tree/main/NLS_EB/results_NLS)results_eb_[1|2|3|4 ...]edition<1|2|3|4...>_postprocess_dataframe. [Example](https://github.com/francesNLP/frances/blob/main/NLS_EB/results_NLS/results_eb_1_edition_postprocess_dataframe). See bellow the comand that we used for storing the dataframe corresponding to the 1st Edition. 

```
df.to_json(r'./results_NLS/results_eb_1_edition_postprocess_dataframe', orient="index") 
```

## 5. Questions

Here a list of questions that we want to ask to these data (using the EB_Articles Clean Metadata):

(Remember, a term can have more than one definition per edition)

- Give me all the volumes that we have per edition
- Given an edition, give me the years that each volume has been published.
- Given an edition and a volume, give me all the terms
- Given an edition, give me all the terms

- Given a term, give me all editions and volumes that it appears. 
- Given a term, give me all the definitions that we have per edition. 
- Give the terms that only appear in one edition.
- Give the terms that appears in all editions. 
- Given an edition, tell me the terms for which we have more definitions

- Search definitions for a given term and edition. 

- Given a term and edition, tell me which terms (based on "related_terms") are related with it. 
-  Work in progress: [Knowledge_Graph](https://github.com/francesNLP/frances/blob/main/NLS_EB/EB_Dataframe_KnowledgeGraph.ipynb)
  -  ![Architecture_KG](https://user-images.githubusercontent.com/6940078/136817688-a62c9117-0579-4faa-b4f8-2598a1fb8a43.png)

- Given a term, see how the definition(s) have changed across editions. 

(Additionally)

- Generic data explorations with dataframes
  - Work in progress: [DataFrame_Exploration](https://github.com/francesNLP/frances/blob/main/NLS_EB/EB_Dataframe_Explorations.ipynb)




## 6. Architecture Proposed


<img width="1194" alt="FrancesArchitecture" src="https://user-images.githubusercontent.com/6940078/134651770-deafc0a8-0dab-4144-a933-151db978e0ad.png">


## 7. ElasticSearch

Terminal 1:

1. Download elasticsearch-7.11.2.
2. Decompress the elastic search-7.11.2 folder
3. cd elasticsearch-7.11.2/
4. ./bin/elasticsearch 
           (Let it running - do not close this terminal)

Terminal  2) 
1. python create_load_indexes.py   —> It creates an ES index (nlsArticles) and loads the json files into Elastic Search. 
2. curl 'localhost:9200/_cat/indices?v’  —> It checks that the index and data have been created correctly in Elastic Search
3. python train_model_es.py.  —> Train a doc2vec model using the data previously loaded to Elastic Search 
4. python test_load_search_model_es.py. —> Test the doc2vec model and retrieve the most similar documents (of a given text) from Elastic Search.  
