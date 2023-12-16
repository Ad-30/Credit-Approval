from .models import Customer, Loan  # Import your models
import pandas as pd
from datetime import datetime

def init_data():
    customers = Customer.objects.all()
    if len(customers) == 0:
        customer_df = pd.read_excel('customer_data.xlsx')

        for index, row in customer_df.iterrows():
            customer = Customer(
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit']
            )
            customer.save()

        loan_df = pd.read_excel('loan_data.xlsx')

        for index, row in loan_df.iterrows():
            try:
                customer_id = row['Customer ID']
                customer = Customer.objects.get(id=customer_id)
                start_date_str = row['Date of Approval'].strftime('%Y-%m-%d')
                end_date_str = row['End Date'].strftime('%Y-%m-%d')

                loan = Loan(
                    customer=customer,
                    loan_id=row['Loan ID'],
                    loan_amount=row['Loan Amount'],
                    tenure=row['Tenure'],
                    interest_rate=row['Interest Rate'],
                    monthly_repayment=row['Monthly payment'],
                    emis_paid_on_time=row['EMIs paid on Time'],
                    start_date=datetime.strptime(start_date_str, '%Y-%m-%d').date(),
                    end_date=datetime.strptime(end_date_str, '%Y-%m-%d').date()
                )
                loan.save()
            except Exception as e:
                pass
