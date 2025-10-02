from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Client, BonusHistory, MessageTemplate, Organization
from .forms import AddClientForm, BonusForm, TemplateForm
import urllib.parse
import logging
from django.contrib.auth import logout

# Настройка логирования
logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    clients = Client.objects.all()
    total_balance = clients.aggregate(total=Sum('balance'))['total'] or 0
    logger.debug(
        f"User {request.user.username} (is_superuser={request.user.is_superuser}, "
        f"is_staff={request.user.is_staff}) accessed dashboard"
    )

    user = request.user
    if user.is_superuser:
        logger.debug("Superuser redirected to admin")
        return redirect('/admin/')

    # Проверка наличия организации
    if not user.organization:
        logger.debug(f"User {user.username} has no organization")
        return render(
            request,
            'core/no_organization.html',
            {'message': 'Вам нужно обратиться к администратору для назначения организации.'}
        )

    org = user.organization
    search_query = request.GET.get('search', '')
    clients = Client.objects.filter(organization=org)
    if search_query:
        clients = clients.filter(Q(name__icontains=search_query) | Q(phone__icontains=search_query))

    today = datetime.now()
    month_start = today - relativedelta(months=1)
    spent = abs(
        BonusHistory.objects.filter(
            client__organization=org,
            date__gte=month_start,
            amount__lt=0
        ).aggregate(total=Sum('amount'))['total'] or 0
    )

    add_form = AddClientForm()
    bonus_form = BonusForm()
    template, _ = MessageTemplate.objects.get_or_create(user=user)
    template_form = TemplateForm(instance=template)

    # Извлечение данных WhatsApp из сессии
    wa_url = request.session.pop('wa_url', None)
    wa_message = request.session.pop('wa_message', None)

    if request.method == 'POST':
        logger.debug(f"POST request received: {request.POST}")

        # Добавление клиента
        if 'add_client' in request.POST:
            add_form = AddClientForm(request.POST)
            if add_form.is_valid():
                client = add_form.save(commit=False)
                client.organization = org
                client.phone = (
                    client.phone.replace(' ', '')
                    .replace('(', '')
                    .replace(')', '')
                    .replace('-', '')
                )

                if not client.phone.startswith('+7'):
                    client.phone = '+7' + client.phone

                if len(client.phone) != 12:
                    add_form.add_error('phone', 'Номер телефона должен быть в формате +7XXXXXXXXXX')
                    context = {
                        'clients': clients, 'add_form': add_form, 'bonus_form': BonusForm(),
                        'template_form': template_form, 'spent': spent, 'business_name': org.name,
                        'search_query': search_query,
                    }
                    return render(request, 'core/dashboard.html', context)

                # ✅ Проверка на дубликат
                existing_client = Client.objects.filter(phone=client.phone, organization=org).first()
                if existing_client:
                    add_form.add_error(
                        'phone',
                        f'Клиент с номером {client.phone} уже существует. '
                        f'Добавьте бонус этому клиенту.'
                    )
                    context = {
                        'clients': clients, 'add_form': add_form, 'bonus_form': BonusForm(),
                        'template_form': template_form, 'spent': spent, 'business_name': org.name,
                        'search_query': search_query,
                    }
                    return render(request, 'core/dashboard.html', context)

                # Сохраняем клиента
                client.save()
                logger.debug(f"Client {client.name} created with phone {client.phone}")

                template, _ = MessageTemplate.objects.get_or_create(user=user)
                message = template.accrual_template.replace('[имя]', client.name).replace(
                    '[сумма]', str(client.balance)
                ).replace('[баланс]', str(client.balance))

                encoded_message = urllib.parse.quote(message)
                wa_url = f"https://wa.me/{client.phone[1:]}?text={encoded_message}"

                # Сохраняем данные в сессии
                request.session['wa_url'] = wa_url
                request.session['wa_message'] = message
                return redirect('dashboard')

            else:
                context = {
                    'clients': clients, 'add_form': add_form, 'bonus_form': bonus_form,
                    'template_form': template_form, 'spent': spent, 'business_name': org.name,
                    'search_query': search_query, 'total_balance': total_balance,
                }
                return render(request, 'core/dashboard.html', context)

        # Добавление бонуса
        elif 'add_bonus' in request.POST:
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, id=client_id, organization=org)
            bonus_form = BonusForm(request.POST)
            if bonus_form.is_valid():
                amount = bonus_form.cleaned_data['amount']
                typ = bonus_form.cleaned_data['type']
                if typ == 'deduction':
                    amount = -amount

                old_balance = client.balance
                client.balance += amount
                client.save()

                desc = 'Начисление' if amount > 0 else 'Списание'
                BonusHistory.objects.create(
                    client=client, amount=amount, description=desc, balance_after=client.balance
                )

                logger.debug(f"Bonus {amount} applied to client {client.name}")

                template = MessageTemplate.objects.get(user=user)
                if amount > 0:
                    msg_template = template.accrual_template
                    sum_str = str(amount)
                else:
                    msg_template = template.deduction_template
                    sum_str = str(-amount)

                message = msg_template.replace('[имя]', client.name).replace(
                    '[сумма]', sum_str
                ).replace('[баланс]', str(client.balance))

                encoded_message = urllib.parse.quote(message)
                wa_url = f"https://wa.me/{client.phone[1:]}?text={encoded_message}"

                request.session['wa_url'] = wa_url
                request.session['wa_message'] = message
                return redirect('dashboard')

            else:
                context = {
                    'clients': clients, 'add_form': add_form, 'bonus_form': bonus_form,
                    'template_form': template_form, 'spent': spent, 'business_name': org.name,
                    'search_query': search_query,
                }
                return render(request, 'core/dashboard.html', context)

        # Обнуление баланса
        elif 'reset_balance' in request.POST:
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, id=client_id, organization=org)
            old_balance = client.balance
            client.balance = 0
            client.save()

            BonusHistory.objects.create(
                client=client, amount=-old_balance, description='Обнуление', balance_after=0
            )

            logger.debug(f"Balance reset for client {client.name}")

            template = MessageTemplate.objects.get(user=user)
            message = template.reset_template.replace('[имя]', client.name).replace('[баланс]', '0')

            encoded_message = urllib.parse.quote(message)
            wa_url = f"https://wa.me/{client.phone[1:]}?text={encoded_message}"

            request.session['wa_url'] = wa_url
            request.session['wa_message'] = message
            return redirect('dashboard')

        # Удаление клиента
        elif 'delete_client' in request.POST:
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, id=client_id, organization=org)
            client.delete()
            logger.debug(f"Client {client.name} deleted")
            return redirect('dashboard')

        # Редактирование шаблонов
        elif 'edit_templates' in request.POST:
            template, _ = MessageTemplate.objects.get_or_create(user=user)
            template_form = TemplateForm(request.POST, instance=template)
            if template_form.is_valid():
                template_form.save()
                logger.debug(f"Templates updated for user {user.username}")
                return redirect('dashboard')
            else:
                context = {
                    'clients': clients, 'add_form': add_form, 'bonus_form': bonus_form,
                    'template_form': template_form, 'spent': spent, 'business_name': org.name,
                    'search_query': search_query,
                }
                return render(request, 'core/dashboard.html', context)

    # Контекст по умолчанию
    context = {
        'clients': clients, 'add_form': add_form, 'bonus_form': bonus_form,
        'template_form': template_form, 'spent': spent, 'business_name': org.name,
        'search_query': search_query, 'wa_url': wa_url, 'wa_message': wa_message,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def history(request, client_id):
    logger.debug(
        f"User {request.user.username} (is_superuser={request.user.is_superuser}, "
        f"is_staff={request.user.is_staff}) accessed history for client_id {client_id}"
    )

    if request.user.is_superuser:
        logger.debug("Superuser redirected to admin from history view")
        return redirect('/admin/')

    org = request.user.organization
    if not org:
        logger.debug(f"User {request.user.username} has no organization in history view")
        return render(
            request,
            'core/no_organization.html',
            {'message': 'Вам нужно обратиться к администратору для назначения организации.'}
        )

    client = get_object_or_404(Client, id=client_id, organization=org)
    history = client.history.all().order_by('-date')
    return render(request, 'core/history.html', {'history': history, 'client': client})


def logout_view(request):
    logout(request)
    return redirect('register')


def register(request):
    return render(request, 'register.html')
