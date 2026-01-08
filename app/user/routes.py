from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.user import user
from app import db, get_client_ip
from app.models import User, Product, Order, OrderItem, OrderStatusEnum
from decimal import Decimal
import re
import logging

email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Профиль пользователя"""
    if request.method == 'POST':
        current_user.fullname = request.form.get('full_name')
        current_user.email = request.form.get('email', '').strip()
        current_user.address = request.form.get('address')
        current_user.phone = request.form.get('phone')

        new_password = request.form.get('password')

        if not re.match(email_pattern, current_user.email):
            flash('Введите корректный адрес электронной почты', 'error')
            return render_template('auth/register.html')

        if new_password:
            if len(new_password) < 8:
                flash('Пароль должен содержать минимум 8 символов', 'error')
                return render_template('user/profile.html')
            current_user.set_password(new_password)

        try:
            db.session.commit()
            actions_logger = logging.getLogger('app.actions')
            actions_logger.info(
                f"User profile updated: {current_user.username}",
                extra={
                    'action': 'profile_update',
                    'status': 'success',
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'entity_type': 'user',
                    'entity_id': current_user.id,
                    'ip_address': get_client_ip(),
                    'extra_data': {
                        'password_changed': bool(new_password)
                    }
                }
            )
            flash('Профиль успешно обновлен', 'success')
        except Exception as e:
            db.session.rollback()
            actions_logger = logging.getLogger('app.actions')
            actions_logger.error(
                f"Profile update failed: {str(e)}",
                exc_info=True,
                extra={
                    'action': 'profile_update',
                    'status': 'error',
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'ip_address': get_client_ip()
                }
            )
            flash('Ошибка при обновлении профиля', 'error')

    return render_template('user/profile.html')


@user.route('/cart')
@login_required
def cart():
    """Корзина"""
    cart_items = session.get('cart', [])
    products = []
    total = Decimal('0.00')

    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product and product.is_active:
            quantity = item['quantity']
            item_total = product.price * quantity
            total += item_total
            products.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })

    return render_template('user/cart.html', cart_items=products, total=total)

@user.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def cart_add(product_id):
    """Добавление товара в корзину"""
    product = Product.query.get_or_404(product_id)

    if not product.is_active:
        flash('Товар недоступен для заказа', 'error')
        return redirect(url_for('main.catalog'))

    quantity = int(request.form.get('quantity', 1))

    if quantity > product.stock_quantity:
        flash('Недостаточно товара на складе', 'error')
        return redirect(url_for('main.product_detail', slug=product.slug))

    cart = session.get('cart', [])

    # Проверяем, есть ли уже такой товар в корзине
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        cart.append({
            'product_id': product_id,
            'quantity': quantity,
        })

    session['cart'] = cart
    actions_logger = logging.getLogger('app.actions')
    actions_logger.info(
        f"Product added to cart: {product.name}",
        extra={
            'action': 'cart_add',
            'status': 'success',
            'user_id': current_user.id,
            'username': current_user.username,
            'entity_type': 'product',
            'entity_id': product_id,
            'ip_address': get_client_ip(),
            'extra_data': {
                'product_name': product.name,
                'quantity': quantity
            }
        }
    )
    flash(f'Товар "{product.name}" добавлен в корзину', 'success')

    return redirect(request.referrer or url_for ('main.catalog'))

@user.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def cart_remove(product_id):
    """Удаление товара из корзины"""
    cart = session.get('cart', [])
    product = Product.query.get(product_id)
    product_name = product.name if product else f'Product ID: {product_id}'
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    actions_logger = logging.getLogger('app.actions')
    actions_logger.info(
        f"Product removed from cart: {product_name}",
        extra={
            'action': 'cart_remove',
            'status': 'success',
            'user_id': current_user.id,
            'username': current_user.username,
            'entity_type': 'product',
            'entity_id': product_id,
            'ip_address': get_client_ip(),
            'extra_data': {
                'product_name': product_name
            }
        }
    )
    flash('Товар удален из корзины', 'success')
    return redirect(url_for('user.cart'))

@user.route('/cart/update', methods=['POST'])
@login_required
def cart_update():
    """Обновление количества товаров в корзине"""
    cart = session.get('cart', [])

    for item in cart:
        product_id = item['product_id']
        new_quantity = request.form.get(f'quantity_{product_id}')

        if new_quantity:
            quantity = int(new_quantity)
            product = Product.query.get(product_id)

            if product and 0 < quantity <= product.stock_quantity:
                item['quantity'] = quantity
            elif quantity > product.stok_quantity:
                flash(f'Недостаточно товара "{product.name}" на складе.', 'error')

    session['cart'] = cart
    return redirect(url_for('user.cart'))


@user.route('/orders')
@login_required
def orders():
    """Список заказов пользователя"""
    orders_list = (Order
                   .query
                   .filter_by(user_id=current_user.id)
                   .order_by(Order.created_at.desc())
                   .all())

    return render_template('user/orders.html', orders=orders_list)


@user.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Детали заказа пользователя"""
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('user.orders'))

    return render_template('user/order_detail.html', order=order)


@user.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    cart_items = session.get('cart', [])

    if not cart_items:
        flash('Корзина пуста', 'error')
        return redirect(url_for('user.cart'))

    # Проверяем наличие товаров и формируем список
    products = []
    total = Decimal('0.00')

    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if not product or not product.is_active:
            flash(f'Товар "{product.name if product else "Неизвестный"}" недоступен', 'error')
            return redirect(url_for('user.cart'))

        quantity = item['quantity']
        if quantity > product.stock_quantity:
            flash(f'Недостаточно товара "{product.name}" на складе', 'error')
            return redirect(url_for('user.cart'))

        item_total = product.price * quantity
        total += item_total
        products.append({
            'product': product,
            'quantity': quantity,
            'total': item_total
        })

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        phone = request.form.get('phone')
        notes = request.form.get('notes')

        if not shipping_address:
            flash('Укажите адрес доставки', 'error')
            return render_template('user/checkout.html', products=products, total=total)

        # Создаем заказ
        order = Order(
            user_id=current_user.id,
            status=OrderStatusEnum.PENDING,
            total_amount=total,
            shipping_address=shipping_address,
            phone=phone or current_user.phone,
            notes=notes
        )

        try:
            db.session.add(order)
            db.session.flush()  # Получаем ID заказа

            # Создаем позиции заказа и уменьшаем количество на складе
            for item in products:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                db.session.add(order_item)

                # Уменьшаем количество на складе
                item['product'].stock_quantity -= item['quantity']

            db.session.commit()

            # Очищаем корзину
            session['cart'] = []

            # Логируем оформление заказа
            actions_logger = logging.getLogger('app.actions')
            order_items_data = [{'product_id': item['product'].id, 'quantity': item['quantity'], 'price': str(item['product'].price)} for item in products]
            actions_logger.info(
                f"Order created: {order.id}",
                extra={
                    'action': 'order_create',
                    'status': 'success',
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'entity_type': 'order',
                    'entity_id': order.id,
                    'ip_address': get_client_ip(),
                    'extra_data': {
                        'order_id': order.id,
                        'total_amount': str(total),
                        'items_count': len(products),
                        'items': order_items_data
                    }
                }
            )

            flash('Заказ успешно оформлен!', 'success')
            return redirect(url_for('user.order_detail', order_id=order.id))
        except Exception as e:
            db.session.rollback()
            actions_logger = logging.getLogger('app.actions')
            actions_logger.error(
                f"Order creation failed: {str(e)}",
                exc_info=True,
                extra={
                    'action': 'order_create',
                    'status': 'error',
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'ip_address': get_client_ip()
                }
            )
            flash('Ошибка при оформлении заказа', 'error')

    return render_template('user/checkout.html', products=products, total=total)
