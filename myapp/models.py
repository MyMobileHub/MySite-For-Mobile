from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=200)
	lname=models.CharField(max_length=200)
	email=models.CharField(max_length=200)
	mobile=models.CharField(max_length=200)
	address=models.TextField()
	password=models.CharField(max_length=200)
	cpassword=models.CharField(max_length=200)
	status=models.CharField(max_length=200,default="Inactive")
	image=models.ImageField(upload_to='images/',default="")

	def __str__(self):
		return self.fname+" "+self.lname

class Phone(models.Model):
	CHOICES=(
		("iphone",'iphone'),
		("Redmi",'Redmi'),
		("Samsung",'Samsung'),
	)
	brand=models.CharField(max_length=200,choices=CHOICES,default="")
	model=models.CharField(max_length=200)
	price=models.CharField(max_length=200)
	specifications=models.TextField()
	image=models.ImageField(upload_to='images/')
	sale=models.BooleanField(default=False)
	sale_price=models.CharField(max_length=100,default="10")
	final_price=models.CharField(max_length=100,null=True,blank=True)


	def __str__(self):
		return self.model

class Review(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	phone=models.ForeignKey(Phone,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	feedback=models.TextField()


class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	phone=models.ForeignKey(Phone,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	status=models.CharField(max_length=100,default="active")
	buy_data=models.DateTimeField(default=timezone.now)
