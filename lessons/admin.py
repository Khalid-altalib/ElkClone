from django.contrib import admin
from .models import *
# from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
admin.site.register(Request)

admin.site.register(User)


class TransactionAdmin(admin.ModelAdmin): 
    list_display=('id','get_invoice_number','amount_display','date_paid','created_by')
    list_display_links=('id','get_invoice_number',)
    search_fields=('created_by__email',)
    ordering=('date_paid',)
    
    def amount_display(self, obj):
        return "$%s" % obj.amount
    amount_display.short_description = 'Amount Paid'
    
    def get_invoice_number(self, obj): 
        return obj.invoice.invoice_number
    get_invoice_number.short_description='Invoice Number'

admin.site.register(Transaction, TransactionAdmin)

class InvoiceAdmin(admin.ModelAdmin):
    list_display=('id','invoice_number', 'get_request_id', 'created_date','amount_to_be_paid','status')
    list_display_links=('id', 'get_request_id',)
    list_filter=('status',)
    search_fields=('request__user__email',)
    ordering=('created_date',)

    def get_request_id (self, obj): 
        return obj.request.request_id
    get_request_id.short_description = 'Request ID'  
    
admin.site.register(Invoice, InvoiceAdmin)
