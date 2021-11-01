#!/usr/bin/env python
# coding: utf-8

# # Merging EB terms-  NLS -  Encyclopaedia Britannica
# 

# ### Loading the necessary libraries
import yaml
import numpy as np
import collections
import string
import copy
import re
import sys
import pandas as pd
from yaml import safe_load
from pandas.io.json import json_normalize
from difflib import SequenceMatcher

from collections import Counter


def read_query_results(filename):
    with open('../results_NLS/'+filename, 'r') as f:
        query_results = safe_load(f)
    return query_results



def write_query_results(filename, results):
    with open('../results_NLS/'+filename, 'w') as f:
        documents = yaml.dump(results, f)




def sort_query_results(query_results):
    new_results={}
    for edition in query_results:
        new_results[edition]=[]
        page_list=[]
        for page_idx in range(0, len(query_results[edition])):
            page_num = query_results[edition][page_idx][0]
            if not page_list:
                page_list.append(page_num)
                new_results[edition].append(query_results[edition][page_idx])
            
            else:
                last_element=page_list[-1]
                if page_num >= last_element:
                    page_list.append(page_num)
                    new_results[edition].append(query_results[edition][page_idx])
                else:
                    ## insert the new page in page_list
                    i_dx=0
                    while page_list[i_dx] < page_num:
                        i_dx+=1
                    page_list.insert(i_dx, page_num)
                    new_results[edition].insert(i_dx,query_results[edition][page_idx])
    return new_results




def consistency_query_results(query_results):
      for i in query_results:
        for j in range(0, len(query_results[i])):
            page_num = query_results[i][j][0]
            if j < (len(query_results[i])-1):
                next_page_num = query_results[i][j+1][0]
                if page_num > next_page_num:
                    print("INCONSISTENCY for %s: %s and %s"% (i, page_num, next_page_num))


def create_dataframe(query_results):

    for edition in query_results:
        for page in query_results[edition]:
            column_list=list(page[1].keys())
            break
        break
        
    data=[]
    for edition in query_results:
        for page in query_results[edition]:
            try:
                data.append(page[1])
               
            except:
                pass
    df = pd.DataFrame(data, columns = column_list)
    #removing the columns that I dont need 
    df= df.drop(['model', 'num_page_words', 'text_unit', 'type_archive'], axis=1)
    #df= df.drop(['last_term_in_page', 'model', 'num_page_words', 'text_unit', 'type_archive'], axis=1)
    #renaming the page num
    df= df.rename(columns={"text_unit_id": "startsAt", "end_page":"endsAt",                           "type_page": "typeTerm", "edition":"editionTitle",                           "title":"volumeTitle", "related_terms":"relatedTerms",                           "source_text_file": "altoXML", "num_articles": "numberOfTerms", "num_text_unit": "numberOfPages",                            "num_article_words":"numberOfWords", "term_id_in_page":"positionPage"})
     
    #removing 'Page' from the string
    df["startsAt"] = df["startsAt"].str.replace("Page", "", regex=True)
    df["startsAt"] = df["startsAt"].astype(int)
    df["endsAt"] = df["endsAt"].astype(int)
   
    
    df['term'] = df["term"].str.replace("_def", "",  regex=True)
    df['term']= df["term"].str.replace('[^a-zA-Z0-9]', '',  regex=True)
    
    #mask=df["term"].str.isalpha()
    #df_new=df.loc[mask]
    
    
    
    df['term'] = df['term'].str.upper()
    
    
    df["volumeNum"] = 0
    df["letters"] = ""
    df["part"] = 0
    
    
    mask = df["editionTitle"].str.contains('Volume')
    for i in range(0, len (mask)):
     
        if mask[i]:
            tmp=df.loc[i,'editionTitle'].split("Volume ")[1].split(",")
            if len(tmp)>=1:
                volume= tmp[0]
                letters = tmp[-1].replace(" ","")
                part_tmp = volume.split("Part ")
                if len(part_tmp)>1:
                    volume=part_tmp[0]
                    part = part_tmp[1]
    
                    try:
                        part = int(part)
                    except:
                        if "I" in part:
                            part = 1
                else:
                    part=0

                volume = int(volume)
                df.loc[i, "letters"] = letters
                df.loc[i,"part"] = part
                df.loc[i ,"volumeNum"] = volume
    
    df["editionNum"] = "0"
    list_editions={"1":["first", "First"], "2":["second", "Second"],"3":["third", "Third"],
                   "4":["fourth", "Fourth"], "5":["fifth","Fifth"], "6":["sixth","Sixth"], 
                   "7":["seventh", "Seventh"], "8":["eighth", "Eighth"]}
    
    for ed in list_editions:
        for ed_versions in list_editions[ed]:
            mask = df["editionTitle"].str.contains(ed_versions)
            df.loc[mask, 'editionNum'] = ed
            
            
    df['editionNum']=df["editionNum"].astype(int)    
    df["supplementTitle"]=""
    df["supplementsTo"]=""
    
    mask= df["volumeTitle"].str.contains("Supplement")
    for i in range(0, len (mask)):
        if mask[i]:
            df.loc[i, 'supplementTitle'] = df.loc[i, 'volumeTitle']
            df.loc[i, 'volumeTitle'] = df.loc[i, 'volumeTitle'] + ","+df.loc[i, 'editionTitle']
            title= df.loc[i, 'supplementTitle']
            related_editions=[]
            for ed in list_editions:
                for ed_versions in list_editions[ed]:
                    if ed_versions in title:
                        related_editions.append(ed)
                        
            df.loc[i, "supplementsTo"]=','.join(related_editions)
            
    df["supplementsTo"] = df.supplementsTo.str.split(",").tolist()
    a=df["archive_filename"].str.split("/").str[-1]
    df['altoXML']= a+ "/" + df["altoXML"]   
    df= df.drop(['archive_filename'], axis=1)
   
    df = df[["term", "definition", "relatedTerms", "header", "startsAt", "endsAt", "numberOfTerms","numberOfWords", "numberOfPages",              "positionPage", "typeTerm", "editionTitle", "editionNum", "supplementTitle", "supplementsTo",              "year", "place", "volumeTitle", "volumeNum", "letters", "part", "altoXML"]]
    
    df = df[df['term'] != '']
    mask=df["term"].str.isalpha()
    df=df.loc[mask] 
    
    ### NEW DECISION: Move Mix Articles as Article
    mask = df["typeTerm"].str.contains("Mix")
    df.loc[mask, 'typeTerm'] = "Article"
    ###########
    return df



def similar(a, b):
    a=a.lower()
    b=b.lower()
    return SequenceMatcher(None, a, b).ratio()


def most_frequent_simple(List):
    ### removed '' and ' ' keys
    if '' in List: 
        List.remove('')
    if len(List) > 1:
        a= max(set(List), key = List.count)
        return a
    else:
        return ''



def most_frequent(words_list, prev_car=None):
    
    result=''
    if '' in words_list: 
        words_list.remove('')
        
    for i in words_list:
        if len(i)<=2:
            words_list.remove(i)
        
    if prev_car=="":
        prev_car= None
        
    if len(words_list) > 1:
        
        c = [item for item in Counter(words_list).most_common(2)]
        
        if len(c) > 1:
            if len(c[0][0]) < 1 and len(c[1][0])>=1:
                result= c[1][0]
        
            elif len(c[0][0]) >= 1 and len(c[1][0])<1:
                result= c[0][0]

            elif len(c[0][0]) < 1 and len(c[1][0])<1:
                result=''
            
            elif c[0][1] == c[1][1]:
        
                similar_count={}
                similar_count[c[0][0]]=0
                similar_count[c[1][0]]=0
        
                for i in words_list:
                    if i != c[0][0] and i!=c[1][0]:
                        
                
                        if similar(i, c[0][0]) > similar(i, c[1][0]):
                            similar_count[c[0][0]]+=1
                    
                        elif similar(i, c[0][0]) < similar(i, c[1][0]):
                            similar_count[c[1][0]]+=1
                 
                if  similar_count[c[0][0]] > similar_count[c[1][0]]:
                    result= c[0][0]
                
                elif similar_count[c[0][0]] < similar_count[c[1][0]]:
        
                    result= c[1][0]
            
            
                if prev_car:
                    if c[0][0][0] == prev_car:
                    
                        result= c[0][0]
                        
                    elif c[1][0][0] == prev_car:
                     
                        result= c[1][0]
                    
                    elif c[0][0][0]> prev_car:
                        result= c[0][0]
                    
                    else:
                        result= c[1][0]
                     
                
                else:
                    result= c[0][0]
            else:
                 result= c[0][0]
        else:
            result= c[0][0]
    return result



def check_string(term, List):
    flag = 0
    for element in List:
        if term in element:
            flag = 1
            break
    if flag == 1:
        return True
    else:
        return False



def clean_topics_terms(term):
    table = str.maketrans('', '', string.ascii_lowercase)
    return term.translate(table)




def create_dataframe_from_file(filename):
    with open('../results_NLS/'+filename, 'r') as f:
        query_results = safe_load(f)
    
    df = create_dataframe(query_results)
    return df



def prune_json(json_dict):
    """
    Method that given a JSON object, removes all its empty fields.
    This method simplifies the resultant JSON.
    :param json_dict input JSON file to prune
    :return JSON file removing empty values
    """
    final_dict = {}
    if not (isinstance(json_dict, dict)):
        # Ensure the element provided is a dict
        return json_dict
    else:
        for a, b in json_dict.items():
            if b or isinstance(b, bool):
                if isinstance(b, dict):
                    aux_dict = prune_json(b)
                    if aux_dict:  # Remove empty dicts
                        final_dict[a] = aux_dict
                elif isinstance(b, list):
                    aux_list = list(filter(None, [prune_json(i) for i in b]))
                    if len(aux_list) > 0:  # Remove empty lists
                        final_dict[a] = aux_list
                else:
                    final_dict[a] = b
    return final_dict



def delete_entries(query_results_updated, eliminate_pages):
    new_results={}
    for edition in query_results_updated:
        new_results[edition]=[]
        for page_idx in range(0, len(query_results_updated[edition])):
            if page_idx not in eliminate_pages[edition]:
                new_results[edition].append(query_results_updated[edition][page_idx])
    return new_results



def deleting_adding_entries(query_results_up, eliminate_pages, create_entries):
    new_results={}
    flag = 1
    for edition in query_results_up:
        new_results[edition]=[]
        for page_idx in range(0, len(query_results_up[edition])):
            if page_idx not in eliminate_pages[edition]:
                new_results[edition].append(query_results_up[edition][page_idx])
            else:
                for new_pages in create_entries[edition][page_idx]:
                    new_results[edition].append(new_pages)
            
        
    return new_results      



def related_terms_info(related_terms):
    related_data=[]
    for elem in related_terms:
        if elem.isupper() or "." in elem or "," in elem:
            elem=elem.split(".")[0]
            term=elem.split(",")[0]
            if len(term)>2 and term[0].isupper() :
                m = re.search('^([0-9]+)|([IVXLCM]+)\\.?$', term)
                if m is None:
                    term_up = term.upper()
                    if term_up !="FIG" and term_up !="NUMBER" and term_up!="EXAMPLE" and term_up!="PLATE" and term_up!="FIGURE":
                        #related_data.append(term_up) and term_up!="EXAMPLE" and term_up!="PLATE" and term_up!="FIGURE"
                        related_data.append(term_up.strip())
    return related_data



def page2full_pages(element):

    
    term = element["term"]
    header = element["header"]
    type_page = element["type_page"]
    definition = element["definition"]
  
   
    if (type_page == "Empty") and len(definition)<100 and element["num_articles"]<2:
        type_page ="FullPage"
    
    elif ("PREFACE" in term) or ("PREFACE" in header):
        term = "PREFACE"
        header = "PREFACE"
        type_page="FullPage"
       
    
    elif ("PLATE" in term) or ("PLARF" in term) or ("ELATE" in term) or ("TLAFE" in term):
        header = "Plate"
        term = "Plate"
        type_page = "FullPage"
      
        
    elif ("PLATE" in header) or ("PLAFR" in header) or ("ELATE" in header) or ("TLAFE" in header):
        header = "Plate"
        term = "Plate"
        type_page = "FullPage"
      
        
    elif ("ARTSANDSCI" in term) or ("ARTSANDSCI" in header):
        header = "FrontPage"
        term = "FrontPage"
        type_page="FullPage"
        

        
    elif "ERRATA" in term or ("ERRATA" in header):
        header = "ERRATA"
        term = "ERRATA"
        type_page="FullPage"
       
        
   
    elif (" LISTOFAUTHORSC" in term) or ("LISTOFAUTHORS" in term) or ("LISTOFAUTHORSC" in term) or ("LISTAUTHORS" in term):
        header = "AuthorList"
        term = "AuthorList"
        type_page="FullPage"
        
        
    elif (" LISTOFAUTHORSC" in header) or ("LISTOFAUTHORS" in header) or ("LISTOFAUTHORSC" in header) or ("LISTAUTHORS" in header):
        header = "AuthorList"
        term = "AuthorList"
        type_page="FullPage"
       
        
    
    element["term"] = term
    element["header"] = header
    element["type_page"] = type_page
   
    return element



def fixing_fullPages(query_results):
    parts_string=["Part", "Fart", "Parc", "CPart","P", "PI", "PII", "PIII", "P", "C", "PXXIV", "IV", "VI" "VII", "VIII", "IX", "XI"]
    create_entries={}
    eliminate_pages={}
    for edition in query_results:
        create_entries[edition]={}
        eliminate_pages[edition]=[]
        flag_p = 1
        for page_idx in range(0, len(query_results[edition])):
            element = query_results[edition][page_idx][1]
            current_page = query_results[edition][page_idx][0]
            
            if int(current_page) <= 10:
                element["type_page"] = "FullPage"
            
            elif int(current_page) > 10 and int(current_page) < 20:
                if element["type_page"]!="FullPage":
                    element = page2full_pages(element)
                    next_element= query_results[edition][page_idx+1][1]
                    
                if element["type_page"]!="FullPage" and next_element["type_page"]=="FullPage" and len(element["definition"])<50:
                    element["type_page"] = "FullPage"
                
            elif int(current_page)>=20 and element["type_page"] == "Empty" and (len(element["term"])<=5 or check_string(element["term"], parts_string)) and element["num_articles"]< 2 and len(element["definition"])<100:
                element["type_page"] = "FullPage"
            
            elif int(current_page)>=20 and element["type_page"] == "Topic" and (len(element["term"])<=5 or check_string(element["term"], parts_string)) and len(element["definition"])<100:
                element["type_page"] = "FullPage"
                
            
            
        
                
                
            
    return query_results



def fixing_articles(query_results):
    create_entries={}
    eliminate_pages={}
    parts_string=["S", "HXXA", "P", "C","", " ", "_", "-", "Part", "Fart", "Parc", "CPart","P", "PI", "PII", "PIII", "P", "C", "IV", "VI" "VII", "VIII", "IX", "XI"]
    for edition in query_results:
        create_entries[edition]={}
        eliminate_pages[edition]=[]
        flag_p = 1
        for page_idx in range(0, len(query_results[edition])):
            element = query_results[edition][page_idx][1]
            element_page = query_results[edition][page_idx][0]
            if page_idx >=1 and page_idx < len(query_results[edition])-1:
                    prev_element = query_results[edition][page_idx-1][1]
            if page_idx < len(query_results[edition])-1:
                    next_element=query_results[edition][page_idx+1][1]
            flag = 0
            
            if (element["type_page"]=="Empty" and element["num_articles"]>2):
                
                element["type_page"]="Article"
        
            
            elif (element["type_page"]=="Topic") or (element["type_page"]=="FullPage" and element_page>15) or (element["type_page"]=="Empty" and element["num_articles"]==1):
                list_terms=[]
                new_entries=[]
                definition=element["definition"]
                definition_list= definition.split(" ")
                term = element["term"].strip()
                flag = 0
                sub_elements=[]
                for word_idx in range(0, len(definition_list)):
                    word = definition_list[word_idx]
                    if ((word.isupper() and "," in word) or (word.isupper() and ";" in word)) and len(word)>3 and "See "!= definition_list[word_idx-1] and "SEE " != definition_list[word_idx-1]:
                        if "," in word:
                            sub_elements.append((word.split(",")[0],word_idx))
                        elif ";" in word:
                            sub_elements.append((word.split(";")[0],word_idx))
                        flag = 1
                
                ### rest_of_editions
                if page_idx < len(query_results[edition])-1:
                    if len(sub_elements) > 1 and next_element["type_page"]=="Article":
                        flag = 1
                        
                if page_idx >=1 and page_idx < len(query_results[edition])-1:

                    if (definition_list[1] == prev_element["definition"].split(" ")[-1]):
                        flag = 1            
                
                if flag: 
                    for elem_idx in range(0, len(sub_elements)):
                        term_id = 0
                       
                        new_element={}
                        elem=sub_elements[elem_idx]
                        new_element["term"]=elem[0].strip()
     
                        if elem_idx+1 < len(sub_elements):
                            sentence=definition_list[elem[1]+1: sub_elements[elem_idx+1][1]]
                            new_element["definition"]=' '.join(sentence)
                       
                            
                        else:
                            new_element["last_term_in_page"] = 1
                            try:
                                sentence= definition_list[elem[1]+1:][1]
                                new_element["definition"]=' '.join(sentence)
        
                            except:
                                sentence= definition_list[elem[1]:]
                                if len(sentence) > 3:
                                    new_element["definition"]=' '.join(sentence)
       
                        if "definition" in new_element: 
                            #%and len(new_element["term"])>=3:
                            
                            new_element["type_page"] = "Article" 
                            new_element["num_article_words"] = len(sentence)  
                            #### related terms ##### 
                            related_terms=[]
                            if "See " in new_element["definition"]:
                                related_terms= new_element["definition"].split("See ")[1]
                            elif "SEE " in new_element["definition"]:
                                related_terms= new_element["definition"].split("SEE ")[1]  
                            new_element["related_terms"]=related_terms_info(related_terms)
                            ####
                            
                            new_element["term_id_in_page"]=term_id 
                            new_element["archive_filename"]= element["archive_filename"]
                            new_element["header"] = element["header"]
                            new_element["model"] = element["model"]
                            new_element["num_page_words"]= element["num_page_words"]
                            new_element["num_text_unit"] = element["num_text_unit"]
                            new_element["place"] = element["place"]
                            new_element["source_text_file"] = element["source_text_file"]
                            new_element["text_unit"] = element["text_unit"]
                            new_element["text_unit_id"] = element["text_unit_id"]
                            new_element["title"] = element["title"]
                            new_element["type_archive"] = element["type_archive"]
                            new_element["year"] = element["year"]
                            new_element["end_page"] =int(element['text_unit_id'].split("Page")[1])
                            new_element["edition"] = element["edition"]
                            
                            new_entries.append(new_element)
                            list_terms.append(new_element["term"].strip())
                            term_id += 1
                            
                
                
                r_removals=[]
                l_term = 0
                for l_term in range(0, len(list_terms)):
                    if check_special_caracters(list_terms[l_term]) or has_numbers(list_terms[l_term]):
                        r_removals.append(list_terms[l_term]) 
                    l_term=l_term +1

                for r_term in r_removals:
                    list_terms.remove(r_term)
                
                        
                if len(list_terms) >= 1:
                    if len(list_terms) == 1 and list_terms[0]== element["term"]:
                        pass
                    elif len(list_terms)<=6 and next_element["type_page"]=="Topic" and prev_element["type_page"]=="Topic":
                        pass
                    else:
                        for i in new_entries:
                            i["num_articles"] = len(list_terms)
                        eliminate_pages[edition].append(page_idx)
                        create_entries[edition][page_idx]=[]
                        for new_d in new_entries:
                            create_entries[edition][page_idx].append([element_page, new_d])
                             
   
    new_results = deleting_adding_entries(query_results, eliminate_pages, create_entries)
    return new_results
 



def check_special_caracters(mystring):
    return any(not c.isalnum() for c in mystring)


def has_numbers(mystring):
    return any(c.isdigit() for c in mystring)



def fixing_topics(query_results):
    eliminate_pages={}
    for edition in query_results:
        eliminate_pages[edition]=[]
        page_idx = 0
        
        while page_idx < len(query_results[edition]):
            element = query_results[edition][page_idx][1]
            current_page = query_results[edition][page_idx][0]

            if  (element["type_page"]=="Mix") or (element["type_page"]=="Empty" and element["num_articles"]<2):
                prev_element = query_results[edition][page_idx-1][1]
                
                if prev_element["type_page"]=="Topic":
                    
                    tmp_type = element["type_page"]
                    element["type_page"] = "Topic"

                    if tmp_type =="Empty":
                        element["term"] = prev_element["term"]
                    
                    elif similar(prev_element["term"].strip(), element["header"].strip()) > 0.70 or similar(prev_element["term"].strip(), element["term"].strip()) or prev_element["term"].strip() in element["definition"]:
                        element["term"] = prev_element["term"]
                    else:
                        element["term"] = element["header"].strip()
                    
                    if element["num_articles"] > 1:
                        for i in range(1, element["num_articles"]):
                            if page_idx + 1 < len(query_results[edition]):
                                page_idx += 1
                                n_element = query_results[edition][page_idx][1]
                                element["definition"]+=n_element["definition"]
                                element["num_article_words"]+=n_element["num_article_words"]
                                element["related_terms"]+= n_element["related_terms"]
                                eliminate_pages[edition].append(page_idx)
                            else:
                                print("Dont entering here - element %s - term %s -  page %s - page_idx %s - len %s" %(edition, element["term"], query_results[edition][page_idx][0], page_idx, len(query_results[edition])))
                            
                    element["num_articles"] = 1    
            page_idx +=1   
        
    new_results= delete_entries(query_results, eliminate_pages)              
    return new_results



def merge_articles(query_results):
    eliminate_pages={}
    page_number_dict={}
    for edition in query_results:
        eliminate_pages[edition]=[]
        page_number_dict[edition]={}

        for page_idx in range(0, len(query_results[edition])):
            prev_number = -1
            current_page=query_results[edition][page_idx][0]
            
            if current_page not in page_number_dict[edition]:
                page_number_dict[edition][current_page]=page_idx
            
            element = query_results[edition][page_idx][1]                               
                
            
            ###########################################        
            
            if "previous_page" in element['term']:
                current_definition= element["definition"]
                previous_page_idx= page_idx -1
                num_article_words=element["num_article_words"]
                related_terms=element["related_terms"]
            
                prev_elements = query_results[edition][previous_page_idx][1]
                prev_number = query_results[edition][previous_page_idx][0]
                if prev_elements["last_term_in_page"] and current_page > prev_number:
                    prev_elements["definition"]+=current_definition
                    prev_elements["num_article_words"]+=num_article_words
                    prev_elements["related_terms"]+= related_terms
                    prev_elements["end_page"] = current_page
                    
                    if prev_number in page_number_dict[edition] and prev_number != -1:
                        for prev_articles_idx in range(page_number_dict[edition][prev_number], page_idx):
                       
                            if query_results[edition][prev_articles_idx][0] == prev_number:
                           
                                 query_results[edition][prev_articles_idx][1]["num_page_words"]+=num_article_words
                  
                    pd_i = page_idx 
                    for i in range(1, element["num_articles"]):
                        if pd_i + 1 < len(query_results[edition]):
                            pd_i += 1
                            if query_results[edition][pd_i][0] == current_page:
                                n_element = query_results[edition][pd_i][1]
                                n_element["num_page_words"]-=num_article_words
                                n_element["num_articles"]-=1
                 
    
                
                eliminate_pages[edition].append(page_idx)
            else:
                element["end_page"] = current_page  
   
    new_results= delete_entries(query_results, eliminate_pages)
    
    return new_results


def removing_fullpages(query_results):
    
    eliminate_pages={}
    for edition in query_results:
        eliminate_pages[edition]=[]
        for page_idx in range(0, len(query_results[edition])):
            element=query_results[edition][page_idx][1]
            if element["type_page"]=="FullPage":
                eliminate_pages[edition].append(page_idx)
        

    new_results= delete_entries(query_results, eliminate_pages)
    
    return new_results     
                                        
         




def merge_topics(query_results):
    eliminate_pages={}
    provenance_removal={}
    freq_topics_terms={}
    merged_topics={}
    character_terms=[]
    parts_string=["S", "HXXA", "P", "C","", " ", "_", "-", "Part", "Fart", "Parc", "CPart","P", "PI", "PII", "PIII", "P", "C", "IV", "VI" "VII", "VIII", "IX", "XI"]
    for edition in query_results:
        eliminate_pages[edition]=[]
        provenance_removal[edition]=[]
        freq_topics_terms[edition]={}
        merged_topics[edition]={}
        
        page_idx = 0
        while page_idx < len(query_results[edition]):
            current_page=query_results[edition][page_idx][0]        
            element = query_results[edition][page_idx][1]

            if "Topic" in element['type_page']:
                term=element["term"].strip()
                while check_string(term, parts_string) and page_idx < len(query_results[edition]):
    
                    page_idx = page_idx + 1
                    next_element = query_results[edition][page_idx][1]
                    term= next_element["term"].strip()
                    element["definition"]+=next_element["definition"]
                    element["num_article_words"]+=next_element["num_article_words"]
                    element["num_page_words"]+=next_element["num_page_words"]                  
                    element["related_terms"]+= next_element["related_terms"]
                    element["end_page"] = next_element['end_page']
                    provenance_removal[edition].append(element["end_page"])
                    eliminate_pages[edition].append(page_idx)
                    page_idx + 1
                
                clean_term=clean_topics_terms(term)
        
                p_id= page_idx + 1
                flag_force = 0  
                if p_id < len(query_results[edition]):
                    flag = 0
                    
                    while p_id < len(query_results[edition]) and flag == 0:
                        
                        next_element = query_results[edition][p_id][1]
                        
                        if not check_string(next_element["term"], parts_string):
                            next_term=clean_topics_terms(next_element["term"].strip())
            
                        else:
                            next_term=next_element["term"].strip()
                            
                        if p_id < len(query_results[edition])-1:    
                            
                            two_next_element = query_results[edition][p_id+1][1]
                            if not check_string(two_next_element["term"], parts_string):
                                two_next_term=clean_topics_terms(two_next_element["term"])
                            else:
                                two_next_term=two_next_element["term"].strip()
                         
                        else:
                            two_next_term=""
                            
                    
                                
                        #m1 = re.search('^([0-9]+)|([IVXLCM]+)\\.?$', next_element["term"])
                        #m2 = re.search('^([0-9]+)|([IVXLCM]+)\\.?$', two_next_element["term"])
                        
                        definition1= next_element["definition"]
                        
                    
                        if similar(clean_term, next_term) > 0.70 or len(next_term)<=3 or len(two_next_term)<=3 or len(definition1)<=30  or check_string(next_term, parts_string) or check_string(two_next_term, parts_string)  or next_term in clean_term or two_next_term in clean_term or similar(clean_term, two_next_term) > 0.70: 
                           
                            if clean_term!="" or clean_term!=" ":
                                if clean_term not in merged_topics[edition]:
                                    merged_topics[edition][clean_term]=[]
                                    merged_topics[edition][clean_term].append(clean_term)
                        
                                if not check_string(next_term, parts_string) and len(next_term)>3:
                                     merged_topics[edition][clean_term].append(next_term)
                            
                         
                            element["definition"]+=next_element["definition"]
                            element["num_article_words"]+=next_element["num_article_words"]
                            element["num_page_words"]+=next_element["num_page_words"]                  
                            element["related_terms"]+= next_element["related_terms"]
                            element["end_page"] = next_element['end_page']
                            provenance_removal[edition].append(element["end_page"])
                            eliminate_pages[edition].append(p_id)
                            p_id= p_id + 1
                            
                            if similar(clean_term, two_next_term) > 0.70 or len(two_next_term)<=3  or check_string(two_next_term, parts_string) or two_next_term in clean_term:   
                                ## adding the two nexts ones. 
                                
                                element["definition"]+=two_next_element["definition"]
                                element["num_article_words"]+=two_next_element["num_article_words"]
                                element["num_page_words"]+=two_next_element["num_page_words"]                  
                                element["related_terms"]+= two_next_element["related_terms"]
                                element["end_page"] = two_next_element['end_page']
                                
                                provenance_removal[edition].append(element["end_page"])
                                
                                if not check_string(two_next_term, parts_string) and len(two_next_term)>3:
                                     merged_topics[edition][clean_term].append(two_next_term)
                                        
                                eliminate_pages[edition].append(p_id)
                                p_id= p_id + 1

                                
                        
                        else:
                            p_id= p_id + 1
                            flag = 1
                    
        
               
                page_idx = p_id
                if clean_term in merged_topics[edition]:
                   
                    if character_terms:
                        freq_term=most_frequent(merged_topics[edition][clean_term], character_terms[-1])
                    else:
                        freq_term=most_frequent(merged_topics[edition][clean_term])
                        
                            
                    freq_topics_terms[edition][clean_term]=freq_term
                                        
                    element["term"]=freq_term.strip()
                    
                    
                else:
                    element["term"]=clean_term.strip()
        
                    
                if len(clean_term)>1:
                    character_terms.append(clean_term[0])  

            else:
                page_idx += 1
                
            
        
    new_results= delete_entries(query_results, eliminate_pages)
    
    return new_results, merged_topics, freq_topics_terms, provenance_removal




def merge_topics_refine(query_results):
    
    topics_editions={}
    eliminate_pages={}
    merged_topics_refine={}
    provenance_removal={}
    for edition in query_results:
        eliminate_pages[edition]=[]
        provenance_removal[edition]=[]
        topics_editions[edition]={}
        merged_topics_refine[edition]=[]
        page_idx = 0
        character="A"
        while page_idx < len(query_results[edition]):
            
            element = query_results[edition][page_idx][1]
            term = element["term"].strip()

            m = re.search('^([0-9]+)|([IVXLCM]+)\\.?$', term)
            
            if "Topic" in element['type_page'] and term!="" and len(term)>=3:
            #and m is None:
            #and term[0] >= character:
                
                if term not in topics_editions[edition]:
                    topics_editions[edition][term]={}
                    topics_editions[edition][term]["start"]=page_idx
                    topics_editions[edition][term]["end"]= page_idx
                else:
                    topics_editions[edition][term]["end"]=page_idx
            
            page_idx += 1
            #if term:
            #    character=term[0]
        
        
        
        
        for term in topics_editions[edition]:
            
            p_start= topics_editions[edition][term]["start"]
            p_end =  topics_editions[edition][term]["end"]
            first_element= query_results[edition][p_start][1]
            
            for p_id in range (p_start + 1, p_end+1):
                element = query_results[edition][p_id][1]
                first_element["definition"]+=element["definition"]
                first_element["num_article_words"]+=element["num_article_words"]
                first_element["num_page_words"]+=element["num_page_words"]                  
                first_element["related_terms"]+= element["related_terms"]
                first_element["end_page"] = element['end_page']
                provenance_removal[edition].append(first_element["end_page"])
                merged_topics_refine[edition].append(term)
                eliminate_pages[edition].append(p_id)
        
    new_results= delete_entries(query_results, eliminate_pages)
    
    return new_results, provenance_removal, merged_topics_refine


def main():
    print(sys.argv, len(sys.argv))

    filename = sys.argv[1]
    query_results=read_query_results(filename)

    dc_results = copy.deepcopy(query_results)
    sorted_results= sort_query_results(dc_results)
    consistency_query_results(sorted_results)

    query_results_articles_fp=fixing_fullPages(sorted_results)
    query_results_articles = merge_articles(query_results_articles)

    articles_refined=fixing_articles(query_results_articles)

    articles_refined = fixing_topics(articles_refined)
    articles_refined= removing_fullpages(articles_refined)

    topics_refined, merged_topics, freq_topics_terms, provenance_removal =merge_topics(articles_refined)

    final_refine, provenance_removal,merged_topics_refine =merge_topics_refine(topics_refined)

    write_query_results(filename+"_updated", final_refine)

    df=create_dataframe(final_refine)

    includeKeywords=["Article", "Topic"]

    df=df[df["typeTerm"].str.contains('|'.join(includeKeywords))].reset_index(drop=True)

    df.to_json(r'../results_NLS/'+filename+'_dataframe', orient="index")

    print("FINISH!")
if __name__ == "__main__":
    main()
