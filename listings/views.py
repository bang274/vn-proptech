import google.generativeai as genai
from django.shortcuts import render, get_object_or_404, redirect # <--- Add 'redirect'
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from .models import Property, Inquiry
import os # Make sure this is imported
# NOTE: In a real app, put the key in settings.py or .env
# For now, we will initialize the client inside the function for speed.

def property_list(request):
    # (Your existing code is here, don't touch it)
    properties = Property.objects.all()
    return render(request, 'listings/index.html', {'properties': properties})

# ADD THIS NEW FUNCTION
def property_detail(request, pk):
    # Try to get the property with this ID. If it doesn't exist, give a 404 error.
    prop = get_object_or_404(Property, pk=pk)
    
    return render(request, 'listings/detail.html', {'prop': prop})

def generate_pitch(request, pk):
    # 1. Get the house
    prop = get_object_or_404(Property, pk=pk)
    
    # 2. Configure Gemini
    # Go to https://aistudio.google.com/app/apikey to get your key

    api_key = os.environ.get("GEMINI_API_KEY") # <--- Safe and clean
    genai.configure(api_key=api_key)
    
    # 3. Initialize the Model
    # We use 'gemini-1.5-flash' because it is fast and cheap (perfect for simple tasks)
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
    
    # 4. Construct the Prompt (Same strategy as before)
    prompt_text = f"""
    Act as a top-tier Vietnamese real estate agent.
    Write a catchy, professional sales listing for this house:
    
    - Title: {prop.title}
    - Location: {prop.location_district}
    - Price: {prop.price_in_billions} Billion VND
    - Area: {prop.area_sqm} sqm
    - Alley Width: {prop.alley_width_meters} meters
    - Legal Status: {'Red Book Ready' if prop.is_legal_clear else 'Processing'}
    
    Tone: Enthusiastic. If the alley is small (< 2.5m), focus on "privacy" and "quiet location" rather than accessibility.
    Include 2-3 Vietnamese terms like "Siêu phẩm", "Chính chủ", or "Đầu tư F0".
    """

    # 5. Call the Intelligence
    try:
        response = model.generate_content(prompt_text)
        
        # 6. Extract and Save
        generated_text = response.text
        prop.ai_description = generated_text
        prop.save()
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")

    # 7. Return to page
    return redirect('property_detail', pk=pk)

def property_list(request):
    # 1. Start with ALL properties
    properties = Property.objects.order_by('-price_in_billions') # Make sure you order them or pagination breaks
    
    # 2. Capture the inputs so we can keep them in the search bar after refresh
    # (This prevents the form from clearing itself)
    values = {
        'q': request.GET.get('q', ''),
        'district': request.GET.get('district', ''),
        'price': request.GET.get('price', '')
    }

    # 3. Filter: Keywords
    if values['q']:
        properties = properties.filter(title__icontains=values['q'])

    # 4. Filter: District (Exact Match)
    if values['district']:
        properties = properties.filter(location_district__icontains=values['district'])

    # 5. Filter: Price (Less Than or Equal To)
    if values['price']:
        properties = properties.filter(price_in_billions__lte=values['price'])

    # 6. Return context
    context = {
        'properties': properties,
        'values': values # Pass this back so the HTML knows what we typed
    }
    
    return render(request, 'listings/index.html', context)

def inquiry(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        name = request.POST['name']
        phone = request.POST['phone']
        message = request.POST['message']
        
        listing = get_object_or_404(Property, pk=listing_id)
        
        # Save to Database
        lead = Inquiry(listing=listing, name=name, phone=phone, message=message)
        lead.save()
        
        # Send Feedback to User (Optional but nice)
        # We need to configure messages in template to see this, but logic acts here.
        
        return redirect('property_detail', pk=listing_id)
    
@login_required(login_url='/admin/') # Only logged-in users (YOU) can see this
def dashboard(request):
    # 1. Fetch Data
    properties = Property.objects.all()
    inquiries = Inquiry.objects.order_by('-contact_date') # Newest leads first
    
    # 2. Calculate Inventory Value (Total Billions)
    total_inventory_value = properties.aggregate(Sum('price_in_billions'))['price_in_billions__sum'] or 0
    
    # 3. Calculate "The Bag" (Potential Commission)
    # Market Rule: 2% Commission is standard in VN.
    # Logic: Total Value * 0.02 * 1 Billion (to convert to VND currency, simplified here just to the number)
    potential_commission = float(total_inventory_value) * 0.02 
    
    # 4. Context for the template
    context = {
        'properties': properties,
        'inquiries': inquiries,
        'total_houses': properties.count(),
        'total_leads': inquiries.count(),
        'inventory_value': round(total_inventory_value, 2),
        'potential_commission': round(potential_commission, 2),
    }
    
    return render(request, 'listings/dashboard.html', context)