from django import forms
from django.core.validators import MinLengthValidator
from django.forms.utils import ErrorList

from lessons.models import User, Request, Child
from lessons.models import User, Request, Transaction, Invoice
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Hidden, Row, Column, Field
from crispy_forms.bootstrap import AppendedText


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    password = forms.CharField(label='Password', widget=forms.PasswordInput(), validators=[MinLengthValidator(8)])
    password_confirmation = forms.CharField(label='Confirm password', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirmation'):
            self.add_error('password_confirmation', 'Passwords do not match')

    def save(self, commit=True):
        super().save(commit=False)
        return User.objects.create_user(
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
        )


class LogInForm(forms.Form):
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'is_superuser']
        widgets = {
            'first_name': forms.TextInput(),
            'last_name': forms.TextInput(),
            'email': forms.TextInput(),
            'is_staff': forms.CheckboxInput(),
            'is_superuser': forms.CheckboxInput(),
        }
        help_texts = {
            'is_staff': None,
            'is_superuser': None
        }
        labels = {
            'is_staff': 'Is Administrator',
            'is_superuser': 'Is Director'
        }

    def __init__(self, data=None, files=None, auto_id="id_%s", prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        if instance is not None and instance.is_superuser:
            self.fields['is_superuser'].disabled = True
            self.fields['is_staff'].disabled = True


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['availability', 'number_of_lessons', 'interval', 'duration', 'lesson_content']

    child = forms.ModelChoiceField(queryset=Child.objects, blank=True, required=False, label="For Child:")
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), blank=True, required=False,
                                     label="Requested Teacher:")

    def save(self, user_id, commit=True):
        super().save(commit=False)
        request = Request.objects.create(
            user=user_id,
            availability=self.cleaned_data.get('availability'),
            number_of_lessons=self.cleaned_data.get('number_of_lessons'),
            interval=self.cleaned_data.get('interval'),
            duration=self.cleaned_data.get('duration'),
            lesson_content=self.cleaned_data.get('lesson_content'),
            teacher=self.cleaned_data.get('teacher'),
            child=self.cleaned_data.get('child')
        )
        return request

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            self.fields['child'].queryset = Child.objects.filter(parent=user)
            self.fields['child'].label_from_instance = lambda child: child.name
        self.fields['teacher'].label_from_instance = lambda teacher: teacher.first_name + " " + teacher.last_name
        self.helper = FormHelper()
        self.helper.form_id = 'request_form'
        # self.helper.form_class = 'blueForms' # removed in my version
        self.helper.form_method = 'post'
        self.helper.form_action = 'make_request'
        self.helper.layout = Layout(
            'child',
            'availability',
            'number_of_lessons',
            Row(
                Column(AppendedText('interval', 'week(s)'), css_class="form-group col-md-6 mb-0"),
                Column(AppendedText('duration', 'minutes'), css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            Row(
                Column('lesson_content', css_class="form-group col-md-6 mb-0"),
                Column('teacher', css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            Submit('submitRequest', 'Make request')
        )


class EditRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['availability', 'number_of_lessons', 'interval', 'duration', 'lesson_content']

    child = forms.ModelChoiceField(queryset=None, blank=True, required=False, label="For Child:")
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), blank=True, required=False,
                                     label="Requested Teacher:")

    def save(self, request, commit=True):
        super().save(commit=False)

        request.availability = self.cleaned_data.get('availability')
        request.number_of_lessons = self.cleaned_data.get('number_of_lessons')
        request.interval = self.cleaned_data.get('interval')
        request.duration = self.cleaned_data.get('duration')
        request.lesson_content = self.cleaned_data.get('lesson_content')
        request.teacher = self.cleaned_data.get('teacher')
        request.child = self.cleaned_data.get('child')
        request.save()

        return request

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['child'].queryset = Child.objects.filter(parent=user)
            self.fields['child'].label_from_instance = lambda child: child.name
        self.fields['teacher'].label_from_instance = lambda teacher: teacher.first_name + " " + teacher.last_name
        self.helper = FormHelper()
        self.helper.form_id = 'edit_request_form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'child',
            'availability',
            'number_of_lessons',
            Row(
                Column(AppendedText('interval', 'week(s)'), css_class="form-group col-md-6 mb-0"),
                Column(AppendedText('duration', 'minutes'), css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            Row(
                Column('lesson_content', css_class="form-group col-md-6 mb-0"),
                Column('teacher', css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            Submit('submitRequest', 'Update request')
        )


class ApproveForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['number_of_lessons', 'interval', 'duration', 'lesson_content', 'teacher', 'class_Day', 'class_Time',
                  'start_Date']

    teacher = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), blank=True, required=False,
                                     label="Requested Teacher:")
    def save(self, request, commit=True):
        super().save(commit=False)

        # request_id = request,
        request.number_of_lessons = self.cleaned_data.get('number_of_lessons')
        request.interval = self.cleaned_data.get('interval')
        request.duration = self.cleaned_data.get('duration')
        request.lesson_content = self.cleaned_data.get('lesson_content')
        request.teacher = self.cleaned_data.get('teacher')
        request.class_Day = self.cleaned_data.get('class_Day')
        request.class_Time = self.cleaned_data.get('class_Time')
        request.start_Date = self.cleaned_data.get('start_Date')
        request.isApproved = True
        request.save()

        return request

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'request_form'
        # self.helper.form_class = 'blueForms' # Lyn version
        self.helper.form_method = 'post'
        # self.helper.form_action = 'approve' # Lyn version
        self.helper.layout = Layout(
            'number_of_lessons',
            Row(
                Column(AppendedText('interval', 'week(s)'), css_class="form-group col-md-6 mb-0", ),
                Column(AppendedText('duration', 'minutes'), css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            'lesson_content',
            'teacher',
            Row(
                Column('class_Day', css_class="form-group col-md-6 mb-0", ),
                Column('class_Time', css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            'start_Date',
            Submit('submitApproval', 'Approve request')
        )


class RegisterChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name']

    def save(self, parent, commit=True):
        super().save(commit=False)
        return Child.objects.create(
            name=self.cleaned_data.get('name'),
            parent=parent
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'register_child'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register_child'
        self.helper.layout = Layout(
            'name',
            Submit('submitChild', 'Register Child')
        )


class EditChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'edit_child'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'edit_child'
        self.helper.layout = Layout(
            'name',
            Submit('submitChild', 'Edit Child')
        )


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'invoice', 'date_paid']

    def save(self, user, commit=True):
        super().save(commit=False)

        localInvoice = self.cleaned_data.get('invoice')
        payment = Transaction()
        payment.amount = self.cleaned_data.get('amount')
        payment.invoice = self.cleaned_data.get('invoice')
        payment.date_paid = self.cleaned_data.get('date_paid')
        payment.administrated_by = user
        payment.created_by = localInvoice.request.user
        payment.save()

        return payment

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['invoice'] = forms.ModelChoiceField(queryset=Invoice.objects.all(),
                                                        to_field_name="invoice_number")
        self.helper = FormHelper()
        self.helper.form_id = 'request_form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'create_transaction'
        self.helper.layout = Layout(
            'invoice',
            'amount',
            'date_paid',
            Submit('submitTransaction', 'Create transaction')
        )
