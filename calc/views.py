from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from .models import Document
from datetime import date
from io import StringIO as IO
# Create your views here.

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

def getIndex(name,data):
  for i,j in enumerate(data.columns):
    if j.lower()==name:
      # print(j)
      return i
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
def home(request):
  return NOne
# from django.views.decorators.csrf import ensure_csrf_cookie
# @ensure_csrf_cookie
@csrf_exempt
def upload(request):
    context = {}

    if request.method == 'POST':
        uploaded_file = request.FILES.get("doc")
        ext=uploaded_file.name.split(".")[1]
        if ext=='xlsx':

          fulldata=pd.ExcelFile(uploaded_file)
          sheet_names=fulldata.sheet_names
          data=pd.read_excel(fulldata,"Data Extract Format - Examples")
          data1 = pd.read_excel(fulldata,"Master List for Region Mapping")


          dates=["Date Originated","Installed On Date (Affected Items)","Initial Review Complete Date (Page Three)","Shipped On Date (Affected Items)","Date Closed","Date/Time Closed  (Page Three)"]
          date_indexes=[getIndex(date.lower(),data) for date in dates]  
          Quality = ["Division", "Franchise", "Product Family", "Product"," Quality Site"] 
          qa_cat=['QA As Reported Code 0','QA As Reported Code 1']

          for rowindex, row in data.iterrows():
    #Task2
            for colindex, cols in enumerate(data.columns):
              if colindex in date_indexes:
                data[cols] =  pd.to_datetime(data[cols]).dt.strftime('%d/%m/%Y')
    #Task5
            a=pd.to_datetime(data['Date Originated'].iloc[rowindex])-pd.to_datetime(data['Installed On Date (Affected Items)'].iloc[rowindex])
            data.loc[rowindex,'Time to Failure']=a.days
            data.loc[rowindex,'Time to Failure Buckets']=getCategory(data.loc[rowindex,"Time to Failure"],'Time to Failure Buckets')
    
    #Task 4
            if data.loc[rowindex,'Status']!='Closed':
              data.loc[rowindex,'Report Run']=date.today().strftime("%d/%m/%Y")
              a=pd.to_datetime(data['Date Originated'].iloc[rowindex])-pd.to_datetime(data['Report Run'].iloc[rowindex])
              data.loc[rowindex,'Case Age']=abs(a.days)
              data.loc[rowindex,'Case Age Buckets']=getCategory(data.loc[rowindex,"Case Age"],'Case Age Buckets')
    #Task3
            List = data.loc[rowindex,'Quality Classification (Affected Items)'].split("|")
            for q,l in zip(Quality,List):
              data.loc[rowindex,q] = l
    #Task6
            if "install" in data.loc[rowindex,'SR Type (Page Three)'].lower():
              data.loc[rowindex,'Installation complaint']="Yes"
            else:
              data.loc[rowindex,'Installation complaint']="No"
    #Task7
            if pd.isnull(data.loc[rowindex,'Account Country (Page Three)']):
              data.loc[rowindex,'Account Country (Page Three)']=data.loc[rowindex,'Event Country (Page Three)']
            if pd.isnull(data.loc[rowindex,'Account Country (Page Three)'])==False:
              if len(data1[data1['Country'].str.lower()==data.loc[rowindex,'Account Country (Page Three)'].lower()]) !=0:
                data.loc[rowindex,'Regions']=data1[data1['Country']==data.loc[rowindex,'Account Country (Page Three)']]['Region'].values[0]
              elif len(data1[data1['Code'].str.lower()==data.loc[rowindex,'Account Country (Page Three)'].lower()]) !=0:
                data.loc[rowindex,'Regions']=data1[data1['Code']==data.loc[rowindex,'Account Country (Page Three)']]['Region'].values[0]
    #Task8
          new_df=data.copy()
          new_df['QA As Reported Code (Page Three)']=new_df['QA As Reported Code (Page Three)'].fillna('-199')
          new_df=explode(new_df.assign(q_a=new_df['QA As Reported Code (Page Three)'].str.split(';')), 'q_a')
          new_df['QA As Reported Code (Page Three)']=new_df['q_a']
          new_df['QA As Reported Code (Page Three)'] = new_df['QA As Reported Code (Page Three)'].replace('-199',np.nan)
          new_df.drop('q_a',axis=1,inplace=True)
          for rowindex,row in new_df.iterrows():
            if pd.isnull(new_df.loc[rowindex,'QA As Reported Code (Page Three)'])==False:
              last_levels=new_df.loc[rowindex,'QA As Reported Code (Page Three)'].split('|')[-2:]
              for qa,level in zip(qa_cat,last_levels):
                new_df.loc[rowindex,qa]=level
          excel_file = uploaded_file
          xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
          data.to_excel(xlwriter, sheet_name='Source')
          new_df.to_excel(xlwriter, sheet_name='As Reported Code')
          xlwriter.save()
          xlwriter.close()
          excel_file.seek(0)
          response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
          response['Content-Disposition'] = 'attachment; filename=source.xlsx'
          return response
        else:
          return HttpResponse("Invalid file")