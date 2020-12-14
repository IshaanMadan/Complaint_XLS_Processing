from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from .models import Document
from datetime import date
from io import StringIO as IO
from . services import format_Dates,qa_Classification_levels,caseAge_Buckets,timeToFailure_Buckets,install_Complaints,complaint_Regions
from . services import getIndex, getColumn, getCategory

def home(request):
  return None
# from django.views.decorators.csrf import ensure_csrf_cookie
# @ensure_csrf_cookie
@csrf_exempt
def upload(request):
  if request.method == 'POST':
    uploaded_file = request.FILES.get("doc")
    ext=uploaded_file.name.split(".")[-1]
    if ext=='xlsx':
      data=pd.read_excel(uploaded_file)
      dates=[item for item in data.columns if 'date'.lower() in item.lower()]
      date_indexes=[getIndex(date,data) for date in dates]  
      for rowindex, row in data.iterrows():
        pass
        #Task 2
        data=format_Dates(rowindex,data,date_indexes)
        #Task 3
        data=qa_Classification_levels(rowindex,data)
        #Task 4
        data=caseAge_Buckets(rowindex,data)
        #Task5
        data=timeToFailure_Buckets(rowindex,data)
        #Task6
        data=install_Complaints(rowindex,data)
        #Task7
        data=complaint_Regions(rowindex,data)
      excel_file = uploaded_file
      xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
      data.to_excel(xlwriter, sheet_name='Source')
      xlwriter.save()
      xlwriter.close()
      excel_file.seek(0)
      response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Disposition'] = 'attachment; filename=source.xlsx'
      return response
    else:
      return HttpResponse("Invalid file")