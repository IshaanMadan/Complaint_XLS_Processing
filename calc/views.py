from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from datetime import date
from io import StringIO as IO
from . services import *
flag=False
# def home(request):
  # return render(request,'home.html')
@csrf_exempt
def upload(request):
  if request.method == 'POST':
    # uploaded_file = request.FILES.get("document")
    uploaded_file = request.FILES["document"]


    # uploaded_file = request.FILES.get("document")
    print("upfile",uploaded_file.name)
    ext=uploaded_file.name.split(".")[-1]
    if ext=='xlsx':
      data=pd.read_excel(uploaded_file)
      dates=[item for item in data.columns if 'date'.lower() in item.lower()]
      date_indexes=[get_index(date,data) for date in dates]  
      for rowindex, row in data.iterrows():
        #Task 2
        data=format_dates(rowindex,data,date_indexes)
        #Task 3
        data,status=qa_classification_levels(rowindex,data)
        if status=="not found":
          return HttpResponse("{} column not found".format(data))
        #Task 4
        data=caseage_buckets(rowindex,data)
        if status=="not found":
          return HttpResponse("{} column not found".format(data))
        #Task5
        data=time_to_failure_buckets(rowindex,data)
        if status=="not found":
          return HttpResponse("{} column not found".format(data))
        #Task6
        data=install_complaints(rowindex,data)
        if len(data)==0:
          return HttpResponse("Column not found")
        #Task7
        data=complaint_regions(rowindex,data)
        if len(data)==0:
          return HttpResponse("Column not found")
      #Task 8
      new_df=data.copy()
      new_df,new_cols=qa_as_reported_code_formatting(data)
      if len(new_df)==0:
          return HttpResponse("Column not found")
      
      # Retain old columns format with addition of new columns
      final_cols=list(data.columns)
      final_cols=final_cols+new_cols
      new_df = new_df[final_cols]
      
      # Excel file creation
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
      # return HttpResponse("Invalid file")
    else:
      return HttpResponse("Invalid file")
  return render(request,'home.html')

      # return HttpResponse("Invalid file")