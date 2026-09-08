from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
import pandas as pd

# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.error(request, 'Please correct the errors indicated below.')
            print("Invalid form:", form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return redirect('FindRecipe')
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return redirect('FindRecipe')


def ChangePassword(request):
    if 'loginid' not in request.session:
        return redirect('UserLogin')

    if request.method == 'POST':
        loginid = request.session['loginid']
        old_pswd = request.POST.get('old_password')
        new_pswd = request.POST.get('new_password')
        confirm_pswd = request.POST.get('confirm_password')

        try:
            user = UserRegistrationModel.objects.get(loginid=loginid)
            if user.password != old_pswd:
                messages.error(request, 'Current password does not match.')
            elif new_pswd != confirm_pswd:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pswd) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                user.password = new_pswd
                user.save()
                messages.success(request, 'Password updated successfully!')
        except Exception as e:
            messages.error(request, 'Failed to update password: ' + str(e))

        referer = request.META.get('HTTP_REFERER')
        if referer and 'ChangePassword' not in referer:
            return redirect(referer)
        return redirect('FindRecipe')

    return render(request, 'users/ChangePassword.html')

NON_VEG_TERMS = {
    'chicken', 'mutton', 'beef', 'pork', 'lamb', 'meat', 'veal', 'ham', 'bacon',
    'prosciutto', 'salami', 'pepperoni', 'sausage', 'hot dog', 'frankfurter',
    'fish', 'salmon', 'tuna', 'cod', 'halibut', 'tilapia', 'trout', 'anchov',
    'shrimp', 'prawn', 'crab', 'lobster', 'calamari', 'squid', 'octopus', 'clam',
    'mussel', 'oyster', 'scallop', 'seafood', 'poultry', 'duck', 'turkey', 'goose',
    'egg', 'eggs', 'gelatin', 'lard', 'bone broth', 'beef broth', 'chicken broth',
    'fish sauce', 'anchovy', 'ribs', 'steak'
}

UNHEALTHY_TERMS = {
    'cupcake', 'cake', 'donut', 'doughnut', 'cookie', 'scone', 'fudge', 'candy',
    'crispy treat', 'pie', 'pastry', 'brownie', 'deep fried', 'fries', 'frosting',
    'marshmallow', 'sundae', 'caramel', 'syrup', 'fried'
}

HEALTHY_TERMS = {
    'salad', 'soup', 'steamed', 'boiled', 'oatmeal', 'oats', 'quinoa', 'lentil',
    'dal', 'sprouts', 'smoothie', 'idli', 'roasted', 'spinach', 'greens',
    'broccoli', 'avocado', 'vegetable', 'chia', 'fruit'
}


def FindRecipe(request):
    if request.method == 'POST':
        from django.conf import settings
        import requests
        import urllib.parse
        from django.contrib import messages
        
        url = 'https://api.spoonacular.com/recipes/'
        apiKey = settings.API_KEY
        
        Ingredients_raw = request.POST.get('ingredients', '').strip()
        Ingredients = Ingredients_raw.replace(',', ',+')
        
        # Request multiple recipes (up to 9) prepared with the ingredient(s)
        query = url + 'findByIngredients' + '?' + 'apiKey=' + apiKey + '&ingredients=' + Ingredients + '&number=9'
        try:
            response = requests.get(query, timeout=10)
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Fetch bulk info for vegetarian, health score, and aggregate likes
                recipe_ids = [str(item['id']) for item in data if item.get('id')]
                bulk_info_map = {}
                if recipe_ids:
                    try:
                        bulk_query = f"{url}informationBulk?apiKey={apiKey}&ids={','.join(recipe_ids)}"
                        bulk_resp = requests.get(bulk_query, timeout=10)
                        bulk_data = bulk_resp.json()
                        if isinstance(bulk_data, list):
                            for b_item in bulk_data:
                                if isinstance(b_item, dict) and b_item.get('id'):
                                    bulk_info_map[b_item['id']] = b_item
                    except Exception:
                        pass
                
                recipes_list = []
                for item in data:
                    title = item.get('title', '')
                    image = item.get('image', '')
                    recipe_id = item.get('id', '')
                    b_info = bulk_info_map.get(recipe_id, {})
                    
                    # Popularity likes
                    likes = b_info.get('aggregateLikes') if b_info.get('aggregateLikes') is not None else item.get('likes', 0)
                    try:
                        likes = int(likes)
                    except (ValueError, TypeError):
                        likes = 0
                    
                    # Generate YouTube search URLs for Telugu and English recipe videos
                    q_telugu = urllib.parse.quote_plus(f"{title} recipe in telugu")
                    q_english = urllib.parse.quote_plus(f"{title} recipe in english")
                    yt_telugu = f"https://www.youtube.com/results?search_query={q_telugu}"
                    yt_english = f"https://www.youtube.com/results?search_query={q_english}"
                    
                    used_ings = [ing.get('name', '') for ing in item.get('usedIngredients', []) if ing.get('name')]
                    missed_ings = [ing.get('name', '') for ing in item.get('missedIngredients', []) if ing.get('name')]
                    all_ings_text = ' '.join(used_ings + missed_ings).lower()
                    title_lower = title.lower()
                    full_text = f"{title_lower} {all_ings_text}"
                    
                    # 1. Veg vs Non-Veg Classification
                    has_non_veg = any(term in full_text for term in NON_VEG_TERMS)
                    if has_non_veg:
                        is_veg = False
                    elif b_info.get('vegetarian') is not None:
                        is_veg = bool(b_info.get('vegetarian'))
                    else:
                        is_veg = True
                    
                    # 2. Healthy vs Not Healthy Classification
                    health_score = b_info.get('healthScore', 0) or 0
                    try:
                        health_score = float(health_score)
                    except (ValueError, TypeError):
                        health_score = 0
                    very_healthy = bool(b_info.get('veryHealthy', False))
                    is_unhealthy_kw = any(term in title_lower for term in UNHEALTHY_TERMS)
                    is_healthy_kw = any(term in full_text for term in HEALTHY_TERMS)
                    
                    if is_unhealthy_kw:
                        is_healthy = False
                    elif very_healthy or health_score >= 20:
                        is_healthy = True
                    elif is_healthy_kw:
                        is_healthy = True
                    elif health_score >= 10:
                        is_healthy = True
                    else:
                        is_healthy = False
                    
                    recipes_list.append({
                        'id': recipe_id,
                        'title': title,
                        'image': image,
                        'youtube_telugu': yt_telugu,
                        'youtube_english': yt_english,
                        'used_ingredients': used_ings,
                        'missed_ingredients': missed_ings,
                        'likes': likes,
                        'is_veg': is_veg,
                        'is_healthy': is_healthy,
                        'health_score': health_score,
                    })
                
                # Sort popular dishes to the top (descending order of likes)
                recipes_list.sort(key=lambda x: x.get('likes', 0), reverse=True)
                
                # Flag popular dishes
                for idx, r in enumerate(recipes_list):
                    if idx < 3 and r.get('likes', 0) > 0:
                        r['is_popular'] = True
                    else:
                        r['is_popular'] = False
                
                return render(request, 'users/findrecipe.html', {
                    'recipes': recipes_list,
                    'title': recipes_list[0]['title'] if recipes_list else '',
                    'image': recipes_list[0]['image'] if recipes_list else '',
                    'ingredients': Ingredients_raw
                })
            else:
                messages.error(request, 'No recipes found for the entered ingredients.')
                return render(request, 'users/findrecipe.html', {'ingredients': Ingredients_raw})
        except Exception as e:
            messages.error(request, 'Error fetching recipes: ' + str(e))
            return render(request, 'users/findrecipe.html', {'ingredients': Ingredients_raw})
    else:
        return render(request, 'users/findrecipe.html')
    
    
def Nutrition(request):
    if request.method == 'POST':
        from django.conf import settings
        import requests
        import pandas as pd
        from django.contrib import messages
        
        url = 'https://api.spoonacular.com/recipes/'
        apiKey = settings.API_KEY
        
        Ingredients_raw = request.POST.get('ingredients', '').strip()
        Ingredients = Ingredients_raw.replace(',', ',+')
        
        Ingredient_query = url + 'findByIngredients' + '?' + 'apiKey=' + apiKey + '&ingredients=' + Ingredients + '&number=1'
        try:
            Ingredient_response = requests.get(Ingredient_query)
            dict_Ingredient_response = Ingredient_response.json()
            if isinstance(dict_Ingredient_response, list) and len(dict_Ingredient_response) > 0:
                id = dict_Ingredient_response[0]['id']
                nutrition_query = url + str(id) + '/nutritionWidget.json?apiKey=' + apiKey
                nutrition_response = requests.get(nutrition_query)
                dict_nutrition_response = nutrition_response.json()
                bad_nutrients = dict_nutrition_response.get('bad', [])
                good_nutrients = dict_nutrition_response.get('good', [])
                
                bad_keys = [n['title'] for n in bad_nutrients]
                bad_values = [n['amount'] for n in bad_nutrients]
                good_keys = [n['title'] for n in good_nutrients]
                good_values = [n['amount'] for n in good_nutrients]
                
                bad_nutrient_df = pd.DataFrame.from_dict({'Nutrient': bad_keys, 'amount': bad_values})
                bad_nutrient_html = bad_nutrient_df.to_html()
                good_nutrient_df = pd.DataFrame.from_dict({'Nutrient': good_keys, 'amount': good_values})
                good_nutrient_html = good_nutrient_df.to_html()
                
                return render(request, 'users/Nutrition.html', {
                    'bad_nutrient_html': bad_nutrient_html,
                    'good_nutrient_html': good_nutrient_html,
                    'ingredients': Ingredients_raw
                })
            else:
                messages.error(request, 'No nutrition profile found for the entered ingredients.')
                return render(request, 'users/Nutrition.html', {'ingredients': Ingredients_raw})
        except Exception as e:
            messages.error(request, 'Error fetching nutrition: ' + str(e))
            return render(request, 'users/Nutrition.html', {'ingredients': Ingredients_raw})
    else:
        return render(request, 'users/Nutrition.html')
    