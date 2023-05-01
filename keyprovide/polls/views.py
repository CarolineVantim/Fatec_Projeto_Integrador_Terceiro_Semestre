from polls.erps_connections.good_after.libs.good_after_class import SiteGoodAfter
from polls.erps_connections.ndays.libs.ndays_class import SiteNDays
from django.shortcuts import render, redirect, HttpResponseRedirect
from storage_non_sequential.storage import MongoConnect
from django.contrib.auth.models import User, auth
from polls.models import MarketPlaceProducts
from django.contrib import messages
from .models import DonationList
from polls.forms import UserForm
from unidecode import unidecode
#from polls.models import User



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
    user_form = UserForm(request.POST)
    context = {'user_form': user_form}
    if user_form.is_valid():
        print(user_form.clean_password())
        if request.method == 'POST':
            if user_form.clean_password() == user_form.clean_confirm_password():
                if User.objects.filter(username=user_form.clean_username()).exists():
                    messages.info(request, 'Este usuário não está disponível.')
                    return redirect('registration')
                elif User.objects.filter(email=user_form.clean_email()).exists():
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
            return render(request, 'registration.html')
    else:
        return render(request, 'registration.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
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
    return render(request, "index.html", {"all_results": search_ndays.all_occurrences})

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

def add_product_list(request, user_id, reference):
    pass


def index_donations(request):
	list = DonationList.objects.order_by("id")

	form = DonationList()

	context ={"list":list, "form": form}
	
	return render (request, "shopping_list/index.html", context)


def completeItem(request, user_id: int, item_id: int):
	item = DonationList.objects.get(pk=item_id)
	item.complete = True
	item.save()

	return (redirect('index'))


def deleteItem(request, user_id:int, item_id: int):
	item = DonationList.objects.get(pk=item_id)
	item.delete()
	return redirect('index')

def deleteAll(request):
	DonationList.objects.all().delete()
	return redirect('index')
