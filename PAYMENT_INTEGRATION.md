# UatPayments Gateway Integration

## Overview
Payment gateway integration using UatPayments has been successfully added to the ADAMS Django project.

## API Credentials
- **API_KEY**: `fb6bca86-b429-4abf-a42f-824bdd29022e`
- **SALT**: `80c67bfdf027da08de88ab5ba903fecafaab8f6d`
- **Payment Gateway URL**: `https://pgbiz.omniware.in/v2/paymentrequest`

## Files Added/Modified

### 1. `app/views.py`
**Added:**
- `payment_request(request)` - Handles payment request and redirects to payment gateway
- `payment_response(request)` - Handles payment response from gateway (CSRF exempt)

**Location:** Lines 3534-3618

**Key Features:**
- SHA512 hash generation for payment request
- Hash verification for payment response
- Required field validation
- Error handling with logging

### 2. `app/urls.py`
**Added Routes:**
```python
path('payment_request/', views.payment_request, name='payment_request'),
path('payment_response/', views.payment_response, name='payment_response'),
```

### 3. Templates Created

#### `app/templates/payment_request.html`
- Payment form with all required fields
- Auto-submit functionality (redirects to gateway)
- Bootstrap styling integrated with main.html
- Mode selection (TEST/LIVE)

#### `app/templates/payment_success.html`
- Success page with transaction details
- Transaction ID display
- Amount confirmation
- Navigation buttons

#### `app/templates/payment_failure.html`
- Failure page with error message
- User-friendly error display
- Retry option

## Usage

### 1. Access Payment Form
Navigate to: `http://127.0.0.1:8000/payment_request/`

### 2. Fill Required Fields
- **Amount** (required)
- **Email** (required)
- **Name** (required)
- **Phone** (required)
- **Address Line 1** (required)
- **City** (required)
- **Order ID** (required)
- **Currency** (default: INR)
- **Description** (required)
- **Country** (default: IND)
- **Return URL** (default: `http://127.0.0.1:8000/payment_response/`)
- **Mode** (TEST or LIVE)

### 3. Submit Payment
- Form auto-submits to payment gateway
- User is redirected to UatPayments gateway
- After payment, user is redirected back to `payment_response/`

### 4. Payment Response
- Success: User sees success page with transaction ID
- Failure: User sees failure page with error message

## Testing

### Test Mode
1. Set `mode` to `TEST` in the form
2. Use test credentials provided by UatPayments
3. Complete test transaction

### Live Mode
1. Set `mode` to `LIVE` in the form
2. Use real payment credentials
3. Complete actual transaction

## Hash Generation

### Request Hash
```
hash_string = SALT + | + address_line_1 + | + address_line_2 + | + amount + | + api_key + | + city + | + country + | + currency + | + description + | + email + | + mode + | + name + | + order_id + | + phone + | + return_url + | + state + | + udf1 + | + udf2 + | + udf3 + | + udf4 + | + udf5 + | + zip_code
hash = SHA512(hash_string).upper()
```

### Response Hash Verification
```
hash_string = SALT + | + (all POST fields sorted alphabetically, excluding 'hash')
calculated_hash = SHA512(hash_string).upper()
```

## Security Features

1. **CSRF Protection**: Payment request form includes CSRF token
2. **Hash Verification**: All responses are verified using SHA512 hash
3. **Required Field Validation**: Prevents incomplete submissions
4. **Error Handling**: Comprehensive error handling with logging

## Integration Points

### From Registration Form
You can link the payment form from the registration page:
```html
<a href="{% url 'payment_request' %}" class="btn btn-primary">Make Payment</a>
```

### Pre-fill Form Data
You can pre-fill payment form with user data:
```python
# In your view
return redirect('payment_request', data={
    'name': user.get_full_name(),
    'email': user.email,
    'phone': user.phone,
    # ... other fields
})
```

## Environment Variables (Optional)

For production, consider moving credentials to environment variables:

```python
# In settings.py
UATPAYMENTS_API_KEY = os.getenv("UATPAYMENTS_API_KEY", "fb6bca86-b429-4abf-a42f-824bdd29022e")
UATPAYMENTS_SALT = os.getenv("UATPAYMENTS_SALT", "80c67bfdf027da08de88ab5ba903fecafaab8f6d")
```

Then update views.py to use:
```python
from django.conf import settings
API_KEY = settings.UATPAYMENTS_API_KEY
SALT = settings.UATPAYMENTS_SALT
```

## Troubleshooting

### Form Not Auto-Submitting
- Check browser console for JavaScript errors
- Verify hash is generated correctly
- Check that all required fields are filled

### Hash Mismatch Error
- Verify SALT matches in both request and response
- Check field order in hash generation
- Ensure no extra whitespace in field values

### Payment Not Redirecting
- Verify return_url is correct
- Check payment gateway configuration
- Review gateway logs

## Next Steps

1. **Test Integration**: Test with TEST mode first
2. **Update Return URL**: Change return_url to production domain
3. **Add Payment Logging**: Log all payment transactions
4. **Link to Registration**: Integrate payment into registration flow
5. **Update User Model**: Store transaction IDs in database

## Support

For UatPayments support:
- Gateway URL: `https://pgbiz.omniware.in/v2/paymentrequest`
- Contact UatPayments team for API documentation
