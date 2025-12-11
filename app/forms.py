from django import forms
# from .models import UserReg
# from django.contrib.auth.hashers import make_password, check_password

# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput, min_length=8)
#     confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

#     class Meta:
#         model = UserReg
#         fields = ['username', 'password', 'confirm_password', 'email', 'phone_number', 'role']

#     # def clean_username(self):
#     #     username = self.cleaned_data.get('username')
#     #     if len(username) > 30:
#     #         raise forms.ValidationError("Ensure this value has at most 30 characters.")
#     #     return username

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match.")

#         cleaned_data['password'] = make_password(password)  # Encrypt password
#         return cleaned_data

# from django import forms
# from django.contrib.auth.models import User
# from .models import UserReg

# from django import forms
# from django.contrib.auth.models import User
# from .models import UserReg

# class UserRegistrationForm(forms.ModelForm):
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput,
#         label="Confirm Password"
#     )
#     phone_number = forms.CharField(
#         max_length=12,
#         required=False,  # You can set this to True if phone number is mandatory
#         label="Phone Number"
#     )
#     role = forms.ChoiceField(
#         choices=UserReg.role_choices,
#         required=True
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email', 'first_name', 'last_name']

#     def clean_password(self):
#         password = self.cleaned_data.get('password')
#         if len(password) < 8:
#             raise forms.ValidationError("Password must be at least 8 characters long.")
#         return password

#     def clean_confirm_password(self):
#         password = self.cleaned_data.get('password')
#         confirm_password = self.cleaned_data.get('confirm_password')
#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match.")
#         return confirm_password

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])
#         if commit:
#             user.save()
#         return user



from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms

class UserRegistrationForm(UserCreationForm):
    photo = forms.FileField(required=True)
    state_nmc = forms.FileField(required=False)
    passport = forms.FileField(required=True)
    medical_qualification = forms.FileField(required=True)
    payment_transaction_proof = forms.FileField(required=True)
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'middle_name', 'last_name', 'gender', 'email',
            'whatsapp_number', 'mobile_number', 'address_communication',
            'address_permanent', 'district', 'father_spouse_details', 'blood_group',
            'password1', 'password2', 'educational_status', 'category', 'university_name', 
            'country_university', 'year_of_joining', 'year_of_completion', 'photo', 'state_nmc', 
            'passport', 'medical_qualification', 'date_time_of_payment', 'payment_transaction_proof', 
            'willing_to_be_donor', 'agreement', 'mid', 'application'
        ]

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['district'].choices = User.district_choices

        print(f"District choices: {self.fields['district'].choices}")

        for field_name, field in self.fields.items():
            field.required = False

            # if field_name != 'state_nmc':
            #     field.required = False
            
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, FileInput):
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_district(self):
        district = self.cleaned_data.get('district')

        # If "Others" is selected, validate the custom district name
        if district == 'Others':
            print("Custom district selected:", self.data)
            custom_district = self.data.get('custom_district')  # Get custom input
            if not custom_district:
                raise forms.ValidationError("Please specify the district if 'Others' is selected.")
            print("Custom district value:", custom_district)
            return custom_district  # Use the custom value instead of "Others"

        # Return the predefined district value
        print("Predefined district selected:", district)
        return district
    
    def clean_state_nmc(self):
        state_nmc = self.cleaned_data.get('state_nmc')
        
        # If state_nmc is empty (i.e., no file uploaded), return None or leave it blank
        if not state_nmc:
            return None  # or you can return an empty string, depending on your preference

        # If the file is provided, you can do additional validation or processing here
        return state_nmc


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = [
#             'username', 'first_name', 'middle_name', 'last_name', 'gender', 'email',
#             'whatsapp_number', 'mobile_number', 'address_communication',
#             'address_permanent', 'district', 'father_spouse_details', 'blood_group',
#             'role', 'educational_status', 'category', 'university_name', 
#             'country_university', 'year_of_joining', 'year_of_completion', 'photo', 'state_nmc', 
#             'passport', 'medical_qualification', 'date_time_of_payment', 'payment_transaction_proof', 
#             'willing_to_be_donor', 'agreement', 'mid', 'application'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if field.widget.attrs.get('class'):
#                 field.widget.attrs['class'] += ' form-control'
#             else:
#                 field.widget.attrs['class'] = 'form-control'

from django.forms.widgets import CheckboxInput, FileInput

class UserUpdateForm(forms.ModelForm):
    # photo = forms.FileField(required=True)
    # state_nmc = forms.FileField(required=True)
    # passport = forms.FileField(required=True)
    # medical_qualification = forms.FileField(required=True)
    # payment_transaction_proof = forms.FileField(required=True)
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'middle_name', 'last_name', 'gender', 'email',
            'whatsapp_number', 'mobile_number', 'address_communication',
            'address_permanent', 'district', 'father_spouse_details', 'blood_group',
            'role', 'educational_status', 'category', 'university_name', 
            'country_university', 'year_of_joining', 'year_of_completion', 'photo', 'state_nmc', 
            'passport', 'medical_qualification', 'date_time_of_payment', 'payment_transaction_proof', 
            'willing_to_be_donor', 'mid',
        ]
        # widgets = {
        #     'district': forms.Select(choices=User.district_choices)  # Dropdown for predefined options
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['district'].choices = User.district_choices

        print(f"District choices: {self.fields['district'].choices}")

        for field_name, field in self.fields.items():
            field.required = False
            
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, FileInput):
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_district(self):
        district = self.cleaned_data.get('district')

        # If "Others" is selected, validate the custom district name
        if district == 'Others':
            print("Custom district selected:", self.data)
            custom_district = self.data.get('custom_district')  # Get custom input
            if not custom_district:
                raise forms.ValidationError("Please specify the district if 'Others' is selected.")
            print("Custom district value:", custom_district)
            return custom_district  # Use the custom value instead of "Others"

        # Return the predefined district value
        print("Predefined district selected:", district)
        return district

    def save(self, commit=True):
        # Preserve existing file fields if no new file is uploaded
        instance = super().save(commit=False)
        for field_name in ['photo', 'state_nmc', 'passport', 'medical_qualification', 'payment_transaction_proof']:
            if not self.cleaned_data.get(field_name):  # If no new file uploaded
                current_file = getattr(self.instance, field_name)
                setattr(instance, field_name, current_file)  # Retain existing file
        if commit:
            instance.save()
        return instance

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print("Initializing form fields...")
    #     for field_name, field in self.fields.items():
    #         if field.widget.attrs.get('class'):
    #             field.widget.attrs['class'] += ' form-control'
    #         else:
    #             field.widget.attrs['class'] = 'form-control'





# class UserLoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
