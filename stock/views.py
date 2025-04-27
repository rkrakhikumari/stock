from django.shortcuts import render
from .forms import StockSearchForm
import requests

import yfinance as yf
from .models import SearchHistory  # Import the SearchHistory model
from django.http import JsonResponse


def stock_search(request):
    chart = None
    yesterday_price = None
    today_price = None
    profit_loss = None
    company_name = None
    stock_symbol = None

    # Fetch or create the SearchHistory entry
    search_history, created = SearchHistory.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = StockSearchForm(request.POST)
        if form.is_valid():
            stock_symbol = form.cleaned_data['stock_name']

            # Increment the search count globally
            search_history.search_count += 1
            search_history.save()

            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period="7d")

            if not hist.empty:
                yesterday_price = round(hist['Close'].iloc[-2], 2)
                today_price = round(hist['Close'].iloc[-1], 2)
                profit_loss = round(today_price - yesterday_price, 2)

                labels = hist.index.strftime('%d/%m/%Y').tolist()
                data = [round(price, 2) for price in hist['Close'].tolist()]
                chart = {
                    'labels': labels,
                    'data': data,
                }

                # Fetch company name dynamically
                try:
                    stock_info = stock.info
                    company_name = stock_info.get('longName', 'Unknown Company')
                except Exception:
                    company_name = 'Unknown Company'

    else:
        form = StockSearchForm()

    return render(request, 'stock_search.html', {
        'form': form,
        'chart': chart,
        'yesterday_price': yesterday_price,
        'today_price': today_price,
        'profit_loss': profit_loss,
        'company_name': company_name,
        'stock_symbol': stock_symbol,
        'search_count': search_history.search_count,  # Pass the search count to the template
    })


def autocomplete(request):
    term = request.GET.get('term', '')
    if not term:
        return JsonResponse([], safe=False)  # Return an empty list if no query

    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={term}"

    try:
        response = requests.get(url)
        data = response.json()

        # Extract stock symbols (or company names if required)
        suggestions = [result['symbol'] for result in data.get('quotes', []) if 'symbol' in result]
        
        return JsonResponse(suggestions, safe=False)  # Return the list of suggestions
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return JsonResponse([], safe=False)