from django.core.management.base import BaseCommand, CommandError

from lessons.models import User, Transaction, Child, Invoice, Request


class Command(BaseCommand):
    """
    Deletes all non-superuser users, plus the seeded directors. Be careful!!
    """

    def handle(self, *args, **options):
        print("Unseeding...")
        # Transactions are deleted first because they have a foreign key to User with a Protected constraint
        for j in Transaction.objects.all(): # delete all transactions
            j.delete()
        for i in Invoice.objects.all(): # delete all invoices
            i.delete()
        for h in Request.objects.all(): # delete all requests
            h.delete()
        for k in Child.objects.all(): # delete all children
            k.delete()
        for o in User.objects.all():
            if (not o.is_superuser) or (o.email == 'marty.major@example.org'):
                o.delete()
        print("Done")

