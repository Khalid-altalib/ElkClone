from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from lessons.auth import MSMSUserManager
from django.db import models
from multiselectfield import MultiSelectField
import datetime as dt
from django.utils import timezone


# Create your models here.

class User(AbstractUser):
    username = None
    first_name = models.CharField(blank=True, unique=False, max_length=50)
    last_name = models.CharField(blank=True, unique=False, max_length=50)
    email = models.EmailField(unique=True, blank=False)
    balance = models.DecimalField(blank=False, max_digits=12, default=Decimal('0.00'), decimal_places=2, null=True,
                                  validators=[MinValueValidator(Decimal('0.00'))])  # Lyn version
    # balance = models.IntegerField(blank=False, unique=False) # my version

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['balance']

    objects = MSMSUserManager()

    def generateInvoices(self):

        approved = Request.objects.filter(isApproved=True, user=self.id, invoice=None)
        for request in approved:
            createInvoice(request)

    def generateChildInvoices(self):
        for child in Child.objects.filter(parent=self):
            approvedChild = Request.objects.filter(isApproved=True, child=child, invoice=None)
            for request in approvedChild:
                createInvoice(request)
        self.updateBalance()


    def updateBalance(self):
        self.generateInvoices()
        invoices = Invoice.objects.filter(request__isApproved=True, request__user=self.id)
        transactions = Transaction.objects.filter(created_by=self.id)
        self.balance = calculateUserBalance(invoices, transactions)
        self.save()


def calculateUserBalance(invoices, transactions):
    total_due = 0
    total_paid = 0
    for invoice in invoices:
        total_due += invoice.amount_to_be_paid
    for transaction in transactions:
        total_paid += transaction.amount
    return round(total_due - total_paid, 2)


def createInvoice(inpRequest):

    # Helper function to generate the correct invoice number
    def increment_invoice_number():
        last_invoice = Invoice.objects.filter(request__user=inpRequest.user).order_by('created_date').last()
        if not last_invoice:
            # this is the first invoice for the user
            first_part = str(inpRequest.user.id).zfill(4)
            return first_part + '-001'
        invoice_no = last_invoice.invoice_number
        new_invoice_no = str(int(invoice_no[5:]) + 1)
        new_invoice_no = invoice_no[0:-(len(new_invoice_no))] + new_invoice_no
        return new_invoice_no

    if ((not inpRequest.isApproved) or (inpRequest.DoesNotExist) or (inpRequest.invoice)):
        # raise ValidationError('Invalid Request')
        return
    new_invoice = Invoice.objects.create(request=inpRequest, amount_to_be_paid=inpRequest.get_total_amount_payable(),
                                         invoice_number=increment_invoice_number())
    new_invoice.updateRequestInvoice()
    new_invoice.save()
    return new_invoice


class Child(models.Model):
    name = models.CharField(blank=False, unique=False, max_length=50)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_name_and_parent_combination",
                fields=('name', 'parent')
            )
        ]


class Request(models.Model):
    """Model for a request"""
    # Variable for the choices provided
    # The choices for availability
    AVAILABILITY_CHOICES = [
        ('MONDAYAM', 'Monday AM'),
        ('MONDAYPM', 'Monday PM'),
        ('TUESDAYAM', 'Tuesday AM'),
        ('TUESDAYPM', 'Tuesday PM'),
        ('WEDNESDAYAM', 'Wednesday AM'),
        ('WEDNESDAYPM', 'Wednesday PM'),
        ('THURSDAYAM', 'Thursday AM'),
        ('THURSDAYPM', 'Thursday PM'),
        ('FRIDAYAM', 'Friday AM'),
        ('FRIDAYPM', 'Friday PM'),
        ('SATURDAYAM', 'Saturday AM'),
        ('SATURDAYPM', 'Saturday PM'),
        ('SUNDAYAM', 'Sunday AM'),
        ('SUNDAYPM', 'Sunday PM'),
    ]
    # The choices of days to choose
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]

    TIME_CHOICES = [
        (dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)
    ]

    request_id = models.AutoField(
        primary_key=True
    )

    # Email to identify the user making request
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # The child this request is on behalf of
    child = models.ForeignKey(Child, blank=True, null=True, on_delete=models.CASCADE)

    # Submission_date to help administrator select start date
    submission_date = models.DateTimeField(
        auto_now_add=True
    )

    # Availability is stored as a charField with list of selected options
    availability = MultiSelectField(
        choices=AVAILABILITY_CHOICES,
        default="SUNDAYPM",
        max_length=200
    )

    # Total number of lessons for a request in a term
    number_of_lessons = models.IntegerField(
        validators=[MaxValueValidator(
            50,
            message="You cannot have more than 50 lessons per request."
        ),
            MinValueValidator(
                1,
                message="You cannot have less than 1 lesson per request."
            )]
    )

    # The time between lessons in weeks
    interval = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(
            4,
            message="You cannot have more than 4 weeks between lessons."
        ),
            MinValueValidator(
                1,
                message="You cannot have less than 1 weeks between lesson."
            )]
    )

    # How long each lesson lasts in minutes
    duration = models.IntegerField(
        default=60,
        validators=[MaxValueValidator(
            180,
            message="You cannot have more than 180 minitues per lesson."
        ),
            MinValueValidator(
                30,
                message="You need at least 30 minitues per lesson"
            )]
    )

    # User can specify what the lessons are for
    lesson_content = models.CharField(
        max_length=50,
    )

    # User can select a teacher if they have one in mind
    # Admin will select a teacher for the user if it is blank
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="teacher"
    )

    # the day that the admin schedules the class
    class_Day = models.CharField(
        default='MONDAY',
        max_length=10,
        choices=DAY_CHOICES
    )

    # the time the admin schedules the class
    class_Time = models.TimeField(
        default=dt.time(8),
        choices=TIME_CHOICES
    )

    # the start date scheduled by the admin
    start_Date = models.DateTimeField(
        default=dt.date(2021, 1, 1)
    )

    # Shows if the request has been approved or not by the administrator
    isApproved = models.BooleanField(
        default=False,
    )

    invoice = models.OneToOneField('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='request.masterInvoice+')
    def clean(self):
        if self.child is not None and self.user != self.child.parent:
            raise ValidationError("The selected Child must have this User as its parent!")
        if self.teacher is not None and not self.teacher.is_staff:
            raise ValidationError("The selected Teacher must be a Staff Member!")

    @property
    def get_total_class_duration_in_minutes(self):
        return self.number_of_lessons * self.duration

    cost_per_minute = Decimal(10.00)  # Fixed cost per minute for any lesson

    def get_total_amount_payable(self):
        return Decimal(self.get_total_class_duration_in_minutes * self.cost_per_minute)

    def __str__(self):
        # return the request ID, the user & the invoice associated with the request
        return f"Request ID: {self.request_id}, User: {self.user}, Invoice: {self.invoice}"
        # return f"Request {self.request_id}"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]
    invoice_number = models.CharField(unique=True, blank=False, max_length=8,
                                      validators=[RegexValidator(regex='^\\d\\d\\d\\d-\\d\\d\\d$')],
                                      help_text="Format: xxxx-xxx,required")
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='invoice.masterRequest+')
    created_date = models.DateTimeField(blank=False, default=timezone.now)
    amount_to_be_paid = models.DecimalField(blank=False, max_digits=12, decimal_places=2, null=True,
                                            validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="ACTIVE",
        max_length=7
    )
    """
    def clean(self):
        if self.status is not "ACTIVE" or self.invoice_number is None or self.invoice_number == "":
            raise ValidationError("The selected Invoice is not Active!")
        if self.amount_to_be_paid is None or self.amount_to_be_paid == "":
            raise ValidationError("The selected Invoice has no amount to be paid!")
        if self.request is None or self.request == "":
            raise ValidationError("The selected Invoice has no Request associated with it!")
        if self.request.isApproved is False:
            raise ValidationError("The selected Request is not Approved!")

    """

    def updateRequestInvoice(self):
        self.request.invoice = self
        self.request.save()
        # print("Request Invoice Updated inside Invoice Model") # DEBUG

    def __str__(self):
        return self.invoice_number


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=False,
                                 validators=[MinValueValidator(Decimal('0.01'))])
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True)
    date_paid = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT, related_name='student_user')
    administrated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='admin_user')
    def clean(self):
        if self.amount is None or self.amount == "":
            raise ValidationError("The selected Transaction has no amount!")
        if self.invoice is None or self.invoice == "":
            raise ValidationError("The selected Transaction has no Invoice associated with it!")
        if self.date_paid is None or self.date_paid == "":
            raise ValidationError("The selected Transaction has no Date Paid!")
        """
        Additional constraints
        if self.created_by is None or self.created_by == "":
            raise ValidationError("The selected Transaction has no Created By!")
        if self.administrated_by is None or self.administrated_by == "":
            raise ValidationError("The selected Transaction has no Administrated By!")
        if self.invoice.status is not "ACTIVE":
            raise ValidationError("The selected Invoice is not Active!")
        if self.created_by != self.invoice.request.user:
            raise ValidationError("The selected Transaction must be created by the User associated with the Invoice!")
        if self.administrated_by.is_staff is False:
            raise ValidationError("The selected Transaction must be administrated by a Staff Member!")
        if self.invoice.amount_to_be_paid == self.amount:
            self.invoice.status = "CLOSED"
            self.invoice.save()
            # print("Invoice Closed inside Transaction Model") # DEBUG
        elif self.invoice.amount_to_be_paid > self.amount:
            self.invoice.amount_to_be_paid = self.invoice.amount_to_be_paid - self.amount
            self.invoice.save()
            # print("Invoice Amount Updated inside Transaction Model") # DEBUG
        else:
            raise ValidationError("The selected Transaction amount is invalid!")
        """
