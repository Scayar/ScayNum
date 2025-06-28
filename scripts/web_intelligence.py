# Imports
from googlesearch import search
import requests
import re
import json
import time
import random
from urllib.parse import urlparse, parse_qs
from colorama import Fore, Style, init
from tabulate import tabulate
from fpdf import FPDF
from jinja2 import Template
import datetime
import csv
import os
from collections import Counter
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

# Rotating User-Agents to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# Free proxy list (you can update this with working proxies)
FREE_PROXIES = [
    # Add working free proxies here if needed
    # "http://proxy1:port",
    # "http://proxy2:port",
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Web Search Report for {{ query }}</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; color: #222; }
        .container { background: #fff; max-width: 900px; margin: 40px auto; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px #ccc; }
        h1 { color: #4285f4; }
        .section { margin-top: 30px; }
        .search-engine { background: #4285f4; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .category { background: #34a853; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .threat { background: #ea4335; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .social { background: #fbbc04; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .contact { background: #9c27b0; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .summary { background: #4285f4; color: #fff; padding: 10px; border-radius: 8px; margin-top: 20px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .table th, .table td { border: 1px solid #eee; padding: 8px; text-align: left; }
        .table th { background: #f2f2f2; }
        .url { word-break: break-all; }
    </style>
</head>
<body>
<div class="container">
    <h1>Web Search Report for "{{ query }}"</h1>
    
    <div class="section">
        <h2>Search Summary</h2>
        <div class="summary">
            <b>Total Results:</b> {{ total_results }}<br>
            <b>Search Engines Used:</b> {{ search_engines }}<br>
            <b>Categories Found:</b> {{ categories_found }}<br>
            <b>Social Media Profiles:</b> {{ social_count }}<br>
            <b>Contact Information:</b> {{ contact_count }}<br>
            <b>Threat Indicators:</b> {{ threat_count }}
        </div>
    </div>

    <div class="section">
        <h2>Results by Category</h2>
        {% for category, urls in categorized_results.items() %}
        <div class="category">
            <h3>{{ category }} ({{ urls|length }} results)</h3>
            <ul>
            {% for url in urls %}
                <li class="url">{{ url }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>

    {% if social_media %}
    <div class="section">
        <h2>Social Media Profiles</h2>
        {% for platform, profiles in social_media.items() %}
        <div class="social">
            <h3>{{ platform }} ({{ profiles|length }} profiles)</h3>
            <ul>
            {% for profile in profiles %}
                <li class="url">{{ profile }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if contact_info %}
    <div class="section">
        <h2>Contact Information</h2>
        {% for contact_type, contacts in contact_info.items() %}
        <div class="contact">
            <h3>{{ contact_type }} ({{ contacts|length }} found)</h3>
            <ul>
            {% for contact in contacts %}
                <li>{{ contact }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if threat_indicators %}
    <div class="section">
        <h2>Threat Intelligence</h2>
        {% for threat_type, threats in threat_indicators.items() %}
        <div class="threat">
            <h3>{{ threat_type }} ({{ threats|length }} indicators)</h3>
            <ul>
            {% for threat in threats %}
                <li class="url">{{ threat }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section">
        <b>Report generated at:</b> {{ now }}
    </div>
</div>
</body>
</html>
'''

def filter_latin(text):
    if not text:
        return ''
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_user_folder(query):
    # Create folder with format "query_results"
    # Handle special characters separately to avoid f-string syntax error
    safe_query = query.replace(' ', '_').replace('/', '_').replace('\\', '_')
    folder_name = f"{safe_query}_results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def get_random_user_agent():
    """Get a random User-Agent to avoid detection"""
    return random.choice(USER_AGENTS)

def get_random_proxy():
    """Get a random proxy from the list (if available)"""
    if FREE_PROXIES:
        proxy = random.choice(FREE_PROXIES)
        return {
            "http": proxy,
            "https": proxy
        }
    return None

def smart_query_processing(query):
    """Process query to make it more search-friendly"""
    # Remove extra spaces and normalize
    query = ' '.join(query.split())
    
    # If query is already in quotes, keep it
    if query.startswith('"') and query.endswith('"'):
        return query
    
    # For short queries (1-2 words), add quotes for exact matching
    words = query.split()
    if len(words) <= 2:
        return f'"{query}"'
    
    # For longer queries, create multiple search variations
    return query

def create_search_variations(query):
    """Create multiple search variations for better results"""
    variations = []
    
    # Original query
    variations.append(query)
    
    # Exact phrase match (only if not already quoted)
    if not query.startswith('"'):
        variations.append(f'"{query}"')
    
    # Remove quotes if present and add site-specific searches
    clean_query = query.strip('"')
    variations.append(f'site:com {clean_query}')
    
    # Only add a few variations to avoid rate limiting
    if len(variations) < 4:
        variations.append(f'{clean_query} filetype:pdf')
    
    return variations

def filter_relevant_results(urls, query):
    """Filter results to show most relevant ones first"""
    query_lower = query.lower()
    query_words = query_lower.split()
    
    scored_results = []
    
    for url in urls:
        score = 0
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()
        
        # Exact domain match gets high score
        if any(word in domain for word in query_words):
            score += 100
        
        # URL contains query words
        for word in query_words:
            if word in url_lower:
                score += 10
        
        # Exact phrase match in URL
        if query_lower in url_lower:
            score += 50
        
        # Social media profiles get bonus
        if any(platform in domain for platform in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com']):
            score += 5
        
        # Government/educational sites get bonus
        if '.gov' in domain or '.edu' in domain:
            score += 3
        
        scored_results.append((url, score))
    
    # Sort by score (highest first)
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Return URLs in order of relevance
    return [url for url, score in scored_results]

def search_duckduckgo(query, max_results=20):
    """Search using DuckDuckGo (more reliable than Google)"""
    results = []
    
    try:
        print(Fore.YELLOW + f"  Searching DuckDuckGo for: '{query}'")
        
        # Use DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        proxies = get_random_proxy()
        
        response = requests.get(search_url, headers=headers, timeout=15, verify=False, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find result links
            result_links = soup.find_all('a', class_='result__a')
            for link in result_links:
                href = link.get('href')
                if href and href.startswith('http') and href not in results:
                    results.append(href)
                    if len(results) >= max_results:
                        break
            
            # If no results with class method, try alternative parsing
            if not results:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('http') and 'duckduckgo.com' not in href and href not in results:
                        results.append(href)
                        if len(results) >= max_results:
                            break
            
            print(Fore.GREEN + f"    ✅ Found {len(results)} results from DuckDuckGo")
        else:
            print(Fore.RED + f"    ❌ DuckDuckGo returned status code: {response.status_code}")
    
    except Exception as e:
        print(Fore.RED + f"    Error with DuckDuckGo search: {e}")
    
    return results

def search_bing(query, max_results=20):
    """Search using Bing (more reliable than Google)"""
    results = []
    
    try:
        print(Fore.YELLOW + f"  Searching Bing for: '{query}'")
        
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        proxies = get_random_proxy()
        
        response = requests.get(search_url, headers=headers, timeout=15, verify=False, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find Bing result links
            result_links = soup.find_all('a', href=True)
            for link in result_links:
                href = link['href']
                if href.startswith('http') and 'bing.com' not in href and href not in results:
                    results.append(href)
                    if len(results) >= max_results:
                        break
            
            print(Fore.GREEN + f"    ✅ Found {len(results)} results from Bing")
        else:
            print(Fore.RED + f"    ❌ Bing returned status code: {response.status_code}")
    
    except Exception as e:
        print(Fore.RED + f"    Error with Bing search: {e}")
    
    return results

def search_google_fallback(query, max_results=10):
    """Fallback Google search with better rate limiting"""
    results = []
    
    try:
        print(Fore.YELLOW + f"  Trying Google fallback for: '{query}'")
        
        # Use basic search approach
        from googlesearch import search
        
        search_results = search(query, num_results=max_results, lang="en")
        for result in search_results:
            if hasattr(result, 'url'):
                url = result.url
            else:
                url = str(result)
            
            if url.startswith('http') and url not in results:
                results.append(url)
                if len(results) >= max_results:
                    break
        
        print(Fore.GREEN + f"    ✅ Found {len(results)} results from Google fallback")
    
    except Exception as e:
        print(Fore.RED + f"    ❌ Google fallback failed: {e}")
    
    return results

def categorize_url(url):
    """Categorize URLs based on domain and content"""
    domain = urlparse(url).netloc.lower()
    
    # Social Media
    if any(platform in domain for platform in ['facebook.com', 'fb.com']):
        return 'Social Media - Facebook'
    elif any(platform in domain for platform in ['twitter.com', 'x.com']):
        return 'Social Media - Twitter/X'
    elif any(platform in domain for platform in ['instagram.com']):
        return 'Social Media - Instagram'
    elif any(platform in domain for platform in ['linkedin.com']):
        return 'Social Media - LinkedIn'
    elif any(platform in domain for platform in ['youtube.com', 'youtu.be']):
        return 'Social Media - YouTube'
    elif any(platform in domain for platform in ['tiktok.com']):
        return 'Social Media - TikTok'
    elif any(platform in domain for platform in ['reddit.com']):
        return 'Social Media - Reddit'
    elif any(platform in domain for platform in ['snapchat.com']):
        return 'Social Media - Snapchat'
    elif any(platform in domain for platform in ['telegram.org', 't.me']):
        return 'Social Media - Telegram'
    elif any(platform in domain for platform in ['discord.com', 'discord.gg']):
        return 'Social Media - Discord'
    
    # E-commerce
    elif any(platform in domain for platform in ['amazon.com', 'amazon.co.uk', 'amazon.de']):
        return 'E-commerce - Amazon'
    elif any(platform in domain for platform in ['ebay.com']):
        return 'E-commerce - eBay'
    elif any(platform in domain for platform in ['etsy.com']):
        return 'E-commerce - Etsy'
    
    # Professional
    elif any(platform in domain for platform in ['github.com']):
        return 'Professional - GitHub'
    elif any(platform in domain for platform in ['stackoverflow.com']):
        return 'Professional - Stack Overflow'
    elif any(platform in domain for platform in ['medium.com']):
        return 'Professional - Medium'
    
    # News/Media
    elif any(platform in domain for platform in ['news.', 'bbc.com', 'cnn.com', 'reuters.com']):
        return 'News & Media'
    
    # Government
    elif any(platform in domain for platform in ['.gov', '.mil']):
        return 'Government & Military'
    
    # Educational
    elif any(platform in domain for platform in ['.edu', '.ac.uk']):
        return 'Educational'
    
    # Technology
    elif any(platform in domain for platform in ['microsoft.com', 'apple.com', 'google.com', 'github.com']):
        return 'Technology'
    
    # Dark Web (potential)
    elif any(platform in domain for platform in ['.onion', 'tor2web']):
        return 'Dark Web - Potential'
    
    # Cryptocurrency
    elif any(platform in domain for platform in ['coinbase.com', 'binance.com', 'kraken.com']):
        return 'Cryptocurrency'
    
    # Gaming
    elif any(platform in domain for platform in ['steam.com', 'epicgames.com', 'roblox.com']):
        return 'Gaming'
    
    else:
        return 'General Web'

def extract_social_media(urls):
    """Extract social media profiles from URLs"""
    social_media = {}
    
    for url in urls:
        domain = urlparse(url).netloc.lower()
        
        if 'facebook.com' in domain or 'fb.com' in domain:
            if 'Facebook' not in social_media:
                social_media['Facebook'] = []
            social_media['Facebook'].append(url)
        elif 'twitter.com' in domain or 'x.com' in domain:
            if 'Twitter/X' not in social_media:
                social_media['Twitter/X'] = []
            social_media['Twitter/X'].append(url)
        elif 'instagram.com' in domain:
            if 'Instagram' not in social_media:
                social_media['Instagram'] = []
            social_media['Instagram'].append(url)
        elif 'linkedin.com' in domain:
            if 'LinkedIn' not in social_media:
                social_media['LinkedIn'] = []
            social_media['LinkedIn'].append(url)
        elif 'youtube.com' in domain or 'youtu.be' in domain:
            if 'YouTube' not in social_media:
                social_media['YouTube'] = []
            social_media['YouTube'].append(url)
        elif 'tiktok.com' in domain:
            if 'TikTok' not in social_media:
                social_media['TikTok'] = []
            social_media['TikTok'].append(url)
        elif 'reddit.com' in domain:
            if 'Reddit' not in social_media:
                social_media['Reddit'] = []
            social_media['Reddit'].append(url)
        elif 'telegram.org' in domain or 't.me' in domain:
            if 'Telegram' not in social_media:
                social_media['Telegram'] = []
            social_media['Telegram'].append(url)
        elif 'discord.com' in domain or 'discord.gg' in domain:
            if 'Discord' not in social_media:
                social_media['Discord'] = []
            social_media['Discord'].append(url)
        elif 'github.com' in domain:
            if 'GitHub' not in social_media:
                social_media['GitHub'] = []
            social_media['GitHub'].append(url)
    
    return social_media

def extract_contact_info(urls):
    """Extract potential contact information from URLs"""
    contact_info = {
        'Emails': [],
        'Phone Numbers': [],
        'Addresses': []
    }
    
    for url in urls:
        # Extract emails from URL
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', url)
        contact_info['Emails'].extend(emails)
        
        # Extract phone numbers from URL
        phones = re.findall(r'[\+]?[1-9][\d]{0,15}', url)
        contact_info['Phone Numbers'].extend(phones)
    
    # Remove duplicates
    for key in contact_info:
        contact_info[key] = list(set(contact_info[key]))
    
    return contact_info

def detect_threat_indicators(urls):
    """Detect potential threat indicators"""
    threat_indicators = {
        'Dark Web': [],
        'Suspicious Domains': [],
        'Potential Scams': [],
        'Malware Indicators': []
    }
    
    suspicious_keywords = ['hack', 'crack', 'warez', 'torrent', 'pirate', 'scam', 'fake', 'phishing']
    malware_keywords = ['malware', 'virus', 'trojan', 'spyware', 'keylogger']
    
    for url in urls:
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()
        
        # Dark Web detection
        if '.onion' in domain or 'tor2web' in domain:
            threat_indicators['Dark Web'].append(url)
        
        # Suspicious domains
        if any(keyword in domain for keyword in suspicious_keywords):
            threat_indicators['Suspicious Domains'].append(url)
        
        # Potential scams
        if any(keyword in url_lower for keyword in ['scam', 'fake', 'phishing']):
            threat_indicators['Potential Scams'].append(url)
        
        # Malware indicators
        if any(keyword in url_lower for keyword in malware_keywords):
            threat_indicators['Malware Indicators'].append(url)
    
    return threat_indicators

def extract_page_title(url):
    """Try to extract page title for better result display"""
    try:
        headers = {
            'User-Agent': get_random_user_agent()
        }
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title:
                return title.get_text().strip()
    except:
        pass
    return None

class WebSearch:
    def __init__(self, query) -> None:
        self.query = query
        self.lookup()

    def lookup(self):
        print(Fore.CYAN + "\n🔍 Starting Advanced Web Search (DuckDuckGo + Bing)...")
        print(Fore.YELLOW + f"Query: {self.query}")
        
        # Create user folder
        user_folder = create_user_folder(self.query)
        print(Fore.GREEN + f"📁 Created folder: {user_folder}")
        
        all_results = []
        search_engines_used = []
        
        # Create smart search variations
        search_variations = create_search_variations(self.query)
        print(Fore.YELLOW + f"\n🧠 Created {len(search_variations)} search variations for better accuracy")
        
        # Search with DuckDuckGo (primary engine)
        print(Fore.YELLOW + "\n🌐 Searching with DuckDuckGo (primary engine)...")
        
        for i, variation in enumerate(search_variations, 1):
            print(Fore.BLUE + f"Strategy {i}: Searching DuckDuckGo for '{variation}'")
            
            duckduckgo_results = search_duckduckgo(variation, 15)
            if duckduckgo_results:
                all_results.extend(duckduckgo_results)
                if 'DuckDuckGo' not in search_engines_used:
                    search_engines_used.append('DuckDuckGo')
                print(Fore.GREEN + f"  ✅ Found {len(duckduckgo_results)} results")
            else:
                print(Fore.RED + f"  ❌ No results from DuckDuckGo")
            
            # Add delay between searches
            if i < len(search_variations):
                delay = random.uniform(3, 6)  # 3-6 second delay
                print(Fore.YELLOW + f"  ⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        # Search with Bing (secondary engine)
        print(Fore.YELLOW + "\n🌐 Searching with Bing (secondary engine)...")
        
        for i, variation in enumerate(search_variations, 1):
            print(Fore.BLUE + f"Strategy {i}: Searching Bing for '{variation}'")
            
            bing_results = search_bing(variation, 15)
            if bing_results:
                all_results.extend(bing_results)
                if 'Bing' not in search_engines_used:
                    search_engines_used.append('Bing')
                print(Fore.GREEN + f"  ✅ Found {len(bing_results)} results")
            else:
                print(Fore.RED + f"  ❌ No results from Bing")
            
            # Add delay between searches
            if i < len(search_variations):
                delay = random.uniform(3, 6)  # 3-6 second delay
                print(Fore.YELLOW + f"  ⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        # Try Google as fallback only if other engines failed
        if not all_results:
            print(Fore.YELLOW + "\n🔄 No results from primary engines, trying Google fallback...")
            google_results = search_google_fallback(self.query, 10)
            if google_results:
                all_results.extend(google_results)
                search_engines_used.append('Google (Fallback)')
                print(Fore.GREEN + f"✅ Found {len(google_results)} results from Google fallback")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for url in all_results:
            if url not in seen:
                seen.add(url)
                unique_results.append(url)
        
        all_results = unique_results
        
        if not all_results:
            print(Fore.RED + "❌ No results found. Try a different query or check your internet connection.")
            print(Fore.YELLOW + "💡 Tip: Try a different search term or wait a few minutes before trying again.")
            return
        
        print(Fore.GREEN + f"\n📊 Total unique results: {len(all_results)}")
        
        # Filter and rank results by relevance
        print(Fore.YELLOW + "\n🎯 Ranking results by relevance...")
        ranked_results = filter_relevant_results(all_results, self.query)
        
        # Categorize results
        print(Fore.YELLOW + "\n📂 Categorizing results...")
        categorized_results = {}
        for url in ranked_results:
            category = categorize_url(url)
            if category not in categorized_results:
                categorized_results[category] = []
            categorized_results[category].append(url)
        
        # Extract social media profiles
        print(Fore.YELLOW + "\n📱 Extracting social media profiles...")
        social_media = extract_social_media(ranked_results)
        
        # Extract contact information
        print(Fore.YELLOW + "\n📞 Extracting contact information...")
        contact_info = extract_contact_info(ranked_results)
        
        # Detect threat indicators
        print(Fore.YELLOW + "\n⚠️  Analyzing threat indicators...")
        threat_indicators = detect_threat_indicators(ranked_results)
        
        # Display results
        print(Fore.MAGENTA + "\n========== Advanced Web Search Results ==========")
        print(Fore.CYAN + f"Query: {self.query}")
        print(Fore.CYAN + f"Total Results: {len(ranked_results)}")
        print(Fore.CYAN + f"Search Engines: {', '.join(search_engines_used)}")
        print(Fore.CYAN + f"Search Strategies: {len(search_variations)}")
        
        # Display all results first (ranked by relevance)
        print(Fore.LIGHTGREEN_EX + f"\n=== TOP RESULTS (Ranked by Relevance) ===")
        for i, url in enumerate(ranked_results[:20], 1):  # Show top 20 results
            domain = urlparse(url).netloc
            print(Fore.WHITE + f"{i:2d}. {domain}")
            print(Fore.LIGHTBLACK_EX + f"    {url}")
            
            # Try to get page title (with shorter timeout)
            try:
                title = extract_page_title(url)
                if title and len(title) < 80:
                    print(Fore.CYAN + f"    📄 {title}")
            except:
                pass  # Skip title extraction if it fails
        
        if len(ranked_results) > 20:
            print(Fore.YELLOW + f"\n... and {len(ranked_results) - 20} more results")
        
        # Display categorized results
        print(Fore.LIGHTGREEN_EX + f"\n=== RESULTS BY CATEGORY ===")
        for category, urls in categorized_results.items():
            print(Fore.LIGHTGREEN_EX + f"\n{category} ({len(urls)} results):")
            for url in urls[:5]:  # Show first 5 URLs per category
                domain = urlparse(url).netloc
                print(Fore.WHITE + f"  • {domain}")
                print(Fore.LIGHTBLACK_EX + f"    {url}")
            if len(urls) > 5:
                print(Fore.YELLOW + f"  ... and {len(urls) - 5} more")
        
        # Display social media profiles
        if social_media:
            print(Fore.LIGHTMAGENTA_EX + f"\n=== SOCIAL MEDIA PROFILES ===")
            for platform, profiles in social_media.items():
                print(Fore.LIGHTMAGENTA_EX + f"\n{platform} ({len(profiles)} profiles):")
                for profile in profiles:
                    print(Fore.WHITE + f"  • {profile}")
        
        # Display contact information
        if any(contact_info.values()):
            print(Fore.LIGHTCYAN_EX + f"\n=== CONTACT INFORMATION ===")
            for contact_type, contacts in contact_info.items():
                if contacts:
                    print(Fore.LIGHTCYAN_EX + f"\n{contact_type} ({len(contacts)} found):")
                    for contact in contacts:
                        print(Fore.WHITE + f"  • {contact}")
        
        # Display threat indicators
        if any(threat_indicators.values()):
            print(Fore.LIGHTRED_EX + f"\n=== THREAT INDICATORS ===")
            for threat_type, threats in threat_indicators.items():
                if threats:
                    print(Fore.LIGHTRED_EX + f"\n{threat_type} ({len(threats)} indicators):")
                    for threat in threats:
                        print(Fore.WHITE + f"  • {threat}")
        
        # Smart summary
        print(Fore.LIGHTMAGENTA_EX + f"\n=== SMART SUMMARY ===")
        summary = []
        
        # Relevance analysis
        if len(ranked_results) > 30:
            summary.append("Extensive online presence detected.")
        elif len(ranked_results) > 15:
            summary.append("Significant online presence.")
        elif len(ranked_results) > 5:
            summary.append("Moderate online presence.")
        else:
            summary.append("Limited online presence.")
        
        # Check for exact matches
        exact_matches = [url for url in ranked_results if self.query.lower() in url.lower()]
        if exact_matches:
            summary.append(f"Found {len(exact_matches)} exact matches.")
        
        if social_media:
            summary.append(f"Active on {len(social_media)} social media platforms.")
        
        if any(contact_info.values()):
            summary.append("Contact information available online.")
        
        if any(threat_indicators.values()):
            summary.append("⚠️  Potential threat indicators detected.")
        
        if 'Government & Military' in categorized_results:
            summary.append("Government/military connections found.")
        
        if 'Educational' in categorized_results:
            summary.append("Educational background detected.")
        
        # Search quality assessment
        if 'Google (Fallback)' in search_engines_used:
            summary.append("⚠️  Used Google fallback due to primary engine limitations.")
        
        if len(search_variations) > 2:
            summary.append("Used multiple search strategies for comprehensive results.")
        
        print(Fore.LIGHTMAGENTA_EX + f"Summary: {' '.join(summary)}")
        
        # Export to CSV
        csv_filename = os.path.join(user_folder, f"{self.query.replace(' ', '_')}_web_search.csv")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['#', 'URL', 'Domain', 'Category', 'Relevance Score'])
            
            for i, url in enumerate(ranked_results, 1):
                domain = urlparse(url).netloc
                category = categorize_url(url)
                # Calculate relevance score
                score = 0
                url_lower = url.lower()
                query_lower = self.query.lower()
                if query_lower in url_lower:
                    score = 100
                elif any(word in url_lower for word in query_lower.split()):
                    score = 50
                
                writer.writerow([i, url, domain, category, score])
            
            if social_media:
                writer.writerow([])
                writer.writerow(['Social Media Platform', 'Profile URL'])
                for platform, profiles in social_media.items():
                    for profile in profiles:
                        writer.writerow([platform, profile])
            
            if any(contact_info.values()):
                writer.writerow([])
                writer.writerow(['Contact Type', 'Contact Info'])
                for contact_type, contacts in contact_info.items():
                    for contact in contacts:
                        writer.writerow([contact_type, contact])
        
        print(Fore.GREEN + f"📊 CSV results saved as {csv_filename}")
        
        # Export to PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=filter_latin(f"Advanced Web Search Report for: {self.query}"), ln=True, align='C')
        pdf.cell(200, 10, txt=filter_latin(f"Total Results: {len(ranked_results)}"), ln=True)
        pdf.cell(200, 10, txt=filter_latin(f"Search Engines: {', '.join(search_engines_used)}"), ln=True)
        pdf.cell(200, 10, txt=filter_latin(f"Search Strategies: {len(search_variations)}"), ln=True)
        pdf.cell(200, 10, txt=filter_latin(f"Summary: {' '.join(summary)}"), ln=True)
        
        pdf.cell(200, 10, txt=filter_latin("Top Results (Ranked by Relevance):"), ln=True)
        for i, url in enumerate(ranked_results[:30], 1):  # Top 30 results
            domain = urlparse(url).netloc
            pdf.cell(200, 10, txt=filter_latin(f"{i:2d}. {domain}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"    {url}"), ln=True)
        
        for category, urls in categorized_results.items():
            pdf.cell(200, 10, txt=filter_latin(f"{category} ({len(urls)} results):"), ln=True)
            for url in urls[:10]:  # Limit to first 10 URLs per category
                pdf.cell(200, 10, txt=filter_latin(f"  • {url}"), ln=True)
        
        if social_media:
            pdf.cell(200, 10, txt=filter_latin("Social Media Profiles:"), ln=True)
            for platform, profiles in social_media.items():
                pdf.cell(200, 10, txt=filter_latin(f"  {platform}:"), ln=True)
                for profile in profiles:
                    pdf.cell(200, 10, txt=filter_latin(f"    • {profile}"), ln=True)
        
        pdf_path = os.path.join(user_folder, f"{self.query.replace(' ', '_')}_web_search.pdf")
        pdf.output(pdf_path)
        print(Fore.GREEN + f"📄 PDF report saved as {pdf_path}")
        
        # Export to HTML
        html = Template(HTML_TEMPLATE).render(
            query=self.query,
            total_results=len(ranked_results),
            search_engines=', '.join(search_engines_used),
            categories_found=len(categorized_results),
            social_count=len(social_media),
            contact_count=sum(len(contacts) for contacts in contact_info.values()),
            threat_count=sum(len(threats) for threats in threat_indicators.values()),
            categorized_results=categorized_results,
            social_media=social_media,
            contact_info=contact_info,
            threat_indicators=threat_indicators,
            now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        html_path = os.path.join(user_folder, f"{self.query.replace(' ', '_')}_web_search.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(Fore.GREEN + f"🌐 HTML report saved as {html_path}")
        
        print(Fore.LIGHTGREEN_EX + f"\n📁 All files saved in folder: {user_folder}")
        print(Fore.LIGHTGREEN_EX + "\n========== Advanced Web Search Completed! ==========")
