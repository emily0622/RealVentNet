from email.policy import default
from django import forms
from .models import Meep, Comment, Networks, NetworkMembers
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MeepForm(forms.ModelForm):
	body = forms.CharField(required=True, 
		widget=forms.widgets.Textarea(
			attrs={
			"placeholder": "Enter Your VentNet VentPost!",
			"class":"form-control",
			}
			),
			label="",
		)
	title = forms.CharField(required=True, label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Title'}))
	link = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Link'}))

	class Meta:
		model = Meep
		exclude = ("user",)


class CommentForm(forms.ModelForm):
	body = forms.CharField(required=True, 
		widget=forms.widgets.Textarea(
			attrs={
			"placeholder": "Enter Your comment!",
			"class":"form-control",
			}
			),
			label="",
		)

	class Meta:
		model = Comment
		exclude = ('name','post', 'active')



class CreateNetworkForm(forms.ModelForm):
	networkname = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Title'}))
	desc = forms.CharField(required=True, 
		widget=forms.widgets.Textarea(
			attrs={
			"placeholder": "Enter a description of this network",
			"class":"form-control",
			}
			),
			label="",
		)

	class Meta:
		model = Networks
		exclude = ("owner",)


class NetworkMembersForm(forms.ModelForm):
	invited = forms.BooleanField(required=False)

	class Meta:
		model = NetworkMembers
		exclude = ("network","owner","verified","user","accepted",)


# class NetworkNotificationsForm(forms.ModelForm):
# 	accepted = forms.BooleanField(required=False)
# 	declined = forms.BooleanField(required=False)
# 	responded = forms.BooleanField(required=False)

# 	class Meta:
# 		model = NetworkNotifications
# 		exclude = ("network","fromuser","touser","invitedtojoin","requestedtojoin",)


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'