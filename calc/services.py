import pandas as pd
import numpy as np
from datetime import date
from . constants import country_code , country_list,regions, quality_classification_levels

# Returns indexes of requires columns
def getIndex(name,data):
  for i,j in enumerate(data.columns):
    if j==name:
      return i
# Returns categories based on date range
def getCategory(days,category):
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
def getColumn(column_name,dataframe):
  for col in dataframe.columns:  
    if column_name.lower() in col.lower():
      return col
  return None

# Convert dates in the dd/mm/yy format
def format_Dates(rowindex,data,date_indexes):
  for cols in date_indexes:
    if pd.notnull(data.loc[rowindex,data.columns[cols]]):
      data.loc[rowindex,data.columns[cols]]=pd.to_datetime(data.loc[rowindex,data.columns[cols]]).strftime('%d/%m/%Y')
  return data

# Generate levels for the Quality Classification entries
def qa_Classification_levels(rowindex,data):
  levels = data.loc[rowindex,getColumn("Quality Classification",data)].split("|")
  for q,l in zip(quality_classification_levels,levels):
    data.loc[rowindex,q] = l
  return data

# Case Age buckets column created from CaseAge column(created from coparision of report run and date originated)  
def caseAge_Buckets(rowindex,data):
  if data.loc[rowindex,getColumn("status",data)].lower() != 'Closed'.lower():
    data.loc[rowindex,'Report Run']=date.today().strftime("%d/%m/%Y")
    a=pd.to_datetime(data[getColumn("date originated",data)].iloc[rowindex])-pd.to_datetime(data['Report Run'].iloc[rowindex])
    data.loc[rowindex,'Case Age']=abs(a.days)
    data.loc[rowindex,'Case Age Buckets']=getCategory(data.loc[rowindex,"Case Age"],'Case Age Buckets')
  return data

#Empty installed date column filled with shipped date also time to failure column is created
# from comparision of date originated and installed on date column and then burckets is formed from the 
# time to failure column 
def timeToFailure_Buckets(rowindex,data):
  if pd.isnull(data.loc[rowindex,getColumn("Installed On Date",data)]):
    data.loc[rowindex,getColumn("Installed On Date",data)]=data.loc[rowindex,getColumn("Shipped On Date",data)]
  a=pd.to_datetime(data[getColumn("date originated",data)].iloc[rowindex])-pd.to_datetime(data[getColumn("Installed On Date",data)].iloc[rowindex])
  data.loc[rowindex,'Time to Failure']=a.days
  data.loc[rowindex,'Time to Failure Buckets']=getCategory(data.loc[rowindex,"Time to Failure"],'Time to Failure Buckets')
  return data

# Flagged installation complaint in SR Type column
def install_Complaints(rowindex,data):
  if "install".lower() in data.loc[rowindex,getColumn("sr type",data)].lower():
    data.loc[rowindex,'Installation complaint']="Yes"
  else:
    data.loc[rowindex,'Installation complaint']="No"
  return data

# Map regions from the country list or country code. Also empty account country entries to be
# filled with event country 
def complaint_Regions(rowindex,data):
  if pd.isnull(data.loc[rowindex,getColumn("account country",data)]):
    data.loc[rowindex,getColumn("account country",data)]=data.loc[rowindex,getColumn("event country",data)]
  for country,code,region in zip(country_list,country_code,regions):
    if str(data.loc[rowindex,getColumn("account country",data)]).lower()==country.lower():
      data.loc[rowindex,'Regions']=region
    elif str(data.loc[rowindex,getColumn("account country",data)]).lower()==code.lower():
      data.loc[rowindex,'Regions']=region
  return data