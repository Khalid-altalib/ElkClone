import datetime

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from lessons.models import User, Request, Child, Invoice, Transaction, createInvoice


class Command(BaseCommand):

    num_students = 100
    requestless_user_rate = 8
    pending_request_rate = 20
    no_children_rate = 20

    """
    Fills the DB with fake users.
    """

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        print("Seeding required accounts...")
        john_doe = User.objects.create_user(
            email='john.doe@example.org',
            first_name='John',
            last_name='Doe',
            password='Password123'
        )
        alice = Child.objects.create(
            name='Alice Doe',
            parent=john_doe
        )
        bob = Child.objects.create(
            name='Bob Doe',
            parent=john_doe
        )
        petra = User.objects.create_user(
            email='petra.pickles@example.org',
            first_name='Petra',
            last_name='Pickles',
            password='Password123',
            is_staff=True
        )
        david = User.objects.create_user(
            email='david.spinks@example.org',
            first_name='David',
            last_name='Spinks',
            password='Password123',
            is_staff=True
        )
        User.objects.create_superuser(
            email='marty.major@example.org',
            first_name='Marty',
            last_name='Major',
            password='Password123'
        )
        print("Seeding a random second admin account...")
        User.objects.create_user(
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            email=self.faker.email(),
            password=self.faker.password(length=12),
            is_staff=True
        )
        Request.objects.create(
            user=john_doe,
            availability='MONDAYPM',
            number_of_lessons=12,
            interval=1,
            duration=60,
            lesson_content="Basic Piano",
            teacher=petra,
            class_Day='MONDAY',
            class_Time=datetime.time(hour=16),
            start_Date=datetime.date(2022, 12, 12),
            isApproved=True
        )
        Request.objects.create(
            user=john_doe,
            availability='TUESDAYPM',
            number_of_lessons=12,
            interval=1,
            duration=60,
            lesson_content="Basic Piano",
            teacher=petra,
            class_Day='TUESDAY',
            class_Time=datetime.time(hour=16),
            start_Date=datetime.date(2022, 3, 12),
            isApproved=True,
            child=alice
        )
        Request.objects.create(
            user=john_doe,
            availability='THURSDAYPM',
            number_of_lessons=12,
            interval=1,
            duration=60,
            lesson_content="Basic Piano",
            teacher=petra,
            class_Day='THURSDAY',
            class_Time=datetime.time(hour=16),
            start_Date=datetime.date(2022, 3, 12),
            isApproved=True,
            child=bob
        )
        createInvoice(Request.objects.get(user=john_doe, child=alice))
        createInvoice(Request.objects.get(user=john_doe, child=bob))
        createInvoice(Request.objects.get(user=john_doe, child=None))
        print(f"Seeding {Command.num_students} random students...")
        for i in range(0, Command.num_students):
            new_user = User.objects.create_user(
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                email=self.faker.email(),
                password=self.faker.password(length=12)
            )
            if i % Command.no_children_rate != 0:
                new_child = Child.objects.create(
                    name=self.faker.name(),
                    parent = new_user
                )
            else:
                new_child = None
            # TODO: for students with fulfilled lesson requests: some paid, some partially paid, a couple overpaid, some unpaid.
            if i % Command.requestless_user_rate != 0:
                availability = Request.AVAILABILITY_CHOICES[i % len(Request.AVAILABILITY_CHOICES)]
                is_approved = i % Command.pending_request_rate != 0
                num_lessons = i % 10 + 1
                interval = i % 2
                duration = 30 + i/2
                lesson_content="Basic Piano" if i % 3 == 0 else "Basic Guitar" if i % 2 else "Intermediate Trumpet"
                teacher = petra if i % 2 else david
                amountmultiplier = 1 if i % 3 == 0 else 1.5 if i % 2 == 0 else 0.5 if i % 5 == 0 else 0

                if is_approved:

                    Request.objects.create(
                        user=new_user,
                        availability=availability[0],
                        number_of_lessons=num_lessons,
                        interval=interval,
                        duration=duration,
                        lesson_content=lesson_content,
                        teacher=teacher,
                        class_Day=availability[1].split(' ')[0].upper(),
                        class_Time=datetime.time(hour=(8+(i % 4)+(0 if availability[0][:-2] == 'AM' else 12))),
                        start_Date=datetime.date(2022, 12, 12 + (i % 12)),
                        isApproved=is_approved,
                        child=new_child
                    )
                    invoice = createInvoice(Request.objects.get(user=new_user))
                    if invoice:
                        Transaction.objects.create(
                            amount=invoice.amount_to_be_paid * amountmultiplier,
                            date_paid=datetime.date(2023, 12, 12 + (i % 12)),
                            created_by=Request.objects.get(user=new_user).user,
                            administrated_by=teacher,
                            invoice=invoice
                        )

                else:
                    Request.objects.create(
                        user=new_user,
                        availability=availability[0],
                        number_of_lessons=num_lessons,
                        interval=interval,
                        duration=duration,
                        lesson_content=lesson_content,
                        teacher=teacher,
                        child=new_child
                    )
            if i % 10 == 0:
                print(".", end="", flush=True)
        print("\nDone!")
