from django.shortcuts import render, redirect
import os
import syllables
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from django.http import HttpResponse
import numpy as np
import json
from django.http import JsonResponse
from json import dumps
from django.core import serializers
import re
from textblob import TextBlob
import tweepy
import csv
import json
import pandas as pd




consumer_key = "mJ2fluR2xOZaj5byk68urYhRl" 
consumer_secret = "c0lmSii3lq436Oh9Lyp2vsIkxj2fLMTVaCfVbi8xoX1L6kXJJ2"
access_key = "1048889324052275200-hVDEZ5I7L7wQLx2KclPnACpj982rcx"
access_secret = "eI7pR91fjbVSrGNVGRUbd6CEVEIp82rkUMmiPhH9xlK5j"



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
					i = re.sub('\.\.+', ' ', i)
					i = re.sub(' +', ' ',i)
					print(i)
					data_split = i.strip().split('\n')
					for j in data_split:
						if j !='' and len(j)>2:
							data_split = j.split('\n')
							list_data.append(data_split)
				len_of_tweets = len(list_data)
				no_sen_by_twt = []
				no_wrd_by_twt = []
				sylb = []
				# print(list_data)
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
				try:
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
					print(len_of_tweets,'#########')
					data_read = StoreData(file_names=file_name,tl_twts=len_of_tweets,tl_sents=sum_tl_twt,tl_wrds=sum_tl_wrd,tl_sylbs=sum_sylb,median=median_results,read_scores=read_abilty)
					data_read.save()
					data_view = DataView(file_id=data_read,file_name=file_name,tl_twt=no_sen_by_twt,tl_wrd=no_wrd_by_twt,tl_sylb=sylb,median=median_results,read_score=no_resuts)
					data_view.save()
					data_file.close()
				except:
					print(file_name)
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
	writer.writerow(['File Name','Total Tweets','Total Sentence','Total Words','Syllable','Meadin','Read Ability'])
	data = StoreData.objects.filter()
	for row in data:
	    rowobj = [row.file_names,row.tl_twts,row.tl_sents,row.tl_wrds,row.tl_sylbs,row.median,row.read_scores]
	    writer.writerow(rowobj)
	return response 


def delete_all(request):
	StoreData.objects.all().delete()
	return redirect("home")


def view(request):
	view_id = request.GET['view_id']
	view_id  = int(view_id)
	data_view = DataView.objects.all().filter(file_id=view_id)
	data_view = serializers.serialize('json', data_view)
	return HttpResponse(json.dumps(data_view), content_type="application/json")


def scrap_data(request):
	if request.method == 'POST':
		type_of = request.POST.get('dropdown')
		if(str(type_of)  == '@Username'):
			username = request.POST.get('username')
			number_twt = request.POST.get('number_twt')
			no_twt = int(number_twt)
			user_name = str(username)
			get_user_tweets(no_twt, user_name) 


		if(str(type_of)  == '#Hashtag'):
			hashtag = request.POST.get('hasgtag')
			number_twt = request.POST.get('number_twt')
			get_hastag_tweets(number_twt,hashtag)
		
	return redirect('home')


def clean_tweet(tweet):
    tweet = re.sub('http\S+\s*', '', tweet)  # remove URLs
    tweet = re.sub('RT|cc', '', tweet)  # remove RT and cc
    tweet = re.sub('#\S+', '', tweet)  # remove hashtags
    tweet = re.sub('@\S+', '', tweet)  # remove mentions
    tweet = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), '', tweet)  # remove punctuations
    tweet = re.sub('\s+', ' ', tweet)  # remove extra whitespace
    emoji_clear_data = tweet.encode('ascii', 'ignore').decode('ascii')
    tweet = emoji_clear_data
    return tweet



# Function to extract tweets 
def get_user_tweets(no_twt,user_name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret) 
    api = tweepy.API(auth) 
    tweets = api.user_timeline(screen_name=str(user_name), count=int(no_twt))
    twts = ''
    for tweet in tweets:
        if(twts == ''):
            twts = twts + clean_tweet(tweet.text).strip()
        else:
             twts = twts + '\n' + clean_tweet(tweet.text).strip()
    print(twts)   
    with open('./data_with_no_index/'+ user_name + '_tweets.txt', 'w+') as f:
    	print(twts)
    	f.write(twts)
    	f.close()
    print('ok Bye')


def get_hastag_tweets(no_twt,hashtag):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
	twtid = []
	twttweet = []
	no_twt = int(no_twt)
	for tweet in tweepy.Cursor(api.search, q='#' + hashtag, rpp=100, wait_on_rate_limit = True).items(no_twt):
		hi_blob = TextBlob(tweet.text)
		detect_en = hi_blob.detect_language()
		if(detect_en == 'en'):
			twt_id = [tweet.id]
			twtid = twtid + twt_id
			twt_text = [tweet.text.encode('utf-8')]
			twttweet = twttweet + twt_text
	twt = {'id': twtid, 'text': twttweet}
	df = pd.DataFrame(twt)  
	df.to_csv(hashtag + '_hashtag.csv',index=False) 








   




