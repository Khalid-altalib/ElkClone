from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, get_user, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect
from django.urls import reverse
from lessons import forms
from .models import Request, User, Child, Invoice, Transaction
from decimal import Decimal


# Create your views here.
def home(req):
    user = get_user(req)
    if user.is_authenticated:
        return redirect_to_home(user)
    return render(req, 'home.html')


def sign_up(req):
    user = get_user(req)
    if user.is_authenticated:
        return redirect_to_home(user)
    if req.method == 'POST':
        form = forms.SignUpForm(req.POST)
        if form.is_valid():
            user = form.save()
            login(req, user)
            return redirect_to_home(user)
        messages.add_message(req, messages.ERROR, "Invalid sign up details.")

    form = forms.SignUpForm()
    return render(req, 'sign_up.html', {'form': form})


def log_in(req):
    user = get_user(req)
    if user.is_authenticated:
        return redirect_to_home(user)
    if req.method == 'POST':
        form = forms.LogInForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(req, user)
                return redirect_to_home(user)
            messages.add_message(req, messages.ERROR, "Invalid credentials.")
    form = forms.LogInForm()
    return render(req, 'log_in.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url="log_in")
def edit_user(req, user_id):
    user_to_change = User.objects.get(id=user_id)
    if req.method == 'POST':
        form = forms.EditUserForm(req.POST, instance=user_to_change)
        if form.is_valid():
            form.save()
            return redirect_to_home(get_user(req))
        messages.add_message(req, messages.ERROR, "Invalid details.")

    form = forms.EditUserForm(instance=user_to_change)
    return render(req, 'edit_user.html', {'form': form, 'user': user_to_change,
                                          'can_delete': not user_to_change.is_superuser})


def view_student(req, user_id):
    users = User.objects.filter(is_active=True)
    student_to_view = User.objects.get(id=user_id)
    student_to_view.generateInvoices()
    student_to_view.updateBalance()
    approved = Request.objects.filter(isApproved=True, user_id=student_to_view)
    pending = Request.objects.filter(isApproved=False, user_id=student_to_view)
    invoices = Invoice.objects.filter(request__isApproved=True, request__user=student_to_view)
    # active_invoices = Invoice.objects.filter(request__isApproved=True, request__user=student_to_view, status='ACTIVE')
    transactions = Transaction.objects.filter(created_by=student_to_view)
    # Update balance in user model
    balance = calculateUserBalance(invoices, transactions)
    return render(req, 'see_more_student.html', {'user': {
        'id': student_to_view.id, 'email': student_to_view.email, 'first_name': student_to_view.first_name,
        'last_name': student_to_view.last_name,
        'balance': '£' + str(student_to_view.balance)}, 'approved': approved, 'pending': pending,
        'children': Child.objects.filter(parent=student_to_view),
        'invoices': invoices, 'balance': '£' + str(balance),
        'transactions': transactions})


def log_out(req):
    logout(req)
    return redirect('home')


def user_home(req):
    approved = Request.objects.filter(isApproved=True, user_id=req.user)
    pending = Request.objects.filter(isApproved=False, user_id=req.user)
    invoices = Invoice.objects.filter(request__isApproved=True, request__user=req.user)
    active_invoices = Invoice.objects.filter(request__isApproved=True, request__user=req.user, status='ACTIVE')
    transactions = Transaction.objects.filter(created_by=req.user)
    # Update balance in user model 
    user = User.objects.get(id=req.user.id)
    balance = calculateUserBalance(invoices, transactions)
    user.balance = balance
    user.save()

    return render(req, 'user_home.html',
                  {'approved': approved, 'pending': pending, 'children': Child.objects.filter(parent=req.user),
                   'invoices': active_invoices, 'balance': balance, 'transactions': transactions})


def calculateUserBalance(invoices, transactions):
    total_due = 0
    total_paid = 0
    for invoice in invoices:
        total_due += invoice.amount_to_be_paid
    for transaction in transactions:
        total_paid += transaction.amount
    return round(total_due  - total_paid, 2)


def make_request(req):
    if req.method == 'POST':
        form = forms.RequestForm(user=req.user, data=req.POST)
        if form.is_valid():
            request = form.save(user_id=req.user)
            return redirect_to_home(get_user(req))
    else:
        form = forms.RequestForm(user=req.user)
    return render(req, 'make_request.html', {'form': form})


def edit_request(req, requestId):
    try:
        request = Request.objects.get(request_id=requestId)
    except Request.DoesNotExist:
        return redirect_to_home(get_user(req))
    # Checks if the user owns the request to edit them
    if request.user_id == get_user(req).id:
        if req.method == 'POST':
            form = forms.EditRequestForm(user=req.user, data=req.POST)
            form.helper.form_action = reverse('edit_request', args=[request.request_id])
            if form.is_valid():
                edit = form.save(request=request)
                return redirect_to_home(get_user(req))
        else:
            form = forms.EditRequestForm(user=req.user, instance=request)
        return render(req, 'make_request.html', {'form': form})
    else:
        return redirect_to_home(get_user(req))


def see_more_request(req, requestId):
    try:
        request = Request.objects.get(request_id=requestId)
    except Request.DoesNotExist:
        return redirect_to_home(get_user(req))
    # Can only see their own requests
    if request.user_id == get_user(req).id:
        return render(req, 'see_more_request.html', {'request': request})
    else:
        return redirect_to_home(get_user(req))


@login_required(login_url='log_in')
def register_child(req):
    if req.method == 'POST':
        form = forms.RegisterChildForm(req.POST)
        if form.is_valid():
            form.save(parent=req.user)
            return redirect_to_home(get_user(req))
    else:
        form = forms.RegisterChildForm()
    return render(req, 'register_child.html', {'form': form})


@login_required(login_url='log_in')
def edit_child(req, child_id):
    child_to_change = Child.objects.get(id=child_id)
    if child_to_change is None or (child_to_change.parent != req.user and not req.user.is_superuser):
        return redirect_to_home(get_user(req))
    if req.method == 'POST':
        form = forms.EditChildForm(req.POST, instance=child_to_change)
        if form.is_valid():
            form.save()
            return redirect_to_home(get_user(req))
        messages.add_message(req, messages.ERROR, "Invalid details.")

    form = forms.EditChildForm(instance=child_to_change)
    return render(req, 'edit_child.html', {'form': form, 'child': child_to_change})


@login_required(login_url='log_in')
def delete_child(req, child_id):
    child = Child.objects.get(id=child_id)
    if child is not None and (child.parent == req.user or req.user.is_superuser):
        child.delete()
    return redirect_to_home(get_user(req))


@staff_member_required(login_url="log_in")
def admin_home(req):
    lesson_requests = Request.objects.filter(isApproved=False)
    approved_request = Request.objects.filter(isApproved=True)
    users = User.objects.filter(is_active=True)

    for user in users:
        user.generateInvoices()
        user.generateChildInvoices()
        user.updateBalance()

    # invoices = Invoice.objects.filter(request__isApproved=True)
    invoices = Invoice.objects.all()
    transactions = Transaction.objects.all()

    return render(req, 'admin_home.html', {'requests': lesson_requests, 'approved': approved_request, 'users': [
        {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name,
         'balance': '£' + str(user.balance)} for user in users if not user.is_staff], 'invoices': invoices,
                                           'transactions': transactions})


@staff_member_required(login_url="log_in")
def approve_request(req, requestId):

    try:
        lessonRequestObject = Request.objects.get(pk=requestId)
    except Request.DoesNotExist:
        return redirect_to_home(get_user(req))

    if req.method == 'POST':
        form = forms.ApproveForm(req.POST)
        # form.helper.form_action = reverse('approve', args=[request.request_id])
        form.helper.form_action = reverse('approve', kwargs={'requestId': requestId})
        if form.is_valid():
            delete_invoice(requestId)  # delete the old invoice if exists
            createInvoice(requestId)  # create an updated invoice
            approve = form.save(request=lessonRequestObject)
            return redirect_to_home(get_user(req))
        else:
            messages.add_message(req, messages.ERROR, "Invalid input into the Form.")
    else:
        form = forms.ApproveForm()
    return render(req, 'approve_request.html', {'form': form, 'request': lessonRequestObject})


def delete_invoice(requestId):
    """ Deletes the old invoice associated with the request if it exists """
    try:
        Invoice.objects.get(request=requestId).delete()
    except Invoice.DoesNotExist:
        pass
    """
    try:
        invoice = Invoice.objects.get(request=requestId)
        invoice.delete()
    except Invoice.DoesNotExist:
        pass
    """


@staff_member_required(login_url="log_in")
def deleteInvoice(req, invoiceId):
    try:
        Invoice.objects.get(request=invoiceId).delete()
    except Invoice.DoesNotExist:
        return redirect_to_home(get_user(req))

def delete_request(req, requestId):
    try:
        request = Request.objects.get(request_id=requestId)
    except Request.DoesNotExist:
        return redirect_to_home(get_user(req))
    # Redirects staff user to admin home page
    if get_user(req).is_staff:
        request.delete()
        return redirect('admin_home')
    else:
        # Checks whether or not the user owns the request they want to delete
        if request.user_id == get_user(req).id:
            if not request.isApproved:
                request.delete()
        return redirect('user_home')


@user_passes_test(lambda u: u.is_superuser, login_url="log_in")
def director_home(req):
    users = User.objects.filter(is_active=True)
    lesson_requests = Request.objects.filter(isApproved=False)
    approved_request = Request.objects.filter(isApproved=True)
    return render(req, 'director_home.html', {'users': [
        {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name,
         'balance': '£' + str(user.balance / 100), 'is_staff': "✓" if user.is_staff else "✗",
         'is_superuser': "✓" if user.is_superuser else "✗"}
        for user in users],
        'requests': lesson_requests, 'approved': approved_request
    })


@user_passes_test(lambda u: u.is_superuser, login_url="log_in")
def toggle_admin(req, user_id):
    user = User.objects.get(id=user_id)
    if not user.is_superuser:
        user.is_staff = not user.is_staff
        user.save()
    return redirect_to_home(get_user(req))


def redirect_to_home(user):
    if user.is_superuser:
        return redirect('director_home')
    elif user.is_staff:
        return redirect('admin_home')
    else:
        return redirect('user_home')


@user_passes_test(lambda u: u.is_superuser, login_url="log_in")
def delete_user(req, user_id):
    user = User.objects.get(id=user_id)
    if not user.is_superuser:
        user.delete()
    return redirect_to_home(get_user(req))


def createInvoice(inpRequestId):

    # Helper function to generate the correct invoice number
    def increment_invoice_number(inpRequest):
        last_invoice = Invoice.objects.filter(request__user=inpRequest.user).order_by('created_date').last()
        if not last_invoice:
            # this is the first invoice for the user
            first_part = str(inpRequest.user.id).zfill(4)
            return first_part + '-001'
        invoice_no = last_invoice.invoice_number
        new_invoice_no = str(int(invoice_no[5:]) + 1)
        new_invoice_no = invoice_no[0:-(len(new_invoice_no))] + new_invoice_no
        return new_invoice_no

    # Not essential to validate parameter as it is only called from within the approve_request method with valid input
    # but it is good practice nonetheless
    try:
        request = Request.objects.get(request_id=inpRequestId)
    except Request.DoesNotExist:
        return redirect('admin_home')  # go to admin home page if request does not exist

    new_invoice = Invoice.objects.create(request=request, amount_to_be_paid=request.get_total_amount_payable(),
                                         invoice_number=increment_invoice_number(request))
    new_invoice.updateRequestInvoice()
    new_invoice.save()


@staff_member_required(login_url="log_in")
@user_passes_test(lambda u: u.is_staff, login_url="log_in")
def create_transaction(req):

    def close_invoice(transaction):
        associated_invoice = transaction.invoice
        if transaction.amount >= associated_invoice.amount_to_be_paid:
            associated_invoice.status = 'CLOSED'
            associated_invoice.save()

    if req.method == 'POST':
        form = forms.TransactionForm(req.POST)
        form.helper.form_action = reverse('create_transaction')
        if form.is_valid():
            # transactionObject = Transaction.objects.create(invoice=invoice)
            payment = form.save(user=get_user(req))
            close_invoice(payment)
            return redirect_to_home(get_user(req))
    else:
        form = forms.TransactionForm()
    return render(req, 'create_transaction.html', {'form': form})

