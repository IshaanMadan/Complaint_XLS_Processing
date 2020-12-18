import pandas as pd
import numpy as np
from datetime import date
from . constants import *
import sys

# Returns indexes of requires columns
def get_index(name,data):
  for i,j in enumerate(data.columns):
    if j==name:
      return i
# Returns categories based on date range
def get_category(days,category):
  status=np.nan
  if category=='Time to Failure Buckets':
    
    if days<90:
      status="Less than 90 Days"
    elif days>=90 and days<=365:
      status="90 to 365 Days"
    elif days>365 and days<=730:
      status="1 to 2 years"
    elif days>730:
      status=" Above 2 Years"
  elif category=='Case Age Buckets':
    if days<45:
      status="Below 45 Days"
    elif days>=45 and days <90:
      status="45 to 90 days"
    elif days >=90 and days<120:
      status="90 to 120 days"
    elif days>120:
      status="Above 120 days"
  return status

# Returns actual columnname from matching columnname string
def get_column(column_name,dataframe):
  for col in dataframe.columns:  
    if column_name.lower() in col.lower():
      return col
  return column_name

# Convert dates in the dd/mm/yy format
def format_dates(rowindex,data,date_indexes):
  for cols in date_indexes:
    if pd.notnull(data.loc[rowindex,data.columns[cols]]):
      data.loc[rowindex,data.columns[cols]]=pd.to_datetime(data.loc[rowindex,data.columns[cols]]).strftime('%d/%m/%Y')
  return data

# Generate levels for the Quality Classification entries
def qa_classification_levels(rowindex,data):
  flag=0
  col_not_found=''
  status='found'
  cols=[get_column("Quality Classification",data)]
  for c in cols:    
    if c not in data.columns:
      flag=1
      col_not_found=c
      status="not found"
      break
  if flag==0:
    levels = data.loc[rowindex,get_column("Quality Classification",data)].split("|")
    for q,l in zip(quality_classification_levels,levels):
      data.loc[rowindex,q] = l
    return data,status
  else:
    return col_not_found,status

# Case Age buckets column created from CaseAge column(created from coparision of report run and date originated)  
def caseage_buckets(rowindex,data):
  flag=0
  cols=[get_column("Quality Classification",data)]
  for c in cols:    
    if c==None:
      print("hi")
      print(cols)
      flag=1
      break
  if flag==0:
  
    if data.loc[rowindex,get_column("status",data)].lower() != 'Closed'.lower():
      data.loc[rowindex,'Report Run']=date.today().strftime("%d/%m/%Y")
      a=pd.to_datetime(data[get_column("date originated",data)].iloc[rowindex])-pd.to_datetime(data['Report Run'].iloc[rowindex])
      data.loc[rowindex,'Case Age']=abs(a.days)
      data.loc[rowindex,'Case Age Buckets']=get_category(data.loc[rowindex,"Case Age"],'Case Age Buckets')
    return data
  else:
    return ''
    

#Empty installed date column filled with shipped date also time to failure column is created
# from comparision of date originated and installed on date column and then burckets is formed from the 
# time to failure column 
def time_to_failure_buckets(rowindex,data):
  flag=0
  cols=[get_column("Installed On Date",data),get_column("date originated",data)]
  for c in cols:    
    if c==None:
      print("hi")
      print(cols)
      flag=1
      break
  if flag==0:
    if pd.isnull(data.loc[rowindex,get_column("Installed On Date",data)]):
      data.loc[rowindex,get_column("Installed On Date",data)]=data.loc[rowindex,get_column("Shipped On Date",data)]
    a=pd.to_datetime(data[get_column("date originated",data)].iloc[rowindex])-pd.to_datetime(data[get_column("Installed On Date",data)].iloc[rowindex])
    data.loc[rowindex,'Time to Failure']=a.days
    data.loc[rowindex,'Time to Failure Buckets']=get_category(data.loc[rowindex,"Time to Failure"],'Time to Failure Buckets')
    return data
  else:
    return ''

# Flagged installation complaint in SR Type column
def install_complaints(rowindex,data):
  flag=0
  cols=[get_column("sr type",data)]
  for c in cols:    
    if c==None:
      flag=1
      break
  if flag==0:
    if "install".lower() in data.loc[rowindex,get_column("sr type",data)].lower():
      data.loc[rowindex,'Installation complaint']="Yes"
    else:
      data.loc[rowindex,'Installation complaint']="No"
    return data
  else: 
    return ''

# Map regions from the country list or country code. Also empty account country entries to be
# filled with event country 
def complaint_regions(rowindex,data):
  flag=0
  cols=[get_column("account country",data),get_column("event country",data)]
  for c in cols:    
    if c==None:
      flag=1
      break
  if flag==0:
    if pd.isnull(data.loc[rowindex,get_column("account country",data)]):
      data.loc[rowindex,get_column("account country",data)]=data.loc[rowindex,get_column("event country",data)]
    k=data.loc[rowindex,'Account Country (Page Three)']
    if pd.notnull(k):
      for i in mapped_regions:
        if k == i['country']:
          data.loc[rowindex,'Regions']=i['region']
        elif k == i['code']:
          data.loc[rowindex,'Regions']=i['region']
    return data
  else:
    return ''
#Created rows for 'QA as Reported Code' seprated by ';'
def explode(df, lst_cols, fill_value='', preserve_index=False):
    # make sure `lst_cols` is list-alike
    if (lst_cols is not None
        and len(lst_cols) > 0
        and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)
    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()
    # preserve original index values    
    idx = np.repeat(df.index.values, lens)
    # create "exploded" DF
    res = (pd.DataFrame({
                col:np.repeat(df[col].values, lens)
                for col in idx_cols},
                index=idx)
             .assign(**{col:np.concatenate(df.loc[lens>0, col].values)
                            for col in lst_cols}))
    # append those rows that have empty lists
    if (lens == 0).any():
        # at least one list in cells is empty
        res = (res.append(df.loc[lens==0, idx_cols], sort=False)
                  .fillna(fill_value))
    # revert the original index order
    res = res.sort_index()
    # reset index if requested
    if not preserve_index:        
        res = res.reset_index(drop=True)
    return res
# Created rows for 'QA as Reported Code' seprated by ';'. Also columns for 
# last two levels is created as well as combined two levels are created.
def qa_as_reported_code_formatting(data):
  flag=0
  cols=[get_column("QA As Reported Code (Page Three)",data)]
  for c in cols:    
    if c==None:
      flag=1
      break
  if flag==0:
    new_df=data.copy()
    new_df["QA As Reported Code (Page Three) (formatted)"]=new_df['QA As Reported Code (Page Three)']
    new_df['QA As Reported Code (Page Three) (formatted)']=new_df['QA As Reported Code (Page Three) (formatted)'].fillna('-199')
    new_df=explode(new_df.assign(q_a=new_df['QA As Reported Code (Page Three) (formatted)'].str.split(';')), 'q_a')
    new_df['QA As Reported Code (Page Three) (formatted)']=new_df['q_a']
    new_df['QA As Reported Code (Page Three) (formatted)'] = new_df['QA As Reported Code (Page Three) (formatted)'].replace('-199',np.nan)
    new_df.drop('q_a',axis=1,inplace=True)
    for rowindex,row in new_df.iterrows():
      if pd.isnull(new_df.loc[rowindex,'QA As Reported Code (Page Three) (formatted)'])==False:
        last_levels=new_df.loc[rowindex,'QA As Reported Code (Page Three) (formatted)'].split('|')[-2:]
        new_df.loc[rowindex,'As Reported Code Combined Level 4 and 5']='|'.join(last_levels)
        for qa,level in zip(qa_cat,last_levels):
          new_df.loc[rowindex,qa]=level
    new_cols=['QA As Reported Code (Page Three) (formatted)',qa_cat[0],qa_cat[1],'As Reported Code Combined Level 4 and 5']
    return new_df,new_cols
  else:
    return '',''    