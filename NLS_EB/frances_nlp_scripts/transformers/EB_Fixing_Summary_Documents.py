
#!/usr/bin/env python
# coding: utf-8

import pickle
import numpy as np

with open('terms_definitions.txt', 'rb') as fp:
    documents = pickle.load(fp)

with open('topics_summaries_total.txt', 'rb') as fp2:
    documents_sum = pickle.load(fp2)

with open('terms_details.txt', 'rb') as fp3:
    terms_info = pickle.load(fp3)

documents_sum_final=[]

cont=0
cont2=0
for i in range(0, len(documents_sum)):
   if len(documents_sum[i])==0:
     if len(documents[i])!=0:
         documents_sum_final.append(documents[i])
         cont=cont+1
     else:
         definition="Empty definition for %s"%(terms_info[i][0])
         documents_sum_final.append(definition)
         print(definition)
         cont2=cont2+1
         
   else:
     documents_sum_final.append(documents_sum[i])

print("Number of fixes %s" %cont)
print("Number of NO fixes %s" %cont2)

for i in range(0, len(documents_sum_final)):
   if len(documents_sum_final[i])==0:
     print("ERROR IN %s" %i)

with open ('terms_definitions_final.txt', 'wb') as fp4:
     pickle.dump(documents_sum_final, fp4)
