from polls.erps_connections.good_after.libs.good_after_class import SiteGoodAfter
from polls.erps_connections.openai.connection_class import GenerateAttributesText
from polls.erps_connections.ndays.libs.ndays_class import SiteNDays
from django.shortcuts import render, redirect, HttpResponseRedirect
from storage_non_sequential.storage import MongoConnect
from django.contrib.auth.models import auth
from polls.models import MarketPlaceProducts
from .models import DonationListControl
from django.contrib import messages
from .models import DonationList
from .models import User
from .forms import UserForm



def build_product_occurrence(iterable_object: dict or object) -> None:
    temp_list = list()
    for key in iterable_object:
        prop = type(key) is dict
        object_key = {
            'meta_keywords': key['meta_keywords'] if prop else key.meta_keywords,
            'name': key['name'] if prop else key.name,
            'description': key['description'] if prop else key.description,
            'category': key['category'] if prop else key.category,
            'attributes': key['attributes'] if prop else key.attributes,
            'image': key['image'] if prop else key.image,
            'reference': key['reference'] if prop else key.reference,
            'product_link': key['product_link'] if prop else key.product_link,
            'expired_date': key['expired_date'] if prop else key.expired_date,
            'updated_at': key['updated_at'] if prop else key.updated_at,
        }
        temp_list.append(object_key)
    return temp_list

def checking_marketplace_occurrences(term: str, marketplace: str):
    all_possible_key = list()
    occurrences = MarketPlaceProducts.objects.all()
    if marketplace.lower() == 'all':
        if term.isdigit() and len(term) > 8:
            possible_key = occurrences.filter(reference=term)
            if len(possible_key) > 0:
                return possible_key
        else:
            temp_term = term.strip().lower()
            possible_key = occurrences.filter(reference=term)
            if len(possible_key) > 0:
                return possible_key 
            possible_key_1 = list(occurrences.filter(meta_keywords__contains=term))
            possible_key_2 = list(occurrences.filter(name__contains=temp_term))
            possible_key_3 = list(occurrences.filter(name__contains=term))
            for key in possible_key_1 + possible_key_2 + possible_key_3:
                if key not in possible_key:
                    all_possible_key.append(key)
    else:
        if term.isdigit() and len(term) > 8:
            possible_key = occurrences.filter(reference=term, marketplace=marketplace)
            if len(possible_key) > 0:
                return possible_key
        else:
            temp_term = term.strip().lower()
            possible_key_1 = list(occurrences.filter(meta_keywords__contains=term, marketplace=marketplace))
            possible_key_2 = list(occurrences.filter(name__contains=temp_term, marketplace=marketplace))
            possible_key_3 = list(occurrences.filter(name__contains=term, marketplace=marketplace))
            for key in possible_key_1 + possible_key_2 + possible_key_3:
                if key not in possible_key:
                    possible_key.append(key)
    return all_possible_key

def saving_marketplace_occurrences(all_occurrences: list) -> None:
    occurrences = MarketPlaceProducts.objects.all()
    non_sequential = MongoConnect()
    for occurrence in all_occurrences:
        exists = occurrences.filter(reference=occurrence['reference'])
        if len(exists) > 0:
            continue
        model = MarketPlaceProducts(
            meta_keywords = str(occurrence['meta_keywords']),
            name = str(occurrence['name']),
            description = str(occurrence['description']),
            category = str(occurrence['category']),
            attributes = str(occurrence['attributes']),
            image = str(occurrence['image']),
            reference = str(occurrence['reference']),
            product_link = str(occurrence['product_link']),
            expired_date = str(occurrence['expired_date']),
            price_from = float(occurrence['price_from']),
            price_to = float(occurrence['price_to']),
            marketplace = str(occurrence['marketplace'])
        )
        model.save()
        occurrence['expired_date'] = str(occurrence['expired_date'])
        non_sequential.non_db_insert(occurrence)

def check_occurrence(term: str, marketplace: str) -> dict[str: str]:
    all_results = list()
    possible_key = checking_marketplace_occurrences(term, marketplace)
    if len(possible_key) > 0:
        all_results = build_product_occurrence(possible_key)
        return {"all_results": all_results}
    else:
        search_goodafter = SiteGoodAfter(term)
        search_goodafter.send_search_requisition()
        if search_goodafter.availiable:
            search_goodafter.extract_all_occurrences()
            saving_marketplace_occurrences(search_goodafter.all_occurrences)
            return {"all_results": search_goodafter.all_occurrences}
    return {"all_results": {}}

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        print(user_form.is_valid())
        print(user_form.cleaned_data)
        if user_form.is_valid():
            context = {'user_form': user_form}
            if user_form.clean_password() == user_form.clean_confirm_password():
                if User.objects.filter(email=user_form.clean_email()).exists():
                    messages.info(request, 'Este email não está disponível.')
                    return redirect('registration')
                else:
                    user_form.cleaned_data.pop('confirm_password')
                    user_registration = User.objects.create_user(**user_form.cleaned_data)
                    user_registration.save()
                    return redirect('login_user')
            else:
                messages.info(request, 'Senhas não coincidem.')
                return redirect('registration')
        else:
            context = {'user_form': user_form}
            return render(request, 'registration.html', context)
    else:
        model_user = {
            'email': str(),
            'name': str(),
            'password': str(),
            'confirm_password': str(),
            'name': str(),
            'cnpj': str(),
            'cep': str(),
            'number': str(),
            'block': str(),
            'city': str(),
            'state': str(),
            'is_juridic': bool(),
        }
        user_form = UserForm(model_user)
        context = {'user_form': user_form}
        return render(request, 'registration.html', context)

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Senha ou usuários inválido')
            return redirect('login_user')
    else:
        return render(request, 'login_user.html')

def index(request):
    search_ndays = SiteNDays()
    search_ndays.send_search_requisition()
    saving_marketplace_occurrences(search_ndays.all_occurrences)
    all_activated_lists = DonationListControl.objects.all()
    filted_list_ = all_activated_lists.filter(closed='False')
    need_donation_list = list()
    if len(filted_list_) > 0:
        all_products_occurrences = DonationList.objects.all()
        for activated_list in filted_list_:
            specific_list = all_products_occurrences.filter(list_control_id=activated_list.pk)
            corporation = User.objects.get(pk=activated_list.user_id)
            full_list_information = {
                'user_list_id': activated_list.id,
                'products_count': len(specific_list),
                'corporation': corporation.name
            }
            need_donation_list.append(full_list_information)
    return render(request, "index.html", {"all_results": search_ndays.all_occurrences,
                                        "need_donation": need_donation_list})

def home(request, term: str or None = None):
    term = request.GET.get('lookup')
    if term:
        possible_response = check_occurrence(term, 'All')
    else:
        possible_response = dict()
    return render(request, "home.html", possible_response)

def logout_user(request):
    auth.logout(request)
    return HttpResponseRedirect('home')

def productdetail(request, pk):
    term = request.GET.get('lookup')
    if term:
        request.path_info = '/polls/home'
        return HttpResponseRedirect(f'/polls/home?lookup={term}')
    product = MarketPlaceProducts.objects.get(reference=pk)
    product.description = product.description.replace('\/', '/')
    return render(request, 'product.html', {'product': product})

def learn_more(request):
    return render(request, 'learn_more.html')

def add_product_list(request, user_id, reference, quantaty: int or None = None):
    activated_list = DonationListControl.objects.all()
    filted_list_ = activated_list.filter(user_id=user_id, closed='False')
    if not len(filted_list_) > 0:
        filted_list_ = DonationListControl(
                user_id=user_id, closed='False')
        filted_list_.save()
        occurrences = DonationList(
            user_id=user_id,
            reference=reference,
            quantaty=quantaty if quantaty else 1,
            list_control_id=filted_list_.pk)
    else:
        occurrences = DonationList(
            user_id=user_id,
            reference=reference,
            quantaty=quantaty if quantaty else 1,
            list_control_id=filted_list_[0].pk)
    occurrences.save()
    product = MarketPlaceProducts.objects.get(reference=reference)
    product.description = product.description.replace('\/', '/')
    return render(request, 'product.html', {'product': product})

def index_donations(request, user_id: int):
    activated_list = DonationListControl.objects.all()
    filted_list_ = activated_list.filter(user_id=user_id, closed='False')
    unfilted_lists_ = activated_list.filter(user_id=user_id, closed='True')
    donation_list = DonationList.objects.all()
    deactivated_list = list()
    if len(unfilted_lists_) > 0:
        for unfilter_list in unfilted_lists_:
            unfilter_list_donations = donation_list.filter(list_control_id=unfilter_list.pk)
            deactivated_dict = {
                'control_id': unfilter_list.pk,
                'products_count': len(unfilter_list_donations)
            }
            deactivated_list.append(deactivated_dict)
    else:
        deactivated_list = [{
                'control_id': False,
                'products_count': str()
            }]
    if len(filted_list_) > 0:
        filter_list_donations = donation_list.filter(list_control_id=filted_list_[0].pk)
        products = list()
        for occurrence in filter_list_donations:
            occurrences_dicts = {
                'product_occurrence': MarketPlaceProducts.objects.get(reference=occurrence.reference),
                'donation_occurrence': occurrence,
            }
            control_id = occurrence.list_control_id
            products.append(occurrences_dicts)
        context = {"products": products,
                    "control_id": control_id,
                    "deactivated_list": deactivated_list,
                    "can_donate": True}
    else:
        occurrences_dicts = {
            'product_occurrence': 'Adicione itens para ativar uma lista',
            'donation_occurrence': False
                }
        context = {"products": [occurrences_dicts],
                    "control_id": 0,
                    "deactivated_list": deactivated_list,
                    "can_donate": False}
    return render(request, "shop_car.html", context)

def donate_product(request, pk: int, user_id: int):
    item = DonationList.objects.get(pk=pk)
    item.donated_by = user_id
    item.was_donated = True
    item.save()
    return index_donations(request, user_id)

def delete_item(request, user_id: int, reference: str):
    item = DonationList.objects.get(user_id=user_id, reference=reference)
    item.delete()
    return index_donations(request, user_id)

def know_about_product(request, reference: str):
    product = MarketPlaceProducts.objects.get(reference=reference)
    if product.persuasive_text:
        print('SIM')
        return render(request, 'about_product.html', {'product': product})
    else:
        object_ai = GenerateAttributesText(False)
        object_ai.extract_specific_data(str(), product.name)
        if len(object_ai.results) > 0:
            product.persuasive_text = object_ai.results
            product.save()
            return render(request, 'about_product.html', {'product': product})

def close_list(request, user_id: int, list_control_id: int):
    activated_list = DonationListControl.objects.get(pk=list_control_id)
    activated_list.closed = 'True'
    activated_list.save()
    return index_donations(request, user_id)

def specific_list(request, list_control_id: int, user_id: int) -> None:
    # activated_list = DonationListControl.objects.all()
    # filted_list_ = activated_list.filter(user_id=user_id, closed='False')
    # unfilted_lists_ = activated_list.filter(user_id=user_id, closed='True')
    donation_list = DonationList.objects.all()
    deactivated_list = list()
    unfilter_list_donations = donation_list.filter(list_control_id=list_control_id)
    products = list()
    for occurrence in unfilter_list_donations:
        occurrences_dicts = {
            'product_occurrence': MarketPlaceProducts.objects.get(reference=occurrence.reference),
            'donation_occurrence': occurrence,
        }
        control_id = occurrence.list_control_id
        user_id_list = occurrence.user_id
        products.append(occurrences_dicts)
    context = {
        "products": products,
        "control_id": control_id,
        "deactivated_list": deactivated_list,
        "can_donate": False if user_id_list == user_id else True
    }
    return render(request, "shop_car.html", context)


def list_institution(request):
    return render(request, "list_institution.html")
