#date_calculator
import datetime as dt
#prints todays date
today = dt.date.today()
print ("Hello! Today is:", today)

user_input = input("Please enter the date in format YYYY-MM-dd: ") #takes user input
yy, mm, dd = map(int, user_input.split('-')) #delimts the input
bd = dt.date(yy, mm, dd)#transforms it into the integer

print ("Your Birthday is on", bd)

days_to = bd - today
print ("You need to wait days till your Birthday:", days_to)

//_____________________________ //
#classes
class Customer:
	"""docstring for ClassName"""
	def __init__(self, name, city, gender, orders, brand):
		self.name = name
		self.city = city
		self.gender = gender
		self.orders = orders
		self.brand = brand

	def showNumOrders(self):
		print("Customer has amount of orders:", self.orders)

	def changeCity(self,city):
		print("Initial city:", self.city)
		self.city = city
		print("Moved to the", self.city)

customer1 = Customer("Max", "Hamburg", "male", 15, "Brooklyn own by Rocawear")
customer2 = Customer("Rachel", "Berlin", "female", 45, "Oysho")

customer1.showNumOrders()
customer1.changeCity("Dresden")

//_____________________________ //
#odd_even
integers = [int(x) for x in input().split()]
count_odd = 0
count_even = 0
for x in integers:
	if x % 2 == 0:
		count_even+=1
	else:
		count_odd+=1
print("Number of even numbers :",count_even)  
print("Number of odd numbers :",count_odd)
