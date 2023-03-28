from xmlrpc.client import NOT_WELLFORMED_ERROR
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Meep, Comment, Networks, NetworkMembers
from .forms import MeepForm, SignUpForm, CommentForm, CreateNetworkForm, NetworkMembersForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.forms import formset_factory
import people_also_ask
from django.db import models
from django import forms

from django.forms import ModelMultipleChoiceField
# import .gitignore
import requests
# from decouple import config


# API_TOKEN = config('API_TOKEN')

API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
headers = {"Authorization": f"Bearer {'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'}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	

def toxicity(q):
	output = query({
	"inputs": q,})
	return output

"""
Example output:
toxicity(text)

[[{'label': 'toxic', 'score': 0.9984544515609741}, 
{'label': 'obscene', 'score': 0.9859963059425354}, 
{'label': 'insult', 'score': 0.8170381188392639}, 
{'label': 'severe_toxic', 'score': 0.36484864354133606}, 
{'label': 'threat', 'score': 0.020054737105965614}, 
{'label': 'identity_hate', 'score': 0.01344360038638115}]]
"""



"""
Example output:
people_also_ask.get_answer("Why is coffee bad for you?")

{'has_answer': True,
 'question': 'Why is coffee bad for you?',
 'related_questions': ['Why is drinking coffee bad for you?',
  'Is coffee good for your health?',
  'Is coffee toxic to your body?',
  'What does coffee do to your body?'],
 'response': 'Consuming too much caffeine can lead to jitteriness, anxiety, heart palpitations and even exacerbated panic attacks (34). If you are sensitive to caffeine and tend to become overstimulated, you may want to avoid coffee altogether. Another unwanted side effect is that it can disrupt sleep ( 35 ).Aug 30, 2018',
 'heading': 'Consuming too much caffeine can lead to jitteriness, anxiety, heart palpitations and even exacerbated panic attacks (34). If you are sensitive to caffeine and tend to become overstimulated, you may want to avoid coffee altogether. Another unwanted side effect is that it can disrupt sleep ( 35 ).Aug 30, 2018',
 'title': 'Coffee — Good or Bad? - Healthline',
 'link': 'https://www.healthline.com/nutrition/coffee-good-or-bad#:~:text=Consuming%20too%20much%20caffeine%20can,can%20disrupt%20sleep%20(%2035%20).',
 'displayed_link': 'www.healthline.com › nutrition › coffee-good-or-bad',
 'snippet_str': 'Consuming too much caffeine can lead to jitteriness, anxiety, heart palpitations and even exacerbated panic attacks (34). If you are sensitive to caffeine and tend to become overstimulated, you may want to avoid coffee altogether. Another unwanted side effect is that it can disrupt sleep ( 35 ).Aug 30, 2018\nwww.healthline.com › nutrition › coffee-good-or-bad\nhttps://www.healthline.com/nutrition/coffee-good-or-bad#:~:text=Consuming%20too%20much%20caffeine%20can,can%20disrupt%20sleep%20(%2035%20).\nCoffee — Good or Bad? - Healthline',
 'snippet_data': None,
 'date': None,
 'snippet_type': 'Definition Featured Snippet',
 'snippet_str_body': '',
 'raw_text': 'Featured snippet from the web\nConsuming too much caffeine can lead to jitteriness, anxiety, heart palpitations and even exacerbated panic attacks (34). If \nyou\n are sensitive to caffeine and tend to become overstimulated, \n may want to avoid \ncoffee\n altogether. Another unwanted side effect is that it can disrupt sleep ( 35 ).\nAug 30, 2018\nCoffee — Good or Bad? - Healthline\nwww.healthline.com\n › nutrition › coffee-good-or-bad'}
"""

def home(request):
	meeps = Meep.objects.all().filter(in_network=False).order_by("-created_at")
	return render(request, 'home.html', {"meeps":meeps,})


def profile_list(request):
	if request.user.is_authenticated:
		profiles = Profile.objects.exclude(user=request.user)
		return render(request, 'profile_list.html', {"profiles":profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def network_list(request):
	if request.user.is_authenticated:
		networks = Networks.objects.all()
		# .order_by("-created_on")
		print("the networks")
		print(networks)
		return render(request, 'network_list.html', {"networks":networks})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def add_ventpost(request):
	if request.user.is_authenticated:
		responses = []
		answer = False
		flags = []
		print("YOO EMMIRYYY")
		networks = NetworkMembers.objects.filter(user=request.user, accepted=True)
		
		networks_list = []
		for x in networks:
			n = x.network.networkname
			networks_list.append(n)
		form = MeepForm(request.POST or None)
		network_is = NetworkMembers.objects.filter(user=request.user, accepted=True).values('network')
		# test = Networks.objects.filters(id=network_is)
		print("davviddd")
		# print(test)
		# form.fields["network"] = ModelMultipleChoiceField(queryset=networks_list)
		if request.method == "POST":
			# selectednetwork = form['selectednetwork'].value()
			print("EMILYYY SELECTED NETWORK")
			# print(selectednetwork)
			selectednetwork = 'public'
			if networks_list != []:
				selectednetwork = request.POST['selectednetwork']
			print(selectednetwork)

			if request.POST["submitform"] == "submitform":
				if form.is_valid():
					text = form['body'].value()
					meep = form.save(commit=False)
					meep.user = request.user
					print(selectednetwork)
					if selectednetwork != 'public':
						print("here we go!")
						meep.in_network = True
						meep.network = Networks.objects.get(networkname=selectednetwork)
					meep.save()

					autocomment = ""
					if_flag_words = False
					scores = toxicity(text)
					for pair in scores[0]:
						if pair['score'] > 0.3:
							flags.append(pair['label'])
							if if_flag_words == False:
								autocomment += "This post has the following flags: "
							if_flag_words = True
							autocomment += pair['label'] + ' '
					if text != None:
						related_questions = people_also_ask.get_related_questions(text, 3)
						for question in related_questions:
							ans = people_also_ask.get_answer(question)
							if ans['has_answer'] == True:
								autocomment += '\n' + question + '\n' + ans['response']
								autocomment += '\n' + 'Source : ' + ans['link']
					if autocomment != "":
						if len(autocomment) > 1000:
							autocomment = autocomment[:995] + ' ...'
						autocommentobj = Comment(post=meep,name="AutoComment",body=autocomment)
						autocommentobj.save()


					messages.success(request, ("Your Vent Has Been Posted!"))
					return redirect('home')
			if request.POST["submitform"] == "info":
				text = form['body'].value()
				print(text)
				if text != None:
					related_questions = people_also_ask.get_related_questions(text, 3)
					for question in related_questions:
						ans = people_also_ask.get_answer(question)
						if ans['has_answer'] == True:
							answer = True
							response = {}
							response['question'] = question
							response['answer'] = ans['response']
							response['title'] = ans['title']
							response['link'] = ans['link']
							response['displayed_link'] = ans['displayed_link']
							response['raw_text'] = ans['raw_text']
							responses.append(response)
				
					scores = toxicity(text)
					print(scores)
					for pair in scores[0]:
						if pair['score'] > 0.3:
							flags.append(pair['label'])


		return render(request, 'add_ventpost.html', {"form":form, "responses": responses, "answer":answer, "flags":flags,"networks":networks_list,})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

# request.POST[""]

# Example output:
# toxicity(text)

# [[{'label': 'toxic', 'score': 0.9984544515609741}, 
# {'label': 'obscene', 'score': 0.9859963059425354}, 
# {'label': 'insult', 'score': 0.8170381188392639}, 
# {'label': 'severe_toxic', 'score': 0.36484864354133606}, 
# {'label': 'threat', 'score': 0.020054737105965614}, 
# {'label': 'identity_hate', 'score': 0.01344360038638115}]]

# Example output:
# people_also_ask.get_answer("Why is coffee bad for you?")



def venthighlight(request, slug):
	template_name = 'venthighlight.html'
	post = get_object_or_404(Meep, meepid=slug)
	comments = Comment.objects.filter(post=post).order_by("-created_on")


	return render(request, template_name, {'post': post,
											'comments': comments})


def addcomment(request, slug):
	template_name = 'addcomment.html'
	post = get_object_or_404(Meep, meepid=slug)
	new_comment = None
	# Comment posted
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			print("form is valid")
			# Create Comment object but don't save to database yet
			new_comment = comment_form.save(commit=False)
			# new_comment=Comment(post=post,name=request.user,body=text)
			# Assign the current post to the comment
			new_comment.post = post
			new_comment.name = request.user
			# Save the comment to the database
			new_comment.save()
			# redirect_url = "venthighlight/" + slug
			# return redirect(redirect_url)
			# return venthighlight(request, slug)
			messages.success(request, ("Added comment"))
			return venthighlight(request, slug)
		else:
			messages.success(request, ("couldn;t add comment"))
			return venthighlight(request, slug)
	else:
		comment_form = CommentForm()


	return render(request, template_name, {'post': post,
											'new_comment': new_comment,
											'comment_form': comment_form})





def addpromt(request, slug):
	template_name = 'addpromt.html'
	post = get_object_or_404(Meep, meepid=slug)
	# Comment posted
	if request.method == 'POST':
		print("in post")
		if (request.method == 'POST') and (request.POST['promt'] != "promt"):
			text = request.POST['promt']
			promt_comment = Comment(post=post, name=request.user,body=text)
			promt_comment.save()
			print("we are in the promt section")
			messages.success(request, ("Added comment"))
			return venthighlight(request, slug)


	return render(request, template_name, {'post': post,})





def createnetwork(request):
	if request.user.is_authenticated:
		template_name = 'createnetwork.html'
		form = CreateNetworkForm(request.POST or None)
		if request.method == 'POST':
			if form.is_valid():

				new_net = form.save(commit=False)
				new_net.owner = request.user
				new_net.save()

				messages.success(request, ("Added Network"))
				# html = 'editnetwork/' + str(new_net.id)
				# return redirect('home')
				print("creating boss!")
				boss = NetworkMembers(network=new_net, user=request.user, owner=True,verified=False,invited=False,accepted=True,requested=False)
				boss.save()
				return editnetwork(request, new_net.id, True)
			else:
				messages.success(request, ("Couldn't add network,"))
				return redirect('home')
		else:
			network_form = CreateNetworkForm()

		return render(request, template_name, {"form": network_form})


	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')



def editnetwork(request,pk, fromcreatenet=False):
	print("NET ID IS HEREEE")
	print(pk)
	if request.user.is_authenticated:
		net = get_object_or_404(Networks, id=pk)
		# profiles = Profile.objects.exclude(user=request.user)
		print("HERE WE GO AGGAINNN")
		all_users = User.objects.exclude(id=request.user.id)
		print("all_users")
		print(all_users)
		# alllll = NetworkMembers.objects.all()
		# for entry in alllll:
		# 	print(entry)
		# 	print(entry.network)
		# 	print(entry.accepted)
		# print("allll")
		# print(alllll)
		invited_user = NetworkMembers.objects.filter(network=net,invited=True)
		accepted_user = NetworkMembers.objects.filter(network=net,accepted=True)
		invited_or_accepted = []
		for m in invited_user:
			invited_or_accepted.append(m.user)
		for m in accepted_user:
			invited_or_accepted.append(m.user)
		print("invited_or_accepted")
		print(invited_or_accepted)
		profiles = []
		for user in all_users:

			if user not in invited_or_accepted:
				profiles.append(user)


		profile_formset = formset_factory(NetworkMembersForm, extra=0)
		formset = profile_formset(initial=[{'invited': x} for x in profiles])
		profiles_bool = False
		if len(profiles) > 0:
			print(len(profiles))
			profiles_bool = True
		checks = []
		template_name = 'editnetwork.html'
		print("here emiry")
		print(request)
		if (request.method == 'POST') and (request.POST['submit'] == "continue"):
			print("IN POST")
			print(request.POST)
			return redirect('home')
		if (request.method == 'POST') and (fromcreatenet == False):
			formset = profile_formset(request.POST)
			# print("post")
			invited_list = list(formset.cleaned_data)
			p = 0
			for profile in profiles:
				if invited_list[p]['invited'] == True:
					print("SEEENDDDINGG INVITEEEE")
					form = NetworkMembersForm()
					# print("profile")
					# print(profile.user.username)
					new_net = form.save(commit=False)
					new_net.user = User.objects.get(username=profile)
					new_net.network = net
					new_net.invited = True
					new_net.save()
				p += 1


			# 	messages.success(request, ("Added Network"))
			# 	return redirect('home')
			# else:
			# 	messages.success(request, ("couldn't add network"))
			# 	return redirect('home')
			messages.success(request, ("Network member requests sent"))
			return redirect('home')
		else:
			# network_form = CreateNetworkForm()
			context = {'formset': formset,'checks': checks, 'pk': pk, "profiles":profiles_bool,}
			return render(request, template_name, context)
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')




def profile(request, pk):
	if request.user.is_authenticated:
		profile = Profile.objects.get(user_id=pk)
		meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

		# Post Form logic
		if request.method == "POST":
			# Get current user
			current_user_profile = request.user.profile
			# Get form data
			action = request.POST['follow']
			# Decide to follow or unfollow
			if action == "unfollow":
				current_user_profile.follows.remove(profile)
			elif action == "follow":
				current_user_profile.follows.add(profile)
			# Save the profile
			current_user_profile.save()

		return render(request, "profile.html", {"profile":profile, "meeps":meeps})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		






def networkhighlight(request, pk):
	if request.user.is_authenticated:
		network = Networks.objects.get(id=pk)
		is_owner = False
		print("NETOWRK OWNNERRR")
		print(network.owner)
		print(request.user.username)
		if network.owner == request.user.username:
			is_owner = True
		meeps = Meep.objects.all().filter(network=network).order_by("-created_at")
		print("users!")
		print(NetworkMembers.objects.filter(network=network,accepted=True))
		member_list = NetworkMembers.objects.filter(network=network,accepted=True).values('user')
		member_users = []
		print(member_list)
		for member in member_list:
			member_users.append(User.objects.get(id=member['user']))
		# {% url 'profile' member.id %}
		print("passed")
		return render(request, "networkhighlight.html", {"network":network,"owner":is_owner,"meeps":meeps,"member_list":member_users,})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		




def notifications(request, pk):
	if request.user.is_authenticated:
		profile = Profile.objects.get(user_id=pk)
		# userobj = User.objects.get(id=pk)
		a = NetworkMembers.objects.all()
		# for thing in a:
		# 	print(thing.network.networkname)
		# 	print("to user")
		# 	print(thing.user)
		# 	print("from user")
		# 	print(thing.owner)
		# 	print(thing.accepted)

		invited = NetworkMembers.objects.filter(user=pk, invited=True)
		# print("invited")
		# print(invited)
		invited_list = [inv.network.networkname for inv in invited]

		# Post Form logic
		if request.method == "POST":
			# Get current user
			current_user_profile = request.user.profile
			print(len(request.POST))
			for invite in invited:
				status = request.POST[invite.network.networkname]
				#if accepted
				if status == 'accept':
					invite.invited = False
					invite.accepted = True
					invite.save()
				if status == 'decline':
					invite.delete()
		invited = NetworkMembers.objects.filter(user=pk, invited=True)
		invited_list = [inv.network.networkname for inv in invited]
			
		return render(request, "notifications.html", {"profile":profile, "invited":invited, 'pk': pk, 'invited_list':invited_list,})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		







def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ("You Have Been Logged In!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error logging in. Please Try Again..."))
			return redirect('login')

	else:
		return render(request, "login.html", {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You Have Been Logged Out. Sorry to Meep You Go..."))
	return redirect('home')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# first_name = form.cleaned_data['first_name']
			# second_name = form.cleaned_data['second_name']
			# email = form.cleaned_data['email']
			# Log in user
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ("You have successfully registered! Welcome!"))
			return redirect('home')
	
	return render(request, "register.html", {'form':form})


def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		form = SignUpForm(request.POST or None, instance=current_user)
		if form.is_valid():
			form.save()
			login(request, current_user)
			messages.success(request, ("Your Profile Has Been Updated!"))
			return redirect('home')

		return render(request, "update_user.html", {'form':form})
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')
	