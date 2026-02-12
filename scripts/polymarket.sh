#!/bin/bash
# Polymarket Gamma API Wrapper - Read-Only Mode
# No API key, no authentication, no wallet required
# Docs: https://docs.polymarket.com/quickstart/fetching-data

BASE_URL="https://gamma-api.polymarket.com"
CLOB_URL="https://clob.polymarket.com"

show_help() {
    cat << EOF
Polymarket Read-Only CLI

Usage: $0 <command> [options]

Commands:
    events [limit]          List active events (default: 10)
    event <slug>            Get specific event details
    markets [limit]         List active markets
    market <slug>           Get specific market details
    tags [limit]            List all categories/tags
    price <token_id>        Get current price for token
    book <token_id>         Get orderbook depth
    sports                  List sports leagues
    search <query>          Search markets by keyword
    
Examples:
    $0 events 20
    $0 market will-bitcoin-reach-100k-by-2025
    $0 tags
    $0 search "Trump"
EOF
}

fetch_events() {
    local limit=${1:-10}
    curl -s "$BASE_URL/events?active=true&closed=false&limit=$limit" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for i, event in enumerate(data[:$limit], 1):
        market = event.get('markets', [{}])[0]
        outcomes = market.get('outcomes', '[]')
        prices = market.get('outcomePrices', '[]')
        cat = event.get('tags', [{}])[0].get('label', 'N/A')
        print(f\"{i}. {event.get('title', 'N/A')}\")
        print(f\"   Slug: {event.get('slug', 'N/A')}\")
        print(f\"   Category: {cat}\")
        if outcomes != '[]' and prices != '[]':
            import ast
            try:
                out = ast.literal_eval(outcomes)
                pr = ast.literal_eval(prices)
                for o, p in zip(out, pr):
                    print(f\"   • {o}: {float(p)*100:.1f}%\")
            except:
                pass
        print()
except Exception as e:
    print(f'Error: {e}')
"
}

fetch_event() {
    local slug="$1"
    if [ -z "$slug" ]; then
        echo "Usage: $0 event <slug>"
        exit 1
    fi
    curl -s "$BASE_URL/events?slug=$slug" | python3 -m json.tool 2>/dev/null || echo "Event not found"
}

fetch_markets() {
    local limit=${1:-10}
    curl -s "$BASE_URL/markets?active=true&closed=false&limit=$limit" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, dict) and 'markets' in data:
        data = data['markets']
    for i, m in enumerate(data[:$limit], 1):
        print(f\"{i}. {m.get('question', 'N/A')}\")
        print(f\"   Slug: {m.get('slug', 'N/A')}\")
        print(f\"   Volume: ${m.get('volume', 'N/A')}\")
        print()
except Exception as e:
    print(f'Error: {e}')
"
}

fetch_market() {
    local slug="$1"
    if [ -z "$slug" ]; then
        echo "Usage: $0 market <slug>"
        exit 1
    fi
    curl -s "$BASE_URL/markets?slug=$slug" | python3 -m json.tool 2>/dev/null || echo "Market not found"
}

fetch_tags() {
    local limit=${1:-20}
    curl -s "$BASE_URL/tags?limit=$limit" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('Available Categories:')
    for tag in data[:$limit]:
        print(f\"  • {tag.get('label', 'N/A')} (slug: {tag.get('slug', 'N/A')})\")
except Exception as e:
    print(f'Error: {e}')
"
}

fetch_price() {
    local token_id="$1"
    if [ -z "$token_id" ]; then
        echo "Usage: $0 price <token_id>"
        exit 1
    fi
    curl -s "$CLOB_URL/price?token_id=$token_id&side=buy" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    price = data.get('price', 'N/A')
    if price != 'N/A':
        print(f'Current price: {float(price)*100:.2f}% ({price})')
    else:
        print('Price not available')
except Exception as e:
    print(f'Error: {e}')
"
}

fetch_book() {
    local token_id="$1"
    if [ -z "$token_id" ]; then
        echo "Usage: $0 book <token_id>"
        exit 1
    fi
    curl -s "$CLOB_URL/book?token_id=$token_id" | python3 -m json.tool 2>/dev/null || echo "Orderbook not available"
}

fetch_sports() {
    curl -s "$BASE_URL/sports" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('Sports Leagues:')
    for sport in data:
        print(f\"  • {sport.get('name', 'N/A')} (ID: {sport.get('series_id', 'N/A')})\")
except Exception as e:
    print(f'Error: {e}')
"
}

search_markets() {
    local query="$1"
    if [ -z "$query" ]; then
        echo "Usage: $0 search <query>"
        exit 1
    fi
    curl -s "$BASE_URL/events?active=true&closed=false&limit=50" | python3 -c "
import sys, json, re
query = '$query'.lower()
try:
    data = json.load(sys.stdin)
    matches = [e for e in data if query in e.get('title', '').lower()]
    print(f'Found {len(matches)} matches for \"$query\":')
    print()
    for event in matches[:10]:
        print(f\"• {event.get('title', 'N/A')}\")
        print(f\"  Slug: {event.get('slug', 'N/A')}\")
        print()
except Exception as e:
    print(f'Error: {e}')
"
}

case "$1" in
    events)
        fetch_events "$2"
        ;;
    event)
        fetch_event "$2"
        ;;
    markets)
        fetch_markets "$2"
        ;;
    market)
        fetch_market "$2"
        ;;
    tags)
        fetch_tags "$2"
        ;;
    price)
        fetch_price "$2"
        ;;
    book)
        fetch_book "$2"
        ;;
    sports)
        fetch_sports
        ;;
    search)
        search_markets "$2"
        ;;
    *)
        show_help
        ;;
esac
