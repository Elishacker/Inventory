
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Category, Product, Sale, SaleItem
from .forms import LoginForm, CategoryForm, ProductForm, UserForm
from .permissions import admin_required, seller_required

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password')
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Simple dashboard with key stats
    product_count = Product.objects.count()
    seller_sales = Sale.objects.filter(seller=request.user).count() if not request.user.is_staff else None
    total_sales = Sale.objects.count()
    latest_sales = Sale.objects.order_by('-created_at')[:5]

    # Daily total (sum of today's sales)
    today = timezone.localdate()
    daily_total = Sale.objects.filter(created_at__date=today).aggregate(total=models.Sum('total'))['total'] or 0

    # Most bought product
    most_bought_item = (
        SaleItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')
        .first()
    )

    # Format for easy display
    most_bought = None
    if most_bought_item:
        most_bought = f"{most_bought_item['product__name']}"

    return render(request, 'core/dashboard.html', {
        'product_count': product_count,
        'seller_sales': seller_sales,
        'total_sales': total_sales,
        'latest_sales': latest_sales,
        'daily_total': daily_total,
        'most_bought': most_bought,
    })

# ----- Admin: Categories -----
@admin_required
def category_list(request):
    categories = Category.objects.order_by('name')
    return render(request, 'core/category_list.html', {'categories': categories})

@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created')
        return redirect('category_list')
    return render(request, 'core/category_form.html', {'form': form, 'title': 'New Category'})

@admin_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated')
        return redirect('category_list')
    return render(request, 'core/category_form.html', {'form': form, 'title': 'Edit Category'})

@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted')
        return redirect('category_list')
    return render(request, 'core/confirm_delete.html', {'object': category, 'back_url': 'category_list'})

# ----- Admin: Products -----
@admin_required
def product_list(request):
    products = Product.objects.select_related('category').order_by('name')
    return render(request, 'core/product_list.html', {'products': products})

@admin_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product created')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'New Product'})

@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted')
        return redirect('product_list')
    return render(request, 'core/confirm_delete.html', {'object': product, 'back_url': 'product_list'})

# ----- Admin: Users -----
@admin_required
def user_list(request):
    users = User.objects.order_by('username')
    return render(request, 'core/user_list.html', {'users': users})

@admin_required
def user_create(request):
    form = UserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            is_staff=form.cleaned_data['is_staff'],
            is_active=form.cleaned_data['is_active'],
        )
        pwd = form.cleaned_data.get('password')
        user.set_password(pwd or User.objects.make_random_password())
        user.save()
        messages.success(request, 'User created')
        return redirect('user_list')
    return render(request, 'core/user_form.html', {'form': form, 'title': 'New User'})

@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.is_staff = form.cleaned_data['is_staff']
        user.is_active = form.cleaned_data['is_active']
        pwd = form.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        user.save()
        messages.success(request, 'User updated')
        return redirect('user_list')
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Edit User'})

@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted')
        return redirect('user_list')
    return render(request, 'core/confirm_delete.html', {'object': user, 'back_url': 'user_list'})

# ----- Seller: POS & Sales -----
@seller_required
def pos_view(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    if request.method == 'POST':
        # expects POST with items[] = product_id|qty per line, or simple form fields
        items = []
        for key, val in request.POST.items():
            if key.startswith('qty_'):
                pid = key.split('_', 1)[1]
                try:
                    qty = int(val)
                except:
                    qty = 0
                if qty > 0:
                    items.append((int(pid), qty))

        if not items:
            messages.error(request, 'No items selected')
            return redirect('pos')

        with transaction.atomic():
            sale = Sale.objects.create(seller=request.user, total=0)
            total = 0
            for pid, qty in items:
                product = get_object_or_404(Product, pk=pid, is_active=True)
                if product.stock < qty:
                    transaction.set_rollback(True)
                    messages.error(request, f'Insufficient stock for {product.name}')
                    return redirect('pos')
                product.stock -= qty
                product.save()
                line_price = product.price
                SaleItem.objects.create(sale=sale, product=product, quantity=qty, price=line_price)
                total += line_price * qty
            sale.total = total
            sale.save()
            messages.success(request, f'Sale #{sale.id} recorded. Total: {total}')
            return redirect('sales_list')

    return render(request, 'core/pos.html', {'products': products})

@login_required
def sales_list(request):
    qs = Sale.objects.all().order_by('-created_at')
    if not request.user.is_staff:
        qs = qs.filter(seller=request.user)
    return render(request, 'core/sales_list.html', {'sales': qs})

# ----- Admin: Reports -----
@admin_required
def sales_report(request):
    # Aggregate total sales per day and by seller
    from django.db.models.functions import TruncDate
    daily = (
        Sale.objects
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .order_by('-day')
        .annotate(total=models.Sum('total'), count=models.Count('id'))
    )
    by_seller = (
        Sale.objects
        .values('seller__username')
        .order_by('seller__username')
        .annotate(total=models.Sum('total'), count=models.Count('id'))
    )
    return render(request, 'core/reports.html', {'daily': daily, 'by_seller': by_seller})
