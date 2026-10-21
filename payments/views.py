from django.shortcuts import render, get_object_or_404
from .models import PaymentModel
from orders.models import OrderModel


#-------> Payment details View
def payment_detail(request, order_number):
    order = get_object_or_404(OrderModel, order_number=order_number, user=request.user)
    payments = get_object_or_404(PaymentModel, order=order, )

    con = {
        'order' : order,
        'payment' : payments
    }
    return render(request, 'payment/payment_detail.html', con)
