from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from decimal import Decimal
from collections import defaultdict

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.db.models import Sum
from xhtml2pdf import pisa

from .models import Product, Supplier, Invoice, Category, SupplierTransaction


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully")

        return redirect('login')

    return render(request, 'inventory/register.html')


# ================= LOGIN =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'inventory/login.html')


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= DASHBOARD =================
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'inventory/dashboard.html', {
        'total_products': Product.objects.count(),
        'low_stock': Product.objects.filter(quantity__lt=5).count(),
        'total_suppliers': Supplier.objects.count(),
        'recent_products': Product.objects.all().order_by('-id')[:5]
    })


# ================= PRODUCTS =================
@login_required(login_url='login')
def product_list(request):
    return render(request, 'inventory/product_list.html', {
        'products': Product.objects.all()
    })


@login_required(login_url='login')
def add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get('name'),
            category=Category.objects.get(id=request.POST.get('category')),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity')
        )
        return redirect('product_list')

    return render(request, 'inventory/add_product.html', {
        'categories': categories
    })


@login_required(login_url='login')
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.category = Category.objects.get(id=request.POST.get('category'))
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.save()
        return redirect('product_list')

    return render(request, 'inventory/update_product.html', {
        'product': product,
        'categories': categories
    })


@login_required(login_url='login')
def delete_product(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    return redirect('product_list')


# ================= SUPPLIERS =================
@login_required(login_url='login')
def supplier_list(request):
    suppliers = Supplier.objects.all()
    supplier_data = []

    for supplier in suppliers:
        transactions = SupplierTransaction.objects.filter(supplier=supplier)

        # 🔥 GROUP PRODUCTS
        product_summary = defaultdict(lambda: {'IN': 0, 'OUT': 0})

        for t in transactions:
            product_summary[t.product.name][t.transaction_type] += t.quantity

        total = transactions.aggregate(total=Sum('quantity'))['total'] or 0

        supplier_data.append({
            'supplier': supplier,
            'products': dict(product_summary),
            'total': total
        })

    return render(request, 'inventory/supplier_list.html', {
        'supplier_data': supplier_data
    })


@login_required(login_url='login')
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        return redirect('supplier_list')

    return render(request, 'inventory/update_supplier.html', {'supplier': supplier})


@login_required(login_url='login')
def delete_supplier(request, pk):
    get_object_or_404(Supplier, pk=pk).delete()
    return redirect('supplier_list')


# ================= TRANSACTION =================
@login_required(login_url='login')
def add_transaction(request):
    if request.method == "POST":
        supplier = Supplier.objects.get(id=request.POST.get('supplier'))
        product = Product.objects.get(id=request.POST.get('product'))
        quantity = int(request.POST.get('quantity'))
        t_type = request.POST.get('type')

        SupplierTransaction.objects.create(
            supplier=supplier,
            product=product,
            quantity=quantity,
            transaction_type=t_type
        )

        # 🔥 AUTO STOCK UPDATE
        if t_type == 'IN':
            product.quantity += quantity
        else:
            product.quantity -= quantity

        product.save()

        return redirect('product_list')

    return render(request, 'inventory/add_transaction.html', {
        'suppliers': Supplier.objects.all(),
        'products': Product.objects.all()
    })


# ================= REPORTS =================
@login_required(login_url='login')
def reports(request):
    return render(request, 'inventory/reports.html', {
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(quantity__lt=5)
    })


# ================= INVOICE =================
@login_required(login_url='login')
def generate_invoice(request, pk):
    product = get_object_or_404(Product, id=pk)

    price = Decimal(product.price)
    tax = price * Decimal("0.18")
    total = price + tax

    invoice = Invoice.objects.create(
        product=product,
        customer_name="Customer",
        customer_address="Address",
        city="City",
        country="India",
        quantity=1,
        price=price,
        total=total
    )

    template = get_template("inventory/invoice.html")

    html = template.render({
        "invoice": invoice,
        "product": product,
        "quantity": 1,
        "price": price,
        "tax": tax,
        "total": total,
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response