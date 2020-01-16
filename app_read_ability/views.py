from django.shortcuts import render, redirect
import os
import syllables
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from django.http import HttpResponse
import numpy as np

# Create your views here.
def home(request):
	rbl_list = StoreData.objects.all().order_by('-id')
	len_file = len(rbl_list)
	page = request.GET.get('page', 1)
	paginator = Paginator(rbl_list, 5)
	try:
		rbl = paginator.page(page)
	except PageNotAnInteger:
		rbl = paginator.page(1)
	except EmptyPage:
		rbl = paginator.page(paginator.num_pages)
	return render(request,'index.html',{'rbl':rbl,'len_file':len_file})


def check_readbily(request):
	if request.method == 'POST':
		myFile = request.FILES.getlist('file')
		v_one = 206.835
		v_two = 1.015
		v_three = 84.6
		os.chdir('./data_with_no_index/')
		cwd = os.getcwd()
		print(cwd)
		for file_name in myFile:
			file_name = str(file_name)
			try:
				data_file = open(file_name,'r')
				list_data = []
				for i in data_file:
					data_split = i.strip().split('\n')
					for j in data_split:
						if j !='':
							data_split = j.strip().split('\n')
							list_data.append(data_split)
				len_of_tweets = len(list_data)
				no_sen_by_twt = []
				no_wrd_by_twt = []
				sylb = []
				for sen in list_data:
					for twt in sen:
						twt = twt.split('.')
						no_sen_by_twt.append(len(twt))
						twt  = str(twt)
						twt = twt.replace('[','')
						twt = twt.replace(']','')
						twt = twt.replace("'",'')
						twt = twt.replace(",",'')
						syl = syllables.estimate(twt)
						sylb.append(syl)
						twt = twt.split()
						no_wrd_by_twt.append(len(twt))
				no_resuts = []
				
				for i in range(len_of_tweets):
				    v_four = no_wrd_by_twt[i]/no_sen_by_twt[i]
				    v_five = sylb[i]/no_wrd_by_twt[i]
				    v_six = v_two*v_four
				    v_seven = v_three*v_five
				    results = v_one - v_six - v_seven
				    no_resuts.append(results)
				median_results = np.median(no_resuts)
				median_results = str(round(median_results, 2 ))
				s = 0
				n = len(no_resuts)
				for i in no_resuts:
				    s = s + i

				read_abilty = s /n
				read_abilty = str(round(read_abilty, 2))
				sum_sylb = sum(sylb)
				sum_tl_twt = sum(no_sen_by_twt)
				sum_tl_wrd = sum(no_wrd_by_twt)
				file_name = file_name.replace('.txt','')
				data_read = StoreData(file_names=file_name,tl_twts=sum_tl_twt,tl_wrds=sum_tl_wrd,tl_sylbs=sum_sylb,median=median_results,read_scores=read_abilty).save()
				data_view = DataView(file_id=data_read,file_name="",tl_twt="",tl_wrd="",tl_sylb="",median="jbh",read_score="",).save()
				data_file.close()
			except OSError as e:
				os.chdir('../')
				return HttpResponse('<h1>Please Select  on ./data_with_no_index/</h1>\
					<p>path ->  ./Check_read_ability/data_with_no_index/</p>')
					
		os.chdir('../')
	return redirect('home')



def delete(request, id):  
    rbl = StoreData.objects.get(id=id)  
    rbl.delete()  
    return redirect("home")

def download_csv_file(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="file_data.csv"'
	writer = csv.writer(response)
	writer.writerow(['File Name','Total Tweets','Total Words','Syllable','Read Ability'])
	data = StoreData.objects.filter()
	for row in data:
	    rowobj = [row.file_names,row.tl_twts,row.tl_wrds,row.tl_sylbs,row.read_scores]
	    writer.writerow(rowobj)
	return response 


def delete_all(request):
	StoreData.objects.all().delete()
	return redirect("home")





   




