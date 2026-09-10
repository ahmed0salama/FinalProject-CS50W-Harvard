from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Q
from django.db import transaction
from .forms import ProductForm, RegisterForm, VendorForm, UserProfileForm
from .decorators import employee_required
from .models import *
import json


def index(request):
    categories = Category.objects.all()
    products = Product.objects.select_related('category', 'active_ingredient').all()[:20]
    return render(request, "pharmacy/index.html", {
        "categories": categories,
        "products": products
    })


@employee_required
def erp_vendor_list(request):
    """عرض قائمة الموردين وإضافتهم"""
    vendors = Vendor.objects.all()
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المورد بنجاح!")
            return redirect('erp_vendors')
    else:
        form = VendorForm()

    return render(request, 'pharmacy/erp/vendor_list.html', {
        'vendors': vendors,
        'form': form
    })


@employee_required
def erp_purchase_order_list(request):
    orders = PurchaseOrder.objects.select_related('vendor', 'created_by').prefetch_related('items__product').order_by('-created_at')
    return render(request, 'pharmacy/erp/purchase_orders.html', {'orders': orders})


@employee_required
@transaction.atomic
def erp_purchase_order_create(request):
    """إنشاء فاتورة شراء جديدة وزيادة رصيد المخزن"""
    vendors = Vendor.objects.all()
    products = Product.objects.filter(is_deleted=False)

    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')  # بالعبوات (Packages)
        prices = request.POST.getlist('purchase_price[]')

        if not vendor_id or not product_ids:
            messages.error(request, "يرجى اختيار المورد وإضافة منتج واحد على الأقل.")
            return redirect('erp_purchase_create')

        vendor = get_object_or_404(Vendor, pk=vendor_id)
        
        # إنشاء أمر الشراء
        po = PurchaseOrder.objects.create(
            vendor=vendor,
            created_by=request.user,
            total_amount=0.00
        )

        total = 0.00
        for pid, qty, price in zip(product_ids, quantities, prices):
            if not pid or not qty or not price:
                continue

            product = Product.objects.select_for_update().get(pk=pid)
            qty_pkg = int(qty)
            buy_price = float(price)
            subtotal = qty_pkg * buy_price
            total += subtotal

            # إنشاء عنصر الفاتورة
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=product,
                quantity_packages=qty_pkg,
                unit_purchase_price=buy_price,
                subtotal=subtotal
            )

            # زيادة مخزن المنتج آلياً بالوحدات الفرعية
            product.stock_in_sub_units += (qty_pkg * product.units_per_package)
            product.save()

        po.total_amount = total
        po.save()

        messages.success(request, f"تم تسجيل فاتورة الشراء #{po.id} بنجاح وتحديث رصيد المخزن!")
        return redirect('erp_purchases')

    return render(request, 'pharmacy/erp/purchase_form.html', {
        'vendors': vendors,
        'products': products
    })


@employee_required
@transaction.atomic
def api_pos_checkout(request):
    """معالجة عملية البيع وخصم المخزون وتسجيل الدفع الجزئي/الآجل"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            client_id = data.get("client_id")
            items = data.get("items", []) # [{product_id, quantity, unit_type, unit_price}]
            amount_paid = float(data.get("amount_paid", 0.00))

            if not items:
                return JsonResponse({"error": "Cart is empty"}, status=400)

            client = None
            if client_id:
                client = get_object_or_404(User, pk=client_id)

            # إنشاء فاتورة المبيعات
            sales_order = SalesOrder.objects.create(
                client=client,
                processed_by=request.user,
                status=SalesOrder.Status.COMPLETED,
                amount_paid=amount_paid
            )

            total_amount = 0.00

            # إضافة المنتجات وخصم المخزون آلياً
            for item in items:
                product = Product.objects.select_for_update().get(pk=item["product_id"])
                quantity = int(item["quantity"])
                unit_type = item["unit_type"] # "PACKAGE" or "SUB_UNIT"
                
                unit_price = float(product.package_price if unit_type == "PACKAGE" else product.sub_unit_price)
                subtotal = unit_price * quantity
                total_amount += subtotal

                # حساب كمية الخصم من المخزون بالوحدات الفرعية
                stock_deduction = quantity * product.units_per_package if unit_type == "PACKAGE" else quantity

                if product.stock_in_sub_units < stock_deduction:
                    raise ValueError(f"Insufficient stock for {product.name}")

                product.stock_in_sub_units -= stock_deduction
                product.save()

                SalesOrderItem.objects.create(
                    sales_order=sales_order,
                    product=product,
                    unit_type=unit_type,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )

            # حساب المتبقي وتحديث الفاتورة ورصيد العميل
            remaining = total_amount - amount_paid
            sales_order.total_amount = total_amount
            sales_order.remaining_balance = max(0.00, remaining)

            if remaining <= 0:
                sales_order.payment_status = SalesOrder.PaymentStatus.PAID
            elif amount_paid > 0:
                sales_order.payment_status = SalesOrder.PaymentStatus.PARTIAL
            else:
                sales_order.payment_status = SalesOrder.PaymentStatus.UNPAID

            sales_order.save()

            # تسديد المتبقي على مديونية العميل
            if remaining > 0 and client:
                balance = float(client.balance) + round(remaining, 2)
                client.balance = balance
                client.save()

            return JsonResponse({
                "message": "Sale order completed successfully!",
                "order_id": sales_order.id,
                "total_amount": total_amount,
                "amount_paid": amount_paid,
                "remaining_balance": max(0.00, remaining)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@employee_required
def erp_pos_view(request):
    """شاشة نقطة البيع السريعة (POS Cashier Interface)"""
    clients = User.objects.filter(role=User.Role.CLIENT)
    products = Product.objects.filter(is_deleted=False, stock_in_sub_units__gt=0)
    
    return render(request, "pharmacy/erp/pos.html", {
        "clients": clients,
        "products": products
    })


@employee_required
def erp_dashboard(request):
    """اللوحة الرئيسية لـ ERP"""
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_in_sub_units__lte=20)
    total_categories = Category.objects.count()
    total_vendors = Vendor.objects.count()
    
    # حساب إجمالي قطع المخزون وقيمتها المالية
    stock_stats = Product.objects.aggregate(
        total_sub_units=Sum('stock_in_sub_units')
    )

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products[:5],
        'total_categories': total_categories,
        'total_vendors': total_vendors,
        'total_stock_items': stock_stats['total_sub_units'] or 0,
    }
    return render(request, 'pharmacy/erp/dashboard.html', context)


@employee_required
def erp_inventory_list(request):
    """إدارة وشاشة المخزون والمنتجات"""
    search_query = request.GET.get('q', '')
    products = Product.objects.all().select_related('category', 'active_ingredient')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(active_ingredient__name__icontains=search_query)
        )

    return render(request, 'pharmacy/erp/inventory_list.html', {
        'products': products,
        'search_query': search_query
    })


@employee_required
def erp_product_create(request):
    """إضافة منتج جديد للمخزن"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"تمت إضافة المنتج '{product.name}' بنجاح!")
            return redirect('erp_inventory')
    else:
        form = ProductForm()

    return render(request, 'pharmacy/erp/product_form.html', {
        'form': form,
        'title': 'إضافة منتج جديد'
    })


@employee_required
def erp_product_edit(request, product_id):
    """تعديل بيانات منتج موجود"""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث بيانات '{product.name}' بنجاح!")
            return redirect('erp_inventory')
    else:
        form = ProductForm(instance=product)

    return render(request, 'pharmacy/erp/product_form.html', {
        'form': form,
        'product': product,
        'title': f'تعديل المنتج: {product.name}'
    })


@employee_required
def erp_stock_adjust(request, product_id):
    """تعديل كمية المخزون بشكل سريع (إضافة/خصم شحنة)"""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        adjustment = int(request.POST.get('amount', 0))
        unit_type = request.POST.get('unit_type', 'sub_unit') # package or sub_unit
        
        if unit_type == 'package':
            adjustment_sub_units = adjustment * product.units_per_package
        else:
            adjustment_sub_units = adjustment

        new_stock = product.stock_in_sub_units + adjustment_sub_units
        if new_stock < 0:
            messages.error(request, "لا يمكن أن يكون المخزون النهائي بالسالب!")
        else:
            product.stock_in_sub_units = new_stock
            product.save()
            messages.success(request, f"تم تحديث مخزون '{product.name}' بنجاح! الرصيد الحالي: {product.stock_in_sub_units} {product.sub_unit}")

    return redirect('erp_inventory')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث البيانات الشخصية بنجاح!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    orders = request.user.sales_orders.order_by('-created_at')[:5]

    return render(request, 'pharmacy/profile.html', {
        'form': form,
        'orders': orders
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            # Default role for public registration is CLIENT
            user.role = user.Role.CLIENT
            user.save()
            
            login(request, user)
            messages.success(request, f"Account created successfully. Welcome, {user.username}!")
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'pharmacy/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                
                # Redirect employees/admins to ERP Dashboard, clients to Index
                if user.is_employee_or_admin():
                    return redirect('erp_dashboard')
                return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'pharmacy/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    alternatives = []
    
    if product.active_ingredient:
        alternatives = Product.objects.filter(
            active_ingredient=product.active_ingredient
        ).exclude(pk=product.id)

    return render(request, "pharmacy/product_detail.html", {
        "product": product,
        "alternatives": alternatives
    })


def api_search_products(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    products = Product.objects.select_related('category', 'active_ingredient').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(active_ingredient__name__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand or "",
            "category": p.category.name if p.category else "",
            "price": float(p.package_price),
            "stock": p.stock_in_sub_units,
            "image_url": p.image_url or "",
            "requires_prescription": p.requires_prescription,
            "active_ingredient": p.active_ingredient.name if p.active_ingredient else None
        })

    return JsonResponse({"products": data})


def api_get_alternatives(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if not product.active_ingredient:
        return JsonResponse({"alternatives": []})

    alternatives = Product.objects.filter(
        active_ingredient=product.active_ingredient
    ).exclude(pk=product.id)

    data = [{
        "id": a.id,
        "name": a.name,
        "brand": a.brand or "",
        "price": float(a.package_price),
        "stock": a.stock_in_sub_units,
        "image_url": a.image_url or ""
    } for a in alternatives]

    return JsonResponse({"alternatives": data})


def api_cart_reserve(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key

            product = get_object_or_404(Product, pk=product_id)
            
            cart_item, created = CartReservation.objects.get_or_create(
                session_id=session_id,
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({"message": "Product reserved successfully", "status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def api_get_cart(request):
    if not request.session.session_key:
        return JsonResponse({"cart": [], "total": 0})

    session_id = request.session.session_key
    items = CartReservation.objects.filter(session_id=session_id).select_related('product')

    cart_data = []
    total_price = 0

    for item in items:
        subtotal = float(item.product.package_price) * item.quantity
        total_price += subtotal
        cart_data.append({
            "id": item.id,
            "product_name": item.product.name,
            "unit_price": float(item.product.package_price),
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return JsonResponse({"cart": cart_data, "total_amount": total_price})