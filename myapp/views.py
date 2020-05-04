from django.shortcuts import render,redirect
from.models import User,Phone,Review,Cart
from django.core.mail import send_mail
import random
from django.conf import settings
from django.views.generic.base import TemplateView
import stripe
from django.utils import timezone
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
	if request.method == 'POST':
		finalprice=request.POST['finalprice']
		charge = stripe.Charge.create (
            amount= finalprice ,
            currency='inr',
            description='charges for the product',
            source=request.POST['stripeToken']

        )
		success=request.POST['success']
		user=User.objects.get(pk=request.session['userpk'])
		carts=Cart.objects.filter(user=user)
		for i in carts:
			i.status="inactive"
			i.buy_data=timezone.now()
			i.save()
		carts=Cart.objects.filter(user=user,status="active")
		finalprice=0
		request.session['carts']=len(carts)
		for i in carts:
			finalprice+=int(i.phone.price)

		return render(request,'myapp/mycart.html',{'carts':carts ,'finalprice':finalprice,'success':success})
	else:
		return render(request,'myapp/index.html')

def mobile(request):
	return render(request,'myapp/mobile.html')
def redmi(request):
	redmis=Phone.objects.filter(brand="Redmi")
	return render(request,'myapp/redmi.html',{'redmis':redmis})
def samsung(request):
	samsungs=Phone.objects.filter(brand="Samsung")
	return render(request,'myapp/samsung.html',{'samsungs':samsungs})
def iphone(request):
	iphones=Phone.objects.filter(brand="iphone")
	return render(request,'myapp/iphone.html',{'iphones':iphones})
def sale(request):
	phone_sale=Phone.objects.filter(sale=True)
	for i in phone_sale:
		if i.sale==True:
			i.final_price=(int(i.price)-(int(i.price)*int(i.sale_price))/100)
			i.save()
		phone_sale=Phone.objects.filter(sale=True)	
	return render(request,'myapp/sale.html',{'phone_sale':phone_sale})
def signup(request):
	return render(request,'myapp/signup.html')
def login(request):
	return render(request,'myapp/login.html')
def signup_user(request):
	fname=request.POST['fname']
	lname=request.POST['lname']
	email=request.POST['email']
	mobile=request.POST['mobile']
	address=request.POST['address']
	image=request.FILES['image']
	password=request.POST['password']
	cpassword=request.POST['cpassword']
	user=User.objects.filter(email=email)

	if user:
		error="Email already register"
		return render(request,'myapp/signup.html',{'error':error})

	elif password==cpassword:
		User.objects.create(fname=fname,lname=lname,email=email,mobile=mobile,address=address,image=image,password=password,cpassword=cpassword)
		
		rec=[email,]
		subject="OTP For Successfull Registration  "
		otp=random.randint(1000,9999)
		message="Your OTP For Registation Is "+str(otp)
		email_from= settings.EMAIL_HOST_USER
		send_mail(subject,message,email_from,rec)
		return render(request,'myapp/verify_otp.html',{'otp':otp,'email':email})
	else:
		error="password & cpassword  not matched"
		return render(request,'myapp/signup.html',{'error':error})

def verify_user(request):
	otp=request.POST['otp']
	email=request.POST['email']
	u_otp=request.POST['u_otp']

	if otp==u_otp:
		user=User.objects.get(email=email)
		user.status="Active"
		user.save()
		return render(request,'myapp/login.html')
	else:
		error="Entered OTP Is Incorrect Please Try Again"
		return render(request,'myapp/verify_otp.html',{'otp':otp,'email':email,'error':error})

def login_user(request):
	email=request.POST['email']
	password=request.POST['password']

	try:
		user=User.objects.get(email=email,password=password,status="Active")
		if user:
			carts=Cart.objects.filter(user=user,status="active")
			request.session['carts']=len(carts)
			request.session['fname']=user.fname
			request.session['lname']=user.lname
			request.session['userpk']=user.pk
			request.session['email']=user.email
			request.session['image']=user.image.url
			return render(request,'myapp/index.html')
	except:
		error="Entered Email Or Password or status is wrong"
		return render(request,'myapp/login.html',{'error':error})

def logout(request):
	try:
		del request.session['fname']
		del request.session['lname']
		del request.session['userpk']
		del request.session['email']

		return render(request,'myapp/login.html')
	except:
		pass

def detail(request,pk):
	phone=Phone.objects.get(pk=pk)
	reviews=Review.objects.filter(phone=phone)
	return render(request,'myapp/detail.html',{'phone':phone,'reviews':reviews})

def feedback(request,pk1,pk2):
	user=User.objects.get(pk=pk1)
	phone=Phone.objects.get(pk=pk2)
	flag=True
	reviews=Review.objects.filter(phone=phone)
	carts=Cart.objects.filter(user=user,status="active")
	request.session['carts']=len(carts)
	return render(request,'myapp/detail.html',{'user':user,'phone':phone,'reviews':reviews,'flag':flag})

def submit_feedback(request,pk1,pk2):
	user=User.objects.get(pk=pk1)
	phone=Phone.objects.get(pk=pk2)
	feedback=request.POST['feedback']
	Review.objects.create(user=user,phone=phone,feedback=feedback)
	reviews=Review.objects.filter(phone=phone)
	carts=Cart.objects.filter(user=user,status="active")
	request.session['carts']=len(carts)
	return render(request,'myapp/detail.html',{'phone':phone,'reviews':reviews})
 
def add_to_cart(request,pk1,pk2):
	user=User.objects.get(pk=pk1)
	phone=Phone.objects.get(pk=pk2)
	Cart.objects.create(user=user,phone=phone)
	carts=Cart.objects.filter(user=user)
	request.session['carts']=len(carts)
	return redirect('mycart')
	
def mycart(request):
	finalprice=0
	user=User.objects.get(pk=request.session['userpk'])
	carts=Cart.objects.filter(user=user,status="active")
	request.session['carts']=len(carts)
	for i in carts:
		finalprice+=int(i.phone.price)
	return render(request,'myapp/mycart.html',{'carts':carts ,'finalprice':finalprice})

def remove_cart(request,pk):
	cart=Cart.objects.get(pk=pk)
	cart.delete()
	user=User.objects.get(pk=request.session['userpk'])
	carts=Cart.objects.filter(user=user,status="active")
	request.session['carts']=len(carts)
	return redirect('mycart')

def change_password(request):
	user=User.objects.get(userpk=request.session['userpk'])
	email=user.email
	rec=[email,]
	subject="OTP For CHANGE PASSWORD  "
	otp=random.randint(1000,9999)
	message="Your OTP For CHANGE PASSWORD Is "+str(otp)
	email_from= settings.EMAIL_HOST_USER
	send_mail(subject,message,email_from,rec)
	return render(request,'myapp/password_otp.html',{'otp':otp,'email':email})

def verify_pass_otp(request):
	otp=request.POST['otp']
	email=request.POST['email']
	u_otp=request.POST['u_otp']

	if otp==u_otp:
		user=User.objects.get(email=email)
		return render(request,'myapp/passwordform.html')
	else:
		error="Entered OTP Is Incorrect Please Try Again"
		return render(request,'myapp/password_otp.html',{'otp':otp,'email':email,'error':error})

def password_form(request):
	password=request.POST['password']
	cpassword=request.POST['cpassword']
	user=User.objects.get(pk=request.session['userpk'])
	if password==cpassword:
		user.password=password
		user.cpassword=cpassword
		user.save()
		try:
			del request.session['fname']
			del request.session['lname']
			del request.session['email']
			del request.session['userpk']
			return render(request,'myapp/login.html')
		except:
			pass
	else:
		error="Entered password and cpassword doesnt match"
		return render(request,'myapp/passwordform.html',{'error':error})

def forgot_password(request):
	return render(request,'myapp/forgot_password.html')

def verify_forgot_password(request):
	email=request.POST['email']
	try:
		user=User.objects.get(email=email)
		if user:
			rec=[email,]
			subject="OTP For CHANGE PASSWORD  "
			otp=random.randint(1000,9999)
			message="Your OTP For CHANGE PASSWORD Is "+str(otp)
			email_from= settings.EMAIL_HOST_USER
			send_mail(subject,message,email_from,rec)
			return render(request,'myapp/otp_forgotpassword.html',{'otp':otp,'email':email})

	except:
		error="your email is not register"
		return render(request,'myapp/login.html',{'error':error})

def verify_otp_forgotpassword(request):
	otp=request.POST['otp']
	email=request.POST['email']
	u_otp=request.POST['u_otp']

	if otp==u_otp:
		user=User.objects.get(email=email)
		return render(request,'myapp/change_passwordform.html',{'email':email})
	else:
		error="Entered OTP Is Incorrect Please Try Again"
		return render(request,'myapp/otp_forgotpassword.html',{'otp':otp,'email':email,'error':error})

def confirm_password_form(request):
	password=request.POST['password']
	cpassword=request.POST['cpassword']
	email=request.POST['email']
	user=User.objects.get(email=email)
	if password==cpassword:
		user.password=password
		user.cpassword=cpassword
		user.save()
		return render(request,'myapp/login.html')
	else:
		error="Entered password and cpassword doesnt match"
		return render(request,'myapp/change_passwordform.html',{'error':error})

def payment(request):
	finalprice=request.POST ['finalprice']
	finalprice1=int(finalprice)*100
	key=settings.STRIPE_PUBLISHABLE_KEY
	return render(request,'myapp/payment.html',{'finalprice':finalprice,'finalprice1':finalprice1,'key':key})

def myorder(request):
	user=User.objects.get(pk=request.session['userpk'])
	carts=Cart.objects.filter(user=user,status="inactive")
	return render(request,'myapp/myorder.html',{'carts':carts})


	
	



	
       



