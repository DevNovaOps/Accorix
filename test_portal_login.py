from django.test import Client
from django.urls import reverse
from core.models import User

# Test portal access
client = Client()

# Get a customer user
customer_user = User.objects.filter(role='customer', contact__isnull=False).first()
if customer_user:
    print(f"Testing login for customer: {customer_user.email}")
    
    # Try to login (we need to set a known password first)
    customer_user.set_password('testpass123')
    customer_user.save()
    
    # Login
    login_success = client.login(username=customer_user.username, password='testpass123')
    print(f"Login successful: {login_success}")
    
    if login_success:
        # Try to access portal dashboard
        response = client.get('/portal/')
        print(f"Portal dashboard status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Portal dashboard accessible!")
        else:
            print(f"❌ Portal dashboard error: {response.status_code}")
            if hasattr(response, 'content'):
                print(response.content.decode()[:500])
else:
    print("No customer user found")

print("\nPortal access test completed!")