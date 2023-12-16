from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import pandas as pd
from datetime import datetime
from api.models import Customer, Loan
from rest_framework import serializers
from datetime import datetime, timedelta
from decimal import Decimal

class CustomerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15)

def decimal_to_float(value):
    return float(value) if isinstance(value, Decimal) else value

def calculate_credit_score(customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        
        past_loans = Loan.objects.filter(customer=customer)
        total_past_loans = past_loans.count()
        past_loans_paid_on_time = past_loans.filter(emis_paid_on_time=True).count() / total_past_loans if total_past_loans else 0
        
        number_of_loans_taken = total_past_loans
        
        current_year = datetime.now().year
        current_year_loans = past_loans.filter(start_date__year=current_year)
        loan_activity_current_year = current_year_loans.count()
        
        loan_approved_volume = decimal_to_float(sum(loan.loan_amount for loan in past_loans))
        
        credit_score = (
            0.3 * past_loans_paid_on_time +
            0.2 * number_of_loans_taken +
            0.1 * loan_activity_current_year +
            0.4 * loan_approved_volume
        ) * 100  
        
        return credit_score
    
    except Customer.DoesNotExist:
        return None

@api_view(['POST'])
def register_customer(request):
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
           
            monthly_salary = serializer.validated_data['monthly_income']
            approved_limit = round(36 * monthly_salary, -5) 
            
            customer = Customer.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                age=serializer.validated_data['age'],
                monthly_salary=monthly_salary,
                phone_number=serializer.validated_data['phone_number'],
                approved_limit=approved_limit
            )
            
            response_data = {
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_salary,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            approved_limit = customer.approved_limit
            monthly_salary = float(customer.monthly_salary) 
            
            current_loans = Loan.objects.filter(customer=customer, end_date__gte=datetime.now().date())
            total_emis = sum(float(loan.monthly_repayment) for loan in current_loans)  
            
            if total_emis > 0.5 * monthly_salary:
                return Response({
                    'customer_id': customer_id,
                    'approval': False,
                    'message': 'Total EMIs exceed 50% of monthly salary'
                })
            
            credit_score = calculate_credit_score(customer_id) 
            
            if credit_score > 50:
                approved = True
                corrected_interest_rate = interest_rate 
            elif 50 > credit_score > 30:
                approved = True
                corrected_interest_rate = max(interest_rate, 12.0) 
            elif 30 > credit_score > 10:
                approved = True
                corrected_interest_rate = max(interest_rate, 16.0)  
            else:
                approved = False
                corrected_interest_rate = 0.0
            
            response_data = {
                'customer_id': customer_id,
                'approval': approved,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate,
                'tenure': tenure,
                'monthly_installment': calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
            }
            
            return Response(response_data)
        
        except Customer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=404)

@api_view(['POST'])
def create_loan(request):
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            approved_limit = customer.approved_limit
            monthly_salary = float(customer.monthly_salary)
            
            current_loans = Loan.objects.filter(customer=customer, end_date__gte=datetime.now().date())
            total_emis = sum(float(loan.monthly_repayment) for loan in current_loans)
            
            if total_emis > 0.5 * monthly_salary:
                return Response({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': 'Total EMIs exceed 50% of monthly salary',
                    'monthly_installment': None
                })
            
            credit_score = calculate_credit_score(customer_id)
            
            
            if credit_score > 50:
                loan_approved = True
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=interest_rate,
                    tenure=tenure,
                    monthly_repayment=calculate_monthly_installment(loan_amount, interest_rate, tenure),
                    start_date=datetime.now().date(),
                    end_date = datetime.now() + timedelta(days=30 * tenure)
                )
                loan.loan_id_id = loan.loan_id
                loan.save()
                return Response({
                    'loan_id': loan.loan_id_id,
                    'customer_id': customer_id,
                    'loan_approved': loan_approved,
                    'message': 'Loan approved',
                    'monthly_installment': loan.monthly_repayment
                })
            else:
                return Response({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': 'Loan not approved based on credit score',
                    'monthly_installment': None
                })
            
        except Customer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=404)

@api_view(['GET'])
def loan_details(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = loan.customer
        
        customer_details = {
            'id': customer.customer_id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone_number': customer.phone_number,
            'age': customer.age
        }
        
        loan_details = {
            'loan_id': loan.loan_id_id,
            'customer': customer_details,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'tenure': loan.tenure
        }
        
        return Response(loan_details)
    except Loan.DoesNotExist:
        return Response({'message': 'Loan does not exist'}, status=404)


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        loans = Loan.objects.filter(customer_id=customer_id, end_date__gte=datetime.now().date())

        loan_details = []
        for loan in loans:
            repayments_left = (loan.end_date.year - datetime.now().date().year) * 12 + loan.end_date.month - datetime.now().date().month

            loan_item = {
                'loan_id': loan.loan_id_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'repayments_left': repayments_left
            }
            loan_details.append(loan_item)

        return Response(loan_details)
    except Loan.DoesNotExist:
        return Response({'message': 'No loans found for this customer'}, status=404)

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = interest_rate / (12 * 100)
    monthly_installment = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure) / (((1 + monthly_interest_rate) ** tenure) - 1)
    return monthly_installment

