#!/usr/bin/env python
# coding: utf-8

# In[1]:
pip install pandas

import pandas as pd
import numpy as pn
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


#Lecture de notre dataframe
df = pd.read_excel("reseau_en_arbre.xlsx")
df.head(10)


# In[3]:


#compter le nombre de ligne colonnes dans le Dataframe
df.shape


# In[4]:


df.duplicated().sum()


# In[5]:


df["id_batiment"].duplicated().sum()


# In[ ]:





# In[6]:


df.isna().sum()


# #supression des doublants

# In[7]:


df_prop = df.drop_duplicates()


# In[8]:


df_prop.shape


# In[9]:


df_intacte = df_prop[df_prop["infra_type"]=="infra_intacte"]


# In[10]:


df_intacte.shape


# In[11]:


df_remplacer = df_prop[df_prop["infra_type"]=="a_remplacer"]


# In[12]:


df_remplacer.shape


# In[ ]:





# In[14]:


df_prop["id_batiment"].count()


# In[15]:


df_prop["id_batiment"].value_counts().count()


# In[16]:


df_group = df_remplacer.groupby("id_batiment")["nb_maisons"].value_counts()


# In[17]:


df_group.head()


# In[18]:


df_infra = pd.read_csv("infra.csv")


# In[19]:


df_infra.head()


# In[20]:


df_infra.shape


# In[21]:


df_infra.isna().sum()


# In[22]:


df_infra.duplicated().sum()


# In[23]:


df_batiment = pd.read_csv("batiments.csv")


# In[25]:


df_batiment.head()


# In[26]:


df_batiment.shape


# In[27]:


#compter le nombre d'hopitaux, habitation et ecole
df_batiment["type_batiment"].value_counts()


# In[28]:


#l'hopital etant une prioriter cherchant les batiment qui ont des hopitaux
df_batiment[df_batiment["type_batiment"]=="hôpital"].head()


# In[29]:


# L'ecole etant notre deuxieme prioriter cherchant les batiments qui ont des ecoles
df_batiment[df_batiment["type_batiment"]=="école"].head()


# In[ ]:





# In[29]:


with pd.ExcelWriter("rapport_complet.xlsx") as writer:
    df_batiment.to_excel(writer, sheet_name="Batiments", index=False)
    df_infra.to_excel(writer, sheet_name="infra", index=False)
    df_prop.to_excel(writer, sheet_name="df_prop", index=False)


# In[ ]:




