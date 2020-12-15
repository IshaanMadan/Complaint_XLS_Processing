from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from datetime import date
from io import StringIO as IO
from . services import *

@csrf_exempt
def upload(request):
  if request.method == 'POST':
    uploaded_file = request.FILES.get("doc")
    ext=uploaded_file.name.split(".")[-1]
    if ext=='xlsx':
      data=pd.read_excel(uploaded_file)
      dates=[item for item in data.columns if 'date'.lower() in item.lower()]
      date_indexes=[get_index(date,data) for date in dates]  
      for rowindex, row in data.iterrows():
        #Task 2
        data=format_dates(rowindex,data,date_indexes)
        #Task 3
        data=qa_classification_levels(rowindex,data)
        #Task 4
        data=caseage_buckets(rowindex,data)
        #Task5
        data=time_to_failure_buckets(rowindex,data)
        #Task6
        data=install_complaints(rowindex,data)
        #Task7
        data=complaint_regions(rowindex,data)
      #Task 8
      new_df=data.copy()
      new_df,new_cols=qa_as_reported_code_formatting(data)

      # Retain old columns format with addition of new columns
      final_cols=list(data.columns)
      final_cols=final_cols+new_cols
      new_df = new_df[final_cols]
      
      # Excel file creattion
      excel_file = uploaded_file
      xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
      data.to_excel(xlwriter, sheet_name='Source',index=False)
      new_df.to_excel(xlwriter, sheet_name='As Reported Source',index=False)
      xlwriter.save()
      xlwriter.close()
      excel_file.seek(0)
      response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Disposition'] = 'attachment; filename=source.xlsx'
      return response
    else:
      return HttpResponse("Invalid file")