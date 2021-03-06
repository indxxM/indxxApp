import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from weightcalculation.graph_helper import get_user
from weightcalculation.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from django.contrib.sessions.backends.db import SessionStore
s = SessionStore()
import pdb;
import pandas as pd
import numpy as np
import csv
import uuid
from datetime import datetime
import requests
from django.views.static import serve
# Create your views here.

"""   Message List here """
Invalid_File = "Selected invalid file, Please select .csv file!"
Blank_File = "Selected blank file, Please select .csv file with data!"
Not_SMCAP = "Required SMCAP column name in upload file!"
Not_ISIN_SMCAP = "Required ISIN and SMCAP columns name in upload file!"
Not_ISIN_MLP_SECTOR = "Required ISIN , MLP and Sector columns name in upload file!"
Not_SMCAP_Classification = "Required SMCAP and Classification columns name in upload file!"
Not_ISIN_Classification = "Required ISIN and Classification columns name in upload file!"
Not_MCAP_ADTV_Dividend_Classification = "Required MCAP, ADTV, Dividend Yield and Classification columns name in upload file!"
Not_ISIN_MCAP_THEME = "Required ISIN, MCAP and Theme columns name in upload file!"
Not_SMCAP_Score = "Required SMCAP and Score columns name in upload file!"
Not_ISIN_SMCAP_ADTV3M_ADTV20D_Classification = "Required ISIN, SMCAP, ADTV3M, ADTV20D and Classification columns name in upload file!"
Not_ISIN_SMCAP_Domicile = "Required ISIN, SMCAP and Domicile columns name in upload file!"
Not_ISIN_SMCAP_Theme = "Required ISIN, SMCAP and Theme columns name in upload file!"
Not_ISIN_SMCAP_Primary_Listing = "Required ISIN, SMCAP and Primary Listing columns name in upload file!"


def initialize_context(request):
	context = {}

	# Check for any errors in the session
	error = request.session.pop('flash_error', None)

	if error != None:
		context['errors'] = []
		context['errors'].append(error)

	# Check for user in the session
	context['user'] = request.session.get('user', {'is_authenticated': False})
	return context
  
def home(request):
	context = initialize_context(request)
	return render(request, 'wc/home.html', context)
	
def sign_in(request):
	# Get the sign-in URL
	sign_in_url, state = get_sign_in_url()
	# Save the expected state so we can validate in the callback
	request.session['auth_state'] = state
	# Redirect to the Azure sign-in page
	return HttpResponseRedirect(sign_in_url)

def sign_out(request):
	# Clear out the user and token
	remove_user_and_token(request)

	return HttpResponseRedirect(reverse('home'))
  
def callback(request):
	# Get the state saved in session
	expected_state = request.session.pop('auth_state', '')
	# Make the token request
	token = get_token_from_code(request.get_full_path(), expected_state)

	# Get the user's profile
	user= get_user(token)
	
	if(user.get('mail') != ''):
		user_detail = User.objects.filter(email= user.get('mail'))
		if not user_detail:
			user_data = User(
				email = user.get('mail'),
				first_name = user.get('givenName'),
				last_name = user.get('surname'),
				is_staff = 1,
				is_active = 1
			)
			user_data.save()
		else:
			request.session['email'] = user_detail['email']
			request.session['fname'] = user_detail['first_name']
			request.session['lname'] = user_detail['last_name']
			
	"""	
	# Temporary! Save the response in an error so it's displayed
	request.session['flash_error'] = { 'message': 'Token retrieved',
		'debug': 'User: {0}\nToken: {1}'.format(user, token) }
	"""
	return HttpResponseRedirect(reverse('home'))

def gettoken(request):
	auth_code = request.GET['code']
	redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
	token = get_token_from_code(auth_code, redirect_uri)
	access_token = token['access_token']
	user = get_me(access_token)
	refresh_token = token['refresh_token']
	expires_in = token['expires_in']

	# expires_in is in seconds
	# Get current timestamp (seconds since Unix Epoch) and
	# add expires_in to get expiration time
	# Subtract 5 minutes to allow for clock differences
	expiration = int(time.time()) + expires_in - 300

	# Save the token in the session
	request.session['access_token'] = access_token
	request.session['refresh_token'] = refresh_token
	request.session['token_expires'] = expiration
	return HttpResponseRedirect(reverse('tutorial:mail'))

############### Template display here ################	
def equal_weight(request):
	templateName = 'wc/equal_weight.html'
	context = {'title': 'Equal Weight'}
	return render(request, templateName, context)

def ul_cap_weight(request):
	templateName = 'wc/ul_cap.html'
	context = {'title': 'Equal Weight'}
	return render(request, templateName, context)


def ul_cap_ag_weight(request):
	templateName = 'wc/ul_cap_ag.html'
	context = {'title': 'Uper, Lower, Agreegation Weight'}
	return render(request, templateName, context)
	
def upr_cap_weight(request):
	templateName = 'wc/upr_cap.html'
	context = {'title': 'Uper Cap Weight'}
	return render(request, templateName, context)

def ul_top_remain_secu_weight(request):
	templateName = 'wc/ul_top_remain_secu.html'
	context = {'title': 'Uper Cap, Lower Cap, Top, Remaining and security Weight'}
	return render(request, templateName, context)
	
def mlp_sector(request):
	templateName = 'wc/mlp_sector.html'
	context = {'title': 'MPL, Sector'}
	return render(request, templateName, context)
	
def sing_sec_agg(request):
	templateName = 'wc/sing_sec_agg.html'
	context = {'title': 'Uper Cap, Lower Cap, Top, Remaining and security Weight'}
	return render(request, templateName, context)
	
def us_sharing(request):
	templateName = 'wc/us_sharing.html'
	context = {'title': 'Pure Play, Quasi Play and Marginal Weight'}
	return render(request, templateName, context)

def global_space(request):
	templateName = 'wc/global_space.html'
	context = {'title': 'Single Security Cap, Quasi Play Cap'}
	return render(request, templateName, context)

def private_credit(request):
	templateName = 'wc/private_credit.html'
	context = {'title': 'Upper, Lower, Market Capitalization or ADTV'}
	return render(request, templateName, context)	

def g5_nextg(request):
	templateName = 'wc/g5_nextg.html'
	context = {'title': '5G Infrastructure & Hardware, Telecommunications Service Providers'}
	return render(request, templateName, context)
	
def ai_big_data(request):
	templateName = 'wc/ai_bigdata.html'
	context = {'title': 'Artificial Intelligence and Big Data'}
	return render(request, templateName, context)
	
def blockchain(request):
	templateName = 'wc/blockchain.html'
	context = {'title': 'Blockchain Index'}
	return render(request, templateName, context)
	
def global_aerospace(request):
	templateName = 'wc/global_aerospace.html'
	context = {'title': 'Global Aerospace & Defense Index'}
	return render(request, templateName, context)
	
def global_cloud_computing(request):
	templateName = 'wc/global_cloud_computing.html'
	context = {'title': 'Global Cloud Computing Index'}
	return render(request, templateName, context)
	
def global_ecomm(request):
	templateName = 'wc/global_ecomm.html'
	context = {'title': 'Global E-Commerce Index'}
	return render(request, templateName, context)
	
def global_iot(request):
	templateName = 'wc/global_iot.html'
	context = {'title': 'Global Internet Of Things Thematic Index'}
	return render(request, templateName, context)
	
def download_csv(request):
	url = 'staticfiles/upload/weight_calc.csv'
	f = open(url, 'r')
	response = HttpResponse(f, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename=weight_calc.csv'
	return response
############### Post form here ################	
def eq_weight_post(request):
	templateName = 'wc/equal_weight.html'
	if request.method == 'POST':
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+filename)
			
			row_count = len(df.axes[0])
			if row_count > 0:
				y = df.groupby('Theme')['ISIN'].count().reset_index()
				a= y['Theme'].count()
				if a==0:
						df['weight'] = 1/row_count
				else:
					theme_cap = 1/a
					for i in range(len(df)):
						for j in range(len(y)):
							if  df.iloc[i]['Theme']==y.iloc[j]['Theme']:
								df.at[i,'count'] = y.iloc[j]['ISIN']
									 
					for i in range(len(df)):
						df.at[i,'weight'] = theme_cap/df.iloc[i]['count']
			
			df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
			url = 'staticfiles/upload/'+dt_time+f.name
			f = open(url, 'r')
			response = HttpResponse(f, content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename='+dt_time+filename
			return response
		else:
			context = { 'message' : Invalid_File}
		return render(request,templateName,context)
	else:
		weightfile = EqualweightForm()
		return render(request,templateName,{'form':weightfile})


def ul_cap_weight_post(request):
	templateName = 'wc/ul_cap.html'

	if request.method == 'POST':
		x = float(request.POST['upper_cap'])
		y = float(request.POST['lower_cap'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			df['weight']=df['SMCAP']/df['SMCAP'].sum()
			df['weight']=df['weight']*100
			row_count = len(df.axes[0])
			#print(row_count)
			if row_count > 0:
				""" Caping """
				count = df['ISIN'][df['weight'] > x].count()
				while count > 0:
					excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
					sum_1 =  df['weight'][df['weight'] < x].sum()
					for i in range(len(df)):
						if df.iloc[i]['weight'] >= x:
							df.at[i,'weight'] = x
						else:
							df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
					count = df['ISIN'][df['weight'] > x].count()

				count = df['ISIN'][df['weight']<y].count()


				while count > 0:
					less_sum = -df['weight'][df['weight']<y].sum()+(count*y)
					sum_1 =  df['weight'][ df['weight']>y].sum()
					sum_2 = df['weight'][ df['weight']>=x].sum() 
					sum_1 = sum_1 - sum_2
					for i in range(len(df)):
						if df.iloc[i]['weight']<=y:
							df.at[i,'weight'] = y
						elif df.iloc[i]['weight']<x and df.iloc[i]['weight']>y:
							df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_1)*(less_sum) 
					count = df['ISIN'][df['weight'] <y].count()
			
				df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
				""" To download csv file """
				url = 'staticfiles/upload/'+dt_time+f.name
				f = open(url, 'r')
				response = HttpResponse(f, content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
				return response
			else:
				context = { 'message' : Blank_File }	
		else:
			context = { 'message' : Invalid_File }
		return render(request,templateName,context)		
	else:
		context = {}
		return render(request, templateName, context)


def ul_cap_ag_weight_post(request):
	templateName = 'wc/ul_cap_ag.html'
	if request.method == 'POST':

		if request.POST['upper_cap'] =="":
			x = ''
		else:
			x = float(request.POST['upper_cap'])
		
		if request.POST['lower_cap'] =="":
			y = ''
		else:
			y = float(request.POST['lower_cap'])
		if request.POST['agg_cap'] =="":
			a = ''
		else:
			a = float(request.POST['agg_cap'])
		if request.POST['agg_cap_lower'] =="":
			b = ''
		else:
			b = float(request.POST['agg_cap_lower'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+filename)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'SMCAP' in df:
				if row_count > 0 and 'SMCAP' in df:
					if(x =="" and y =="" and a =="" and b ==""):
						row_count = len(df.axes[0])
						df['weight'] = 1/row_count
					else:
						""" Caping """
						df['weight'] = df['SMCAP']/df['SMCAP'].sum()
						df['weight'] = df['weight']*100
						
						if(x!=''):
							count = df['ISIN'][df['weight'] > x].count()
							while count > 0:
								excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
								sum_1 =  df['weight'][df['weight'] < x].sum()
								for i in range(len(df)):
									if df.iloc[i]['weight'] >= x:
										df.at[i,'weight'] = x
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
								count = df['ISIN'][df['weight'] > x].count()
						
						if(y!=''):
							count = df['ISIN'][df['weight']<y].count()
							while count > 0:
								less_sum = -df['weight'][df['weight']<y].sum()+(count*y)
								sum_1 =  df['weight'][ df['weight']>y].sum()
								sum_2 = df['weight'][ df['weight']>=x].sum() 
								sum_1 = sum_1 - sum_2
								for i in range(len(df)):
									if df.iloc[i]['weight']<=y:
										df.at[i,'weight'] = y
									elif df.iloc[i]['weight']<x and df.iloc[i]['weight']>y:
										df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_1)*(less_sum) 
								count = df['ISIN'][df['weight'] <y].count()

						if(a!='' and b!=''):
							
							df['cap'] = ''
							for i in range(len(df)):
								if df.iloc[i]['weight'] == y:
									df.at[i,'cap'] = 1
								else:
									df.at[i,'cap'] = 0
									
							df = df.sort_values(by='weight',ascending=False)
							df = df.reset_index(drop=True) 
							count_cap = df['ISIN'][df['cap'] == 1].count()

							Sum_Agg = 0
							j = 0
							#a = float(input("Aggregate cap")) 
							for i in range(len(df)):
								if Sum_Agg <= a:
									Sum_Agg = Sum_Agg + df.iloc[i]['weight']
									j = i-1
								else:
									Sum_Agg = Sum_Agg
									
							df1 = df.loc[0:j,:]
							df2 = df.loc[j+1: len(df)-(count_cap+1),:]
							df2 = df2.reset_index(drop=True)
							df3 = df.loc[len(df)-count_cap:len(df)-1,:]

							#b = float(input("Agg_cap_lower")) 
							count = df2['ISIN'][df2['weight'] > b].count()
							while count > 0:
								excess_sum = df2['weight'][df2['weight'] > b].sum() - (count*b)
								sum_1 =  df2['weight'][df2['weight'] < b].sum()
								for i in range(len(df2)):
									if df2.iloc[i]['weight'] >= b:
										df2.at[i,'weight'] = b
									else:
										df2.at[i,'weight'] = df2.iloc[i]['weight'] + (df2.iloc[i]['weight']/sum_1)*(excess_sum) 
								count = df2['ISIN'][df2['weight'] > b].count()

							df = pd.concat([df1,df2,df3])
					
					
					
					df.to_csv('staticfiles/upload/'+dt_time+filename,index=False)
					""" To download csv file """
					url = 'staticfiles/upload/'+dt_time+filename
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+filename
					return response
				else:
					context = { 'message' : Blank_File }
			else:
				context = { 'message' : Not_ISIN_SMCAP }	
		else:
			context = { 'message' : Invalid_File }
		return render(request,templateName,context)
	else:
		context = {}
		return render(request, templateName, context)
		
		
		
		
		
def upr_cap_weight_post(request):
	templateName = 'wc/upr_cap.html'
	if request.method == 'POST':

		if request.POST['upper_cap'] =="":
			context = {}
		else:
			x = float(request.POST['upper_cap'])
			f = request.FILES['upload_file']
			filename = f.name
			if filename.endswith('.csv'):
				dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
				upl_status = handle_uploaded_file(f)
				df = pd.read_csv('staticfiles/upload/'+dt_time+filename)
				row_count = len(df.axes[0])
				#print(row_count)
				if 'ISIN' in df:
					if row_count > 0:
						df = df.sort_values(by='SMCAP',ascending=False)
						df = df.reset_index(drop=True)
						df['weight'] = df['SMCAP']/df['SMCAP'].sum()
						df['weight'] = df['weight']*100
						
						""" Caping """
						count = df['ISIN'][df['weight'] > x].count()
						while count > 0:
							excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
							sum_1 =  df['weight'][df['weight'] < x].sum()
							for i in range(len(df)):
								if df.iloc[i]['weight'] >= x:
									df.at[i,'weight'] = x
								else:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
							count = df['ISIN'][df['weight'] > x].count()
						   
						for i in range(len(df)):
								df.at[i,'cap'] = 0

						excess_sum = 0
						for i in range(len(df)):
							if i<2:
								if df.iloc[i]['weight']>=8:
									excess_sum = excess_sum + df.iloc[i]['weight']-8
									df.at[i,'weight'] = 8
									df.at[i,'cap'] = 1
								   
							if i==2:
								if df.iloc[i]['weight']>=7:
									excess_sum = excess_sum + df.iloc[i]['weight']-7
									df.at[i,'weight'] = 7
									df.at[i,'cap'] = 1
							if i==3:
								if df.iloc[i]['weight']>=6.5:
									excess_sum = excess_sum + df.iloc[i]['weight']-6.5
									df.at[i,'weight'] = 6.5 
									df.at[i,'cap'] = 1
							if i==4:
								if df.iloc[i]['weight']>=6:
									excess_sum = excess_sum + df.iloc[i]['weight']-6
									df.at[i,'weight'] = 6
									df.at[i,'cap'] = 1
							if i==5:
								if df.iloc[i]['weight']>=5.5:
									excess_sum = excess_sum + df.iloc[i]['weight']-5.5
									df.at[i,'weight'] = 5.5
									df.at[i,'cap'] = 1
							if i==6:
								if df.iloc[i]['weight']>=5:
									excess_sum = excess_sum + df.iloc[i]['weight']-5
									df.at[i,'weight'] = 5 
									df.at[i,'cap'] = 1
							if i>6:
								if df.iloc[i]['weight']>=4.5:
									excess_sum = excess_sum + df.iloc[i]['weight']-4.5
									df.at[i,'weight'] = 4.5
									df.at[i,'cap'] = 1

						sum_1 = 0                
						for i in range(len(df)):
							if df.iloc[i]['cap'] == 0:
								sum_1 = sum_1 + df.iloc[i]['weight']
									
									
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if i<2:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>8:
										excess_sum = excess_sum - (8-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 8
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
										
									   
								if i==2:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>7:
										excess_sum = excess_sum - (7-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 7
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
								if i==3:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>6.5:
										excess_sum = excess_sum - (6.5-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 6.5
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
								if i==4:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>6:
										excess_sum = excess_sum - (6-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 6
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
								if i==5:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>5.5:
										excess_sum = excess_sum - (5.5-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 5.5
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
								if i==6:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>5:
										excess_sum = excess_sum - (5-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 5
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
								if i>6:
									if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>4.5:
										excess_sum = excess_sum - (4.5-df.iloc[i]['weight'])
										sum_1 = sum_1-df.iloc[i]['weight']
										df.at[i,'weight'] = 4.5
									else:
										df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
					
						df.to_csv('staticfiles/upload/'+dt_time+filename,index=False)
						""" To download csv file """
						url = 'staticfiles/upload/'+dt_time+filename
						f = open(url, 'r')
						response = HttpResponse(f, content_type='text/csv')
						response['Content-Disposition'] = 'attachment; filename='+dt_time+filename
						return response
					else:
						context = { 'message' : Blank_File }
				else:
					context = { 'message' : Not_SMCAP }
			else:
				context = { 'message' : Invalid_File }
		return render(request,templateName,context)
			
	else:
		context = {}
		return render(request, templateName, context)
		

def ul_top_remain_secu_weight_post(request):
	templateName = 'wc/ul_top_remain_secu.html'
	if request.method == 'POST':

		if request.POST['upper_cap'] =="":
			context = {}
			return render(request, templateName, context)
		else:
			x = float(request.POST['upper_cap'])
			y = float(request.POST['lower_cap'])
			a = float(request.POST['top_cap'])
			b = float(request.POST['remain_cap'])
			c = float(request.POST['securities'])
			
			f = request.FILES['upload_file']
			filename = f.name
			if filename.endswith('.csv'):
				dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
				upl_status = handle_uploaded_file(f)
				df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
				row_count = len(df.axes[0])
				#print(row_count)
				if 'ISIN' in df and 'SMCAP' in df:
					if row_count > 0:
						df['weight'] = df['SMCAP']/df['SMCAP'].sum()
						df['weight'] = df['weight']*100
						df = df.sort_values(by='weight',ascending= False)
						df = df.reset_index(drop=True)
					
						""" Caping """
						count = df['ISIN'][df['weight'] > x].count()
						while count > 0:
							excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
							sum_1 =  df['weight'][df['weight'] < x].sum()
							for i in range(len(df)):
								if df.iloc[i]['weight'] >= x:
									df.at[i,'weight'] = x
								else:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
							count = df['ISIN'][df['weight'] > x].count()

						sum = 0 
						for i in range(len(df)):
							if i<c:
								sum = sum + df.iloc[i]['weight']
							else:
								break
								
						if sum>a:
							for i in range(len(df)):
								if i<c:
									df.at[i,'weight'] = a/c
								else:
									break     

						excess_sum = sum-a 

						count = 0
						for i in range(len(df)):
							if i>a-1:
								if df.iloc[i]['weight']>b:
									count=count+1
									  
						while count>0:
							for i in range(len(df)):
								if i>a-1:
									if df.iloc[i]['weight']>b:
										excess_sum = excess_sum + df.iloc[i]['weight']-b
										df.at[i,'weight']= b
							rest_sum=0 
							for i in range(len(df)):
								if i>a-1:
									if df.iloc[i]['weight']<b:
										rest_sum = rest_sum+df.iloc[i]['weight']
							for i in range(len(df)):
								if i>a-1:
									if df.iloc[i]['weight']<b:
										df.at[i,'weight']=df.iloc[i]['weight']+(df.iloc[i]['weight']/rest_sum)*excess_sum 
							count = 0
							excess_sum=0
							for i in range(len(df)):
								if i>a-1:
									if df.iloc[i]['weight']>b:
										count=count+1
																	
										 
						count = df['ISIN'][df['weight']<y].count()


						while count > 0:
							less_sum = -df['weight'][df['weight']<y].sum()+(count*y)
							sum_1 =  df['weight'][ df['weight']>y].sum()
							sum_2 = df['weight'][ df['weight']>=b].sum() 
							sum_1 = sum_1 - sum_2
							for i in range(len(df)):
								if df.iloc[i]['weight']<=y:
									df.at[i,'weight'] = y
								elif df.iloc[i]['weight']<b and df.iloc[i]['weight']>y:
									df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_1)*(less_sum) 
							count = df['ISIN'][df['weight'] <y].count()
					
						df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
						""" To download csv file  """
						url = 'staticfiles/upload/'+dt_time+f.name
						f = open(url, 'r')
						response = HttpResponse(f, content_type='text/csv')
						response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
						return response
					else:
						context = { 'message' : Blank_File}
				else:
					context = { 'message' : Not_ISIN_SMCAP}
			else:
				context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)

		


def mlp_sector_post(request):
	templateName = 'wc/mlp_sector.html'

	if request.method == 'POST':
		mlp_cap = float(request.POST['mlp_cap'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			if 'ISIN' in df and 'MLP' in df and 'Sector' in df:
				if row_count > 0:
					df['weight'] = 1/df['ISIN'].count()
					if request.POST['sector_weight'] =="":
						sum = 0
						for i in range(len(df)):
							if df.iloc[i]['MLP']==1:
								sum = sum + df.iloc[i]['weight']
									
									
						rest = 100 - sum          
						if sum>mlp_cap:
							excess_sum = sum-mlp_cap  
							for i in range(len(df)):
								if df.iloc[i]['MLP']==0:
									df.at[i,'weight'] =  df.iloc[i]['weight'] +  (df.iloc[i]['weight']/rest)*excess_sum
								else:
									df.at[i,'weight'] =  df.iloc[i]['weight']-(df.iloc[i]['weight']/sum)*excess_sum
					else:
						sector_weight = float(request.POST['sector_weight'])
						y = df.groupby('Sector')['weight'].sum().reset_index()
						count = y['Sector'][y['weight'] > sector_weight].count()
						x =[]
						while count>0:
							x = df.groupby('Sector')['weight'].sum().reset_index()
							x['ans'] = x['weight']-sector_weight
							
							for i in range(len(df)):
								for j in range(len(x)):
									if  df.iloc[i]['Sector']==x.iloc[j]['Sector']:
										df.at[i,'new'] = x.iloc[j]['ans']
										df.at[i,'cum'] = x.iloc[j]['weight']
										  
							sum = 0
							for i in range(len(df)) :
								if  df.iloc[i]['new']>0:
									sum = sum +  ((df.iloc[i]['weight']/df.iloc[i]['cum'])*df.iloc[i]['new'])
									df.at[i,'weight'] = df.iloc[i]['weight']-((df.iloc[i]['weight']/df.iloc[i]['cum'])*df.iloc[i]['new'])
										  
							sum1 = 0                                 
							for i in range(len(df)) :
								if  df.iloc[i]['new']<0:
									sum1 = sum1 + df.iloc[i]['weight']
											
							for i in range(len(df)) :
								if  df.iloc[i]['new']<0:
									df.at[i,'weight'] = df.iloc[i]['weight']+((df.iloc[i]['weight']/sum1)*sum)

							count = x['Sector'][x['weight'] > sector_weight].count()

						##Checking the sectors with weights capped
						sector_cap = []
						for i in range(len(x)):
							if x.iloc[i]['weight'] == sector_weight:
								sector_cap.append(x.iloc[i]['Sector'])

						for i in range(len(df)):
							if df.iloc[i]['Sector'] in sector_cap:
								df.at[i,'cap'] = 1

						##Applying the MLP Cap
						sum_MLP = df['weight'][df['MLP']==1].sum()
						while sum_MLP>mlp_cap:
							excess_sum = sum_MLP - mlp_cap
							sum_cap = df['weight'][df['cap'] != 1][df['MLP'] !=1].sum() 
							for i in range(len(df)):
								if df.iloc[i]['MLP'] == 1:
									df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_MLP*excess_sum)
								if df.iloc[i]['MLP'] != 1 and df.iloc[i]['cap'] != 1:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_cap*excess_sum)    
							sum_MLP = df['weight'][df['MLP']==1].sum()
								
							df.groupby('Sector')['weight'].sum().reset_index()
					
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
						context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_MLP_SECTOR}	
		else:
			context = { 'message' : Invalid_File }
		return render(request,templateName,context)		
	else:
		context = {}
		return render(request, templateName, context)

def sing_sec_agg_post(request):
	templateName = 'wc/sing_sec_agg.html'
	if request.method == 'POST':
		agg_weight = float(request.POST['agg_weight'])
		sing_sec_cap = float(request.POST['sing_sec_cap'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			if 'SMCAP' in df and 'Classification' in df:
				if row_count > 0:
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight'] = df['weight']*100
					for i in range(len(df)):
						df.at[i,'flag'] = 0


					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Pure-Play':
							df.at[i,'cap'] = 1
						else:
							df.at[i,'cap'] = 0
								
					quasi = 0

					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							quasi = quasi + df.iloc[i]['weight'] 
								
					give = quasi - agg_weight
					pure =  100-quasi
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							df.at[i,'weight']= df.iloc[i]['weight']-(df.iloc[i]['weight']/quasi)*give
						else:
							df.at[i,'weight']= df.iloc[i]['weight']+(df.iloc[i]['weight']/pure)*give

					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['weight']>sing_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-sing_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']

					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>sing_sec_cap:
										df.at[i,'weight']=sing_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['weight']>sing_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-sing_sec_cap
								elif df.iloc[i]['weight']==sing_sec_cap:
									capped = capped + 1
								else:
									sum_1 = sum_1 + df.iloc[i]['weight']            
								
								

					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['weight']>sing_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-sing_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']

					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>sing_sec_cap:
										df.at[i,'weight']=sing_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['weight']>sing_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-sing_sec_cap
								elif df.iloc[i]['weight']==sing_sec_cap:
									capped = capped + 1      
								else:
									sum_1 = sum_1 + df.iloc[i]['weight']
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_SMCAP_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)


def us_sharing_post(request):
	templateName = 'wc/us_sharing.html'
	if request.method == 'POST':
		pure_weight = float(request.POST['pure_weight'])
		quasi_marginal = float(request.POST['quasi_marginal'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'Classification' in df:
				if row_count > 0:
					all = df['ISIN'].count()
					a = df['ISIN'][df['Classification']=='Pure-Play'].count()

					print(a)
					rest = all - a

					pweight = pure_weight/a
					rest_weight = 100 - pure_weight

					for i in range(len(df)):
						if df.iloc[i]['Classification'] == 'Pure-Play':
							df.at[i,'Weight'] = pweight
						else:
							df.at[i,'Weight'] = rest_weight/rest
							 
								
								
					excess_sum = 0            

					for i in range(len(df)):
						if df.iloc[i]['Classification'] != 'Pure-Play':
							if  df.at[i,'Weight']> pweight:
								excess_sum = excess_sum + df.iloc[i]['Weight']-quasi_marginal
								df.at[i,'Weight'] = quasi_marginal 
								   
								   
					for i in range(len(df)):
						if df.iloc[i]['Classification'] == 'Pure-Play' :
							df.at[i,'Weight']=df.iloc[i]['Weight'] + excess_sum/a 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)



def global_space_post(request):
	templateName = 'wc/global_space.html'
	if request.method == 'POST':
		sing_sec_cap = float(request.POST['sing_sec_cap'])
		quasi_cap = float(request.POST['quasi_cap'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'SMCAP' in df and 'Classification' in df:
				if row_count > 0:
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight'] = df['weight']*100 

					count = 0 
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Pure-Play':
							if df.iloc[i]['weight']>sing_sec_cap:
								count = count + 1 

					af = df[df['Classification']=='Pure-Play']
					bf = df[df['Classification']=='Quasi-Play']

					pexcess_sum = 0

					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Pure-Play':
							if df.iloc[i]['weight'] > sing_sec_cap:
								pexcess_sum = pexcess_sum + df.iloc[i]['weight']-sing_sec_cap
								df.at[i,'weight'] = sing_sec_cap
							
							
					qexcess_sum = 0

					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Quasi-Play':
							if df.iloc[i]['weight'] > 1:
								qexcess_sum = qexcess_sum + df.iloc[i]['weight']-1
								df.at[i,'weight'] = 1

					af = df[df['Classification']=='Pure-Play']
					bf = df[df['Classification']=='Quasi-Play']        
					x=af['weight'].sum()  
					y=bf['weight'].sum()

					rest = quasi_cap - y
					qexcess_sum = qexcess_sum-rest
					pexcess_sum = pexcess_sum + qexcess_sum
					sum1 = af['weight'][af['weight']<sing_sec_cap].sum()
					sum2 = bf['weight'][bf['weight']<1].sum() 


					df = df.sort_values(['weight'],ascending= [False])
					df = df.reset_index(drop=True)
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Pure-Play':
							if df.iloc[i]['weight'] < sing_sec_cap:
								if(df.iloc[i]['weight'] + [(df.iloc[i]['weight']/sum1)*(pexcess_sum )])> sing_sec_cap: 
									sum1 = sum1 - df.iloc[i]['weight'];
									pexcess_sum = pexcess_sum -(sing_sec_cap-df.iloc[i]['weight'])
									df.at[i,'weight'] = sing_sec_cap
								else:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum1)*(pexcess_sum) 
									
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Quasi-Play':
							if df.iloc[i]['weight'] < 1:
								if df.iloc[i]['weight'] + [(df.iloc[i]['weight']/sum2)*(rest)] > 1:
									sum2 = sum2 - df.iloc[i]['weight']  ;
									rest = rest -(1-df.iloc[i]['weight'])
									df.at[i,'weight'] = 1
								else:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum2)*rest    
									
					df = df.sort_values(['Classification','weight'],ascending= [True,False])
					df = df.reset_index(drop=True)

					af = df[df['Classification']=='Pure-Play']
					bf = df[df['Classification']=='Quasi-Play']        
					x=af['weight'].sum()  
					y=bf['weight'].sum()

					if y < quasi_cap:
						excess = quasi_cap - y
						sum = 0
						for i in range(len(df)):
							if df.iloc[i]['Classification']=='Pure-Play':
								if df.iloc[i]['weight'] < sing_sec_cap:
									sum = sum + df.iloc[i]['weight']
					   
						for i in range(len(df)):
							if df.iloc[i]['Classification']=='Pure-Play':
								if df.iloc[i]['weight'] < sing_sec_cap:
									if(df.iloc[i]['weight'] + [(df.iloc[i]['weight']/sum)*(excess )])> sing_sec_cap: 
										sum = sum - df.iloc[i]['weight'];
										excess = excess -(sing_sec_cap-df.iloc[i]['weight'])
										df.at[i,'weight'] = sing_sec_cap
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum)*(excess) 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_SMCAP_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)


def private_credit_post(request):
	templateName = 'wc/private_credit.html'
	if request.method == 'POST':
		upper_cap = float(request.POST['upper_cap'])
		lower_cap = float(request.POST['lower_cap'])
		Capitalization = float(request.POST['capitalization'])
		ADTV = float(request.POST['adtv'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'MCAP' in df and 'Dividend Yield' in df and 'Classification (BDC/CEF)' in df and 'ADTV' in df:
				if row_count > 0:
					df['weight'] = df['Dividend Yield']/df['Dividend Yield'].sum()
					df['weight']=df['weight']*100

					sum = 0 
					sum1 = 0
					df['Classification']=df['Classification (BDC/CEF)']

					df['ans'] = 1
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='BDC':
							if df.iloc[i]['ADTV'] < ADTV or df.iloc[i]['MCAP'] < Capitalization:
								sum = sum + df.iloc[i]['weight']-1 
								df.at[i,'weight']=1
								df.at[i,'ans']=0
							else:
								sum1 = sum1 + df.iloc[i]['weight']
						
						else:
							sum1 = sum1 + df.iloc[i]['weight']

					for i in range(len(df)):
						if df.iloc[i]['ans']==1:
						  df.at[i,'weight']= df.iloc[i]['weight']+(df.iloc[i]['weight']/sum1)*sum
									  
					df = df.sort_values(['ans','weight'],ascending= [False,False])     

					# upper_cap should be greater than 1 and lower_cap should be less than 1 
					
					count = df['ISIN'][df['weight'] > upper_cap].count()
					while count > 0:
						excess_sum = 0
						for i in range(len(df)):
							if df.iloc[i]['ans']==1:
								if df.iloc[i]['weight']>upper_cap:
								   excess_sum = excess_sum+ df.iloc[i]['weight']
						excess_sum = excess_sum - count 
						sum1 = 0
						for i in range(len(df)):
							if df.iloc[i]['ans']==1:
								if df.iloc[i]['weight']<upper_cap:
									sum1= sum1 + df.iloc[i]['weight']
						
						for i in range(len(df)):
							if df.iloc[i]['ans']==1:
								if df.iloc[i]['weight'] >= upper_cap:
									df.at[i,'weight'] = upper_cap
								else:
									df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum1)*(excess_sum) 
						count = df['ISIN'][df['weight'] > upper_cap].count()
					 
					count = df['ISIN'][df['weight']<lower_cap].count()


					while count > 0:
						less_sum = -df['weight'][df['weight']<lower_cap].sum()+(count*lower_cap)
						sum_1 =  df['weight'][ df['weight']>lower_cap].sum()
						sum_2 =  df['weight'][ df['weight']>=upper_cap].sum() 
						sum_3 = df['weight'][df['ans']==0]
						sum_1 = sum_1 - sum_2 - sum_3
						for i in range(len(df)):
							if df.iloc[i]['weight']==1:
								if df.iloc[i]['weight']<=lower_cap:
									df.at[i,'weight'] = lower_cap
								elif df.iloc[i]['weight']<upper_cap and df.iloc[i]['weight']>lower_cap:
									df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_1)*(less_sum) 
						count = df['ISIN'][df['weight'] <lower_cap].count() 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_MCAP_ADTV_Dividend_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)


def g5_nextg_post(request):
	templateName = 'wc/g5_nextg.html'
	if request.method == 'POST':
		agg_weight = float(request.POST['agg_weight'])
		mcap_cap = float(request.POST['mcap_cap'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'MCAP' in df and 'Theme' in df:
				if row_count > 0:
					a = df['ISIN'][df['Theme']=='5G Infrastructure & Hardware'].count()
					b = df['ISIN'][df['Theme']=='Telecommunications Service Providers'].count()


					for i in range(len(df)):
						if df.iloc[i]['Theme'] == '5G Infrastructure & Hardware' :
							df.at[i,'weight'] = agg_weight/a
						elif df.iloc[i]['Theme'] == 'Telecommunications Service Providers' :
							df.at[i,'weight'] = (100-agg_weight)/b     
								  
					 

					excess_sum_a = 0 
					excess_sum_b=0
					c = 0
					d = 0
					for i in range(len(df)):
						if df.iloc[i]['Theme'] == '5G Infrastructure & Hardware' :
							if df.iloc[i]['MCAP']<mcap_cap:
								excess_sum_a = excess_sum_a+df.iloc[i]['weight']/2
								df.at[i,'weight'] = df.iloc[i]['weight']/2
								c=c+1
						elif df.iloc[i]['Theme'] == 'Telecommunications Service Providers' :
							if df.iloc[i]['MCAP']<mcap_cap: 
								excess_sum_b = excess_sum_b + df.iloc[i]['weight']/2
								df.at[i,'weight'] = df.iloc[i]['weight']/2 
								d=d+1
											   
									
					for i in range(len(df)):
						if df.iloc[i]['Theme'] == '5G Infrastructure & Hardware' :
							if df.iloc[i]['MCAP']>mcap_cap:
								df.at[i,'weight'] = df.iloc[i]['weight']+excess_sum_a/(a-c)
						elif df.iloc[i]['Theme'] == 'Telecommunications Service Providers' :
							if df.iloc[i]['MCAP']>mcap_cap: 
								df.at[i,'weight'] = df.iloc[i]['weight'] + excess_sum_b/(b-d) 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_MCAP_THEME}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)
		
		
		
def ai_big_data_post(request):
	templateName = 'wc/ai_bigdata.html'
	if request.method == 'POST':
		upper_cap = float(request.POST['upper_cap'])
		lower_cap = float(request.POST['lower_cap'])
		security_cap = float(request.POST['security_cap'])
		score = float(request.POST['score'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'SMCAP' in df and 'Score' in df:
				if row_count > 0:
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight'] = df['weight']*100
					df['Score']=df['Score']*100

					for i in range(len(df)):
						df.at[i,'cap'] = 0
						
					x = upper_cap
					y = lower_cap    

					excess_sum = 0
					sum_x = 0
					count = 0

					for i in range(len(df)):
						if df.iloc[i]['Score'] >=score and df.iloc[i]['weight']>3:
							count = count+1
						if df.iloc[i]['Score'] <score and df.iloc[i]['weight']>1:                
							count = count+1
					while count >0:
						excess_sum = 0
						sum_x = 0
						count = 0
						for i in range(len(df)):
							if df.iloc[i]['Score'] <score and df.iloc[i]['weight'] >1:
								excess_sum = excess_sum + (df.iloc[i]['weight']-1)
								df.at[i,'weight'] = 1
								df.at[i,'cap']=1
							if df.iloc[i]['Score'] >=score and df.iloc[i]['weight'] >security_cap:
								excess_sum = excess_sum + (df.iloc[i]['weight']-security_cap)
								df.at[i,'weight'] = security_cap
								df.at[i,'cap'] = 1
							if df.iloc[i]['cap'] == 0:
								sum_x = sum_x + df.iloc[i]['weight']
						for i in range(len(df)):
							if df.iloc[i]['cap'] ==0:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_x)*excess_sum
						for i in range(len(df)):
							if df.iloc[i]['Score'] >=score and df.iloc[i]['weight']>security_cap:
								count = count+1
							if df.iloc[i]['Score'] <score and df.iloc[i]['weight']>1:                
								count = count+1

					count = df['ISIN'][df['weight']<y].count()    
					while count > 0:
						less_sum = -df['weight'][df['weight']<y].sum()+(count*y)
						sum_1 = 0
						for i in range(len(df)):               
							if df.iloc[i]['cap']==0: 
								if df.iloc[i]['weight']>y:
									sum_1 = sum_1 + df.iloc[i]['weight']
						for i in range(len(df)):
							if df.iloc[i]['weight']<=y:
								df.at[i,'weight'] = y
							elif df.iloc[i]['cap']==0 and df.iloc[i]['weight']>y:
								df.at[i,'weight'] = df.iloc[i]['weight'] - (df.iloc[i]['weight']/sum_1)*(less_sum) 
						count = df['ISIN'][df['weight'] <y].count() 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_SMCAP_Score}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)



def blockchain_post(request):
	templateName = 'wc/blockchain.html'
	if request.method == 'POST':
		mcap_cap = float(request.POST['mcap_cap'])
		index_cap = float(request.POST['index_cap'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'SMCAP' in df and 'ADTV3M' in df and 'ADTV20D' in df and 'Classification' in df:
				if row_count > 0:
					a = df['ISIN'][df['Classification']=='Active Enablers'].count()
					b = df['ISIN'][df['Classification']=='Active Users'].count()

					weight_a = 50/a
					weight_b = 50/b
					excess_sum = 0 
					flag = 0

					for i in range(len(df)):
						df.at[i,'cap'] = 0

					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Active Enablers':
							if df.iloc[i]['MCAP']<mcap_cap and df.iloc[i]['ADTV3M']<3 and df.iloc[i]['ADTV20D']<3:
								df.at[i,'weight'] = index_cap
								excess_sum = excess_sum+(weight_a-index_cap)
								df.at[i,'cap'] = 1
								flag = 1
							else:
								df.at[i,'weight']=weight_a
						else:
							df.at[i,'weight'] = weight_b
								
					count = 0            
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Active Enablers':
							if df.at[i,'cap'] ==0:
								count = count + 1 
									
					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Active Enablers':
							if df.at[i,'cap'] ==0:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (excess_sum/count) 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_SMCAP_ADTV3M_ADTV20D_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)


def global_aerospace_post(request):
	templateName = 'wc/global_aerospace.html'
	if request.method == 'POST':
		capped = float(request.POST['capped'])
		weight_cap = float(request.POST['weight_cap'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'SMCAP' in df and 'Domicile' in df:
				if row_count > 0:
					df['weight']=df['SMCAP']/df['SMCAP'].sum()
					df['weight']=df['weight']*100

					x = float(input("upper cap"))
					count = df['ISIN'][df['weight'] > x].count()
					
					while count > 0:
						excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
						sum_1 =  df['weight'][df['weight'] < x].sum()
						for i in range(len(df)):
							if df.iloc[i]['weight'] >= x:
								df.at[i,'weight'] = x
							else:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
						count = df['ISIN'][df['weight'] > x].count()



					sum = 0 
					for i in range(len(df)):
						if df.iloc[i]['Domicile']=='United States':
							sum = sum + df.iloc[i]['weight'] 

					excess_sum = 0         
					restsum = 100-sum         
						
					if sum>capped:
						excess_sum = sum - capped
						for i in range(len(df)):
							if df.iloc[i]['Domicile']=='United States':
								df.at[i,'weight']=df.iloc[i]['weight']-(df.iloc[i]['weight']/sum)*excess_sum
							else:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/100-sum)*excess_sum<weight_cap:
									df.at[i,'weight']=df.iloc[i]['weight']+(df.iloc[i]['weight']/restsum)*excess_sum
								else:
									restsum = restsum - df.iloc[i]['weight']
									excess_sum = excess_sum - (weight_cap-df.iloc[i]['weight'])
									df.at[i,'weight'] = weight_cap 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_SMCAP_Domicile}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)
		
		
		
def global_cloud_computing_post(request):
	templateName = 'wc/global_cloud_computing.html'
	if request.method == 'POST':
		reit_capped = float(request.POST['reit_capped'])
		security_floor = float(request.POST['security_floor'])
		reit_sec_cap = float(request.POST['reit_sec_cap'])
		public_sec_cap = float(request.POST['public_sec_cap'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'SMCAP' in df and 'Theme' in df:
				if row_count > 0:
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight'] = df['weight']*100
					df['cap'] = 0
					df['flag']=0
					for i in range(len(df)):
						if df.iloc[i]['Theme'] == 'Public Cloud':
							df.at[i,'cap'] = public_sec_cap
						elif df.iloc[i]['Theme'] == 'Data Centre Reits':
							df.at[i,'cap'] = 1
						else:
							df.at[i,'cap'] = 0
							
					cloud = 0

					for i in range(len(df)):
						if df.iloc[i]['cap']==public_sec_cap:
							cloud = cloud + df.iloc[i]['weight']        
								
					give = cloud - reit_capped
					pure =  100-cloud     

					for i in range(len(df)):
						if df.iloc[i]['cap']==public_sec_cap:
							df.at[i,'weight']= df.iloc[i]['weight']-(df.iloc[i]['weight']/cloud)*give
						else:
							df.at[i,'weight']= df.iloc[i]['weight']+(df.iloc[i]['weight']/pure)*give    
								
								
					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==public_sec_cap:
							if df.iloc[i]['weight']>public_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-public_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']     
						else:
							sum_1 = sum_1 + df.iloc[i]['weight'] 


					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==public_sec_cap:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>public_sec_cap:
										df.at[i,'weight']=public_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)      
							else:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==public_sec_cap:
								if df.iloc[i]['weight']>public_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-public_sec_cap
								if  df.iloc[i]['weight']<public_sec_cap: 
									sum_1 = sum_1 + df.iloc[i]['weight'] 
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']  
							   

					count = 0 
					sum = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==public_sec_cap:
							if df.iloc[i]['weight']<security_floor:
								count = count + 1
								sum = sum + df.iloc[i]['weight']
								df.at[i,'weight']=security_floor
								df.at[i,'flag']=1
							   

					less = 0.3*count-sum

					total = 0
					for i in range(len(df)):
						if df.iloc[i]['flag']==0:
							total = total + df.iloc[i]['weight']
								   
					for i in range(len(df)):
						if df.iloc[i]['flag']==0:
							df.at[i,'weight'] = df.iloc[i]['weight']-(df.iloc[i]['weight']/total)*(less)
								   
								   
					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['weight']>reit_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-reit_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']     
						if df.iloc[i]['cap']==0:
							sum_1 = sum_1 + df.iloc[i]['weight'] 


					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>reit_sec_cap:
										df.at[i,'weight']=reit_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)      
							if df.iloc[i]['cap']==0:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['weight']>reit_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-reit_sec_cap
								if df.iloc[i]['weight']<reit_sec_cap: 
									sum_1 = sum_1 + df.iloc[i]['weight'] 
							if df.iloc[i]['cap']==0:
								sum_1 = sum_1 + df.iloc[i]['weight']                 
								   


					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['weight']>reit_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-reit_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']     
						 


					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>reit_sec_cap:
										df.at[i,'weight']=reit_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)      
						
							 

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['weight']>reit_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-reit_sec_cap
								if df.iloc[i]['weight']<reit_sec_cap: 
									sum_1 = sum_1 + df.iloc[i]['weight'] 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_SMCAP_Theme}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)


def global_ecomm_post(request):
	templateName = 'wc/global_ecomm.html'
	if request.method == 'POST':
		stocks2_capped = float(request.POST['stocks2_capped'])
		stocks3_capped = float(request.POST['stocks3_capped'])
		stocks4_capped = float(request.POST['stocks4_capped'])
		stocks5_capped = float(request.POST['stocks5_capped'])
		stocks6_capped = float(request.POST['stocks6_capped'])
		stocks7_capped = float(request.POST['stocks7_capped'])
		stocks_other_capped = float(request.POST['stocks_other_capped'])
		final_constituents = float(request.POST['final_constituents'])
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'ISIN' in df and 'SMCAP' in df and 'Primary Listing' in df:
				if row_count > 0:
					df = df.sort_values(by='SMCAP',ascending=False)
					df = df.reset_index(drop=True)
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight'] = df['weight']*100

					x = float(input("upper cap"))

					count = df['ISIN'][df['weight'] > x].count()
					while count > 0:
						excess_sum = df['weight'][df['weight'] > x].sum() - (count*x)
						sum_1 =  df['weight'][df['weight'] < x].sum()
						for i in range(len(df)):
							if df.iloc[i]['weight'] >= x:
								df.at[i,'weight'] = x
							else:
								df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum) 
						count = df['ISIN'][df['weight'] > x].count()


					for i in range(len(df)):
						df.at[i,'cap'] = 0


					excess_sum = 0
					for i in range(len(df)):
						if i<2:
							if df.iloc[i]['weight']>=stocks2_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks2_capped
								df.at[i,'weight'] = stocks2_capped
								df.at[i,'cap'] = 1
						
						if i==2:
							if df.iloc[i]['weight']>=stocks3_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks3_capped
								df.at[i,'weight'] = stocks3_capped
								df.at[i,'cap'] = stocks3_capped
						if i==3:
							if df.iloc[i]['weight']>=stocks4_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks4_capped
								df.at[i,'weight'] = stocks4_capped 
								df.at[i,'cap'] = 1
						if i==4:
							if df.iloc[i]['weight']>=stocks5_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks5_capped
								df.at[i,'weight'] = stocks5_capped
								df.at[i,'cap'] = 1
						if i==5:
							if df.iloc[i]['weight']>=stocks6_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks6_capped
								df.at[i,'weight'] = stocks6_capped
								df.at[i,'cap'] = 1
						if i==6:
							if df.iloc[i]['weight']>=stocks7_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks7_capped
								df.at[i,'weight'] = stocks7_capped 
								df.at[i,'cap'] = 1
						if i>6:
							if df.iloc[i]['weight']>=stocks_other_capped:
								excess_sum = excess_sum + df.iloc[i]['weight']-stocks_other_capped
								df.at[i,'weight'] = stocks_other_capped
								df.at[i,'cap'] = 1


					sum_1 = 0                
					for i in range(len(df)):
						if df.iloc[i]['cap'] == 0:
							sum_1 = sum_1 + df.iloc[i]['weight']



					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if i<2:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks2_capped:
									excess_sum = excess_sum - (stocks2_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks2_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							
							
							if i==2:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks3_capped:
									excess_sum = excess_sum - (stocks3_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks3_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							if i==3:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks4_capped:
									excess_sum = excess_sum - (stocks4_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks4_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							if i==4:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks5_capped:
									excess_sum = excess_sum - (stocks5_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks5_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							if i==5:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks6_capped:
									excess_sum = excess_sum - (stocks6_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks6_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							if i==6:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks7_capped:
									excess_sum = excess_sum - (stocks7_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks7_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum
							if i>6:
								if df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum>stocks_other_capped:
									excess_sum = excess_sum - (stocks_other_capped-df.iloc[i]['weight'])
									sum_1 = sum_1-df.iloc[i]['weight']
									df.at[i,'weight'] = stocks_other_capped
								else:
									df.at[i,'weight'] = df.iloc[i]['weight']+(df.iloc[i]['weight']/sum_1)*excess_sum


					del df['cap']    
					sum = 0
					for i in range(len(df)):
						if df.iloc[i]['Primary Listing'] == "UNITED STATES":
							sum = sum + df.iloc[i]['weight']

					isum = sum
					df = df.sort_values(by='weight',ascending=True)            
					if sum>final_constituents:  
						while sum>final_constituents:
							for i in range(len(df)):
								if df.iloc[i]['Primary Listing'] == "UNITED STATES":
									df=df.drop(df.index[[i]])
									df = df.reset_index(drop=True)
									break
							sum = 0
							for i in range(len(df)):
								if df.iloc[i]['Primary Listing'] == "UNITED STATES":
									sum = sum + df.iloc[i]['weight']
						excess_sum = isum-sum                                              
						for i in range(len(df)):
							if df.iloc[i]['Primary Listing'] == "UNITED STATES":
								df.at[i,'weight']=df.iloc[i]['weight']+(df.iloc[i]['weight']/sum)*excess_sum                      
						df = df.sort_values(by='weight',ascending=False)                     

					df = df.sort_values(by='weight',ascending=False) 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_ISIN_SMCAP_Primary_Listing}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)		

		
		
def global_iot_post(request):
	templateName = 'wc/global_iot.html'
	if request.method == 'POST':
		agg_cap = float(request.POST['agg_cap'])
		sign_sec_cap = float(request.POST['sign_sec_cap'])
		sign_sec_floor = float(request.POST['sign_sec_floor'])
		sign_sec_weight_cap = float(request.POST['sign_sec_weight_cap'])
		
		f = request.FILES['upload_file']
		filename = f.name
		if filename.endswith('.csv'):
			dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
			upl_status = handle_uploaded_file(f)
			df = pd.read_csv('staticfiles/upload/'+dt_time+f.name)
			row_count = len(df.axes[0])
			#print(row_count)
			if 'SMCAP' in df and 'Classification' in df:
				if row_count > 0:
					df['weight'] = df['SMCAP']/df['SMCAP'].sum()
					df['weight']=df['weight']*100

					for i in range(len(df)):
						df.at[i,'flag'] = 0

					for i in range(len(df)):
						if df.iloc[i]['Classification']=='Pure-Play':
							df.at[i,'cap'] = 1
						else:
							df.at[i,'cap'] = 0
								

					quasi = 0

					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							quasi = quasi + df.iloc[i]['weight']
								
					give = quasi - agg_cap
					pure =  100-quasi
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							df.at[i,'weight']= df.iloc[i]['weight']-(df.iloc[i]['weight']/quasi)*give
						else:
							df.at[i,'weight']= df.iloc[i]['weight']+(df.iloc[i]['weight']/pure)*give    
								
								
								
								
					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['weight']>sign_sec_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-sign_sec_cap
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']
							
								
								   

					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>sign_sec_cap:
										df.at[i,'weight']=sign_sec_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==1:
								if df.iloc[i]['weight']>sign_sec_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-sign_sec_cap
								elif df.iloc[i]['weight']==sign_sec_cap:
									capped = capped + 1
								else:
									sum_1 = sum_1 + df.iloc[i]['weight']            
								
								

					count = 0
					excess_sum = 0
					sum_1 = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['weight']>sign_sec_weight_cap:
								count = count + 1
								excess_sum = excess_sum + df.iloc[i]['weight']-sign_sec_weight_cap  
							else:
								sum_1 = sum_1 + df.iloc[i]['weight']
							
								
								   

					while count>0:
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['flag']==0:
									if df.iloc[i]['weight']>sign_sec_weight_cap:
										df.at[i,'weight']=sign_sec_weight_cap
										df.at[i,'flag'] = 1 
									else:
										df.at[i,'weight'] = df.iloc[i]['weight'] + (df.iloc[i]['weight']/sum_1)*(excess_sum)  

						
						count = 0
						excess_sum = 0
						sum_1 = 0
						capped = 0
						for i in range(len(df)):
							if df.iloc[i]['cap']==0:
								if df.iloc[i]['weight']>sign_sec_weight_cap:
									count = count + 1
									excess_sum = excess_sum + df.iloc[i]['weight']-sign_sec_weight_cap
								elif df.iloc[i]['weight']==sign_sec_weight_cap:
									capped = capped + 1      
								else:
									sum_1 = sum_1 + df.iloc[i]['weight']    
									   
									   
					count = 0 
					sum = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['weight']<sign_sec_floor:
								count = count + 1
								sum = sum + df.iloc[i]['weight']
								df.at[i,'weight']=sign_sec_floor
								df.at[i,'flag']=1
									   
					less = sign_sec_floor*count-sum

					total = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['flag']==0:
								total = total + df.iloc[i]['weight']
					for i in range(len(df)):
						if df.iloc[i]['cap']==0:
							if df.iloc[i]['flag']==0:
								df.at[i,'weight'] = df.iloc[i]['weight']-(df.iloc[i]['weight']/total)*(less)      
									   

					count = 0 
					sum = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['weight']<sign_sec_floor:
								count = count + 1
								sum = sum + df.iloc[i]['weight']
								df.at[i,'weight']=sign_sec_floor
								df.at[i,'flag']=1
									   
					less = sign_sec_floor*count-sum

					total = 0
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['flag']==0:
								total = total + df.iloc[i]['weight']
					for i in range(len(df)):
						if df.iloc[i]['cap']==1:
							if df.iloc[i]['flag']==0:
								df.at[i,'weight'] = df.iloc[i]['weight']-(df.iloc[i]['weight']/total)*(less)                     

					df = df.sort_values(by='weight',ascending=False) 
				
					df.to_csv('staticfiles/upload/'+dt_time+f.name,index=False)
					""" To download csv file  """
					url = 'staticfiles/upload/'+dt_time+f.name
					f = open(url, 'r')
					response = HttpResponse(f, content_type='text/csv')
					response['Content-Disposition'] = 'attachment; filename='+dt_time+f.name
					return response
				else:
					context = { 'message' : Blank_File}
			else:
				context = { 'message' : Not_SMCAP_Classification}
		else:
			context = { 'message' : Invalid_File}
		return render(request, templateName, context)
	else:
		context = {}
		return render(request, templateName, context)
		
##########   To upload file #############		
def handle_uploaded_file(f):
	dt_time = datetime.today().strftime('%Y-%m-%d_%H_%M_%S')
	with open('staticfiles/upload/'+dt_time+f.name, 'wb+') as destination:  
		for chunk in f.chunks():
			destination.write(chunk)
			
def back(request):
    templates = loader.get_template("wc/home.html")
    return HttpResponse(templates.render())