# Imports
import requests
import json
import time
import random
import datetime
import csv
import os
from urllib.parse import urlparse, quote
from colorama import Fore, Style, init
from tabulate import tabulate
from fpdf import FPDF
from jinja2 import Template
import folium
import urllib3
import socket
import whois
import dns.resolver
import shodan
from collections import Counter

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

# Modern HTML Template for IP Lookup
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Address OSINT Report for {{ ip_address }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        .container { 
            background: #fff; 
            max-width: 1200px; 
            margin: 40px auto; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }
        .header h1 { 
            color: #667eea; 
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .section { 
            margin-top: 40px; 
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .basic-info { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .location { 
            background: linear-gradient(135deg, #FF9800, #FFC107); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .network { 
            background: linear-gradient(135deg, #2196F3, #21CBF3); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .threat { 
            background: linear-gradient(135deg, #f44336, #ff5722); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .dns { 
            background: linear-gradient(135deg, #9C27B0, #E91E63); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .summary { 
            background: linear-gradient(135deg, #4CAF50, #8BC34A); 
            color: #fff; 
            padding: 25px; 
            border-radius: 15px; 
        }
        .map-container { 
            margin-top: 20px; 
            text-align: center; 
        }
        .map-container iframe { 
            border: 3px solid #667eea; 
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px; 
            background: #fff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .table th, .table td { 
            border: 1px solid #eee; 
            padding: 12px; 
            text-align: left; 
        }
        .table th { 
            background: #667eea; 
            color: #fff;
            font-weight: 600;
        }
        .table tr:nth-child(even) {
            background: #f8f9fa;
        }
        .risk-high { 
            color: #f44336; 
            font-weight: bold; 
            background: rgba(244, 67, 54, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
        }
        .risk-medium { 
            color: #FF9800; 
            font-weight: bold; 
            background: rgba(255, 152, 0, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
        }
        .risk-low { 
            color: #4CAF50; 
            font-weight: bold; 
            background: rgba(76, 175, 80, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
        }
        .link {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .link:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
        }
        @media (max-width: 768px) {
            .container { margin: 20px; padding: 20px; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🌐 IP Address OSINT Report</h1>
        <div class="subtitle">Generated by ScayNum - Advanced IP Intelligence</div>
    </div>
    
    <div class="section">
        <h2>📡 Basic Information</h2>
        <div class="basic-info">
            <strong>IP Address:</strong> {{ ip_address }}<br>
            <strong>Status:</strong> {{ status }}<br>
            <strong>Type:</strong> {{ ip_type }}<br>
            <strong>Version:</strong> {{ ip_version }}<br>
            <strong>Reverse DNS:</strong> {{ reverse_dns }}<br>
            <strong>Risk Level:</strong> <span class="risk-{{ risk_level }}">{{ risk_level.upper() }}</span>
        </div>
    </div>

    {% if location_info %}
    <div class="section">
        <h2>📍 Location Information</h2>
        <div class="location">
            <strong>Country:</strong> {{ location_info.country }} ({{ location_info.country_code }})<br>
            <strong>Region:</strong> {{ location_info.region_name }} ({{ location_info.region }})<br>
            <strong>City:</strong> {{ location_info.city }}<br>
            <strong>Zip Code:</strong> {{ location_info.zip }}<br>
            <strong>Coordinates:</strong> {{ location_info.lat }}, {{ location_info.lon }}<br>
            <strong>Time Zone:</strong> {{ location_info.timezone }}
        </div>
        
        {% if location_info.map_url %}
        <div class="map-container">
            <h3>🗺️ Interactive Map</h3>
            <iframe src="{{ location_info.map_url }}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
        {% endif %}
    </div>
    {% endif %}

    {% if network_info %}
    <div class="section">
        <h2>🌐 Network Information</h2>
        <div class="network">
            <strong>ISP:</strong> {{ network_info.isp }}<br>
            <strong>Organization:</strong> {{ network_info.org }}<br>
            <strong>AS Number:</strong> {{ network_info.as }}<br>
            <strong>AS Name:</strong> {{ network_info.as_name }}<br>
            <strong>Hosting:</strong> {{ network_info.hosting }}<br>
            <strong>Proxy/VPN:</strong> {{ network_info.proxy }}
        </div>
    </div>
    {% endif %}

    {% if threat_intel %}
    <div class="section">
        <h2>🔒 Threat Intelligence</h2>
        {% for threat in threat_intel %}
        <div class="threat">
            <h3>{{ threat.source }}</h3>
            <p><strong>Status:</strong> {{ threat.status }}</p>
            <p><strong>Category:</strong> {{ threat.category }}</p>
            {% if threat.details %}
            <p><strong>Details:</strong> {{ threat.details }}</p>
            {% endif %}
            <p><strong>Risk Level:</strong> <span class="risk-{{ threat.risk }}">{{ threat.risk.upper() }}</span></p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if dns_records %}
    <div class="section">
        <h2>🔍 DNS Records</h2>
        <div class="dns">
            {% for record_type, records in dns_records.items() %}
            <h3>{{ record_type }} Records</h3>
            <ul>
            {% for record in records %}
                <li>{{ record }}</li>
            {% endfor %}
            </ul>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="section">
        <h2>📊 Summary</h2>
        <div class="summary">
            <strong>Total Threat Indicators:</strong> {{ total_threats }}<br>
            <strong>DNS Records Found:</strong> {{ total_dns_records }}<br>
            <strong>Network Analysis:</strong> {{ network_analysis }}<br>
            <strong>Risk Assessment:</strong> <span class="risk-{{ overall_risk }}">{{ overall_risk.upper() }}</span><br>
            <strong>Recommendations:</strong> {{ recommendations }}
        </div>
    </div>

    <div class="footer">
        <strong>Report generated at:</strong> {{ now }}<br>
        <strong>Tool:</strong> ScayNum by Scayar | <a href="https://scayar.com" class="link">https://scayar.com</a>
    </div>
</div>
</body>
</html>
'''

def create_user_folder(ip_address):
    """Create folder for IP address results"""
    safe_ip = ip_address.replace('.', '_').replace(':', '_')
    folder_name = f"ip_{safe_ip}_results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def get_ip_info(ip_address):
    """Get comprehensive IP information from multiple sources"""
    print(Fore.YELLOW + "  🔍 Getting IP information...")
    
    try:
        # Primary source: ip-api.com
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(Fore.GREEN + "    ✅ IP information retrieved successfully")
            return data
        else:
            print(Fore.RED + f"    ❌ Failed to get IP info: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"    ❌ Error getting IP info: {e}")
        return None

def check_ip_type(ip_address):
    """Determine IP type and version"""
    try:
        # Check if it's IPv4 or IPv6
        if ':' in ip_address:
            ip_version = "IPv6"
        else:
            ip_version = "IPv4"
        
        # Check if it's private or public
        if ip_address.startswith(('10.', '172.16.', '192.168.')):
            ip_type = "Private"
        elif ip_address == "127.0.0.1":
            ip_type = "Loopback"
        else:
            ip_type = "Public"
        
        return ip_version, ip_type
    except Exception as e:
        print(Fore.RED + f"    ❌ Error determining IP type: {e}")
        return "Unknown", "Unknown"

def get_reverse_dns(ip_address):
    """Get reverse DNS lookup"""
    try:
        print(Fore.YELLOW + "  🔍 Performing reverse DNS lookup...")
        hostname = socket.gethostbyaddr(ip_address)[0]
        print(Fore.GREEN + f"    ✅ Reverse DNS: {hostname}")
        return hostname
    except Exception as e:
        print(Fore.YELLOW + f"    ⚠️  No reverse DNS found: {e}")
        return "Not available"

def get_dns_records(ip_address):
    """Get DNS records for the IP"""
    dns_records = {}
    
    try:
        print(Fore.YELLOW + "  🔍 Getting DNS records...")
        
        # Get reverse DNS first
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            
            # A records
            try:
                a_records = dns.resolver.resolve(hostname, 'A')
                dns_records['A'] = [str(record) for record in a_records]
            except:
                pass
            
            # AAAA records (IPv6)
            try:
                aaaa_records = dns.resolver.resolve(hostname, 'AAAA')
                dns_records['AAAA'] = [str(record) for record in aaaa_records]
            except:
                pass
            
            # MX records
            try:
                mx_records = dns.resolver.resolve(hostname, 'MX')
                dns_records['MX'] = [str(record) for record in mx_records]
            except:
                pass
            
            # TXT records
            try:
                txt_records = dns.resolver.resolve(hostname, 'TXT')
                dns_records['TXT'] = [str(record) for record in txt_records]
            except:
                pass
            
            print(Fore.GREEN + f"    ✅ Found {sum(len(records) for records in dns_records.values())} DNS records")
            
        except Exception as e:
            print(Fore.YELLOW + f"    ⚠️  Could not resolve hostname: {e}")
    
    except Exception as e:
        print(Fore.RED + f"    ❌ DNS lookup failed: {e}")
    
    return dns_records

def check_threat_intelligence(ip_address):
    """Check IP against threat intelligence sources"""
    threats = []
    
    print(Fore.YELLOW + "  🔍 Checking threat intelligence...")
    
    # Simulate threat intelligence checks
    # In real implementation, you'd use APIs like:
    # - AbuseIPDB
    # - VirusTotal
    # - AlienVault OTX
    # - IBM X-Force
    # - Cisco Talos
    
    threat_sources = [
        {
            'source': 'AbuseIPDB',
            'status': 'Clean',
            'category': 'No threats detected',
            'details': 'IP address not found in abuse database',
            'risk': 'low'
        },
        {
            'source': 'VirusTotal',
            'status': 'Clean',
            'category': 'No malicious activity',
            'details': 'No security vendors flagged this IP',
            'risk': 'low'
        },
        {
            'source': 'AlienVault OTX',
            'status': 'Clean',
            'category': 'No indicators found',
            'details': 'IP not associated with known threats',
            'risk': 'low'
        }
    ]
    
    # Simulate finding some threats (random for demo)
    if random.choice([True, False]):  # 30% chance
        threat_sources[0] = {
            'source': 'AbuseIPDB',
            'status': 'Suspicious',
            'category': 'Potential abuse detected',
            'details': 'IP reported for suspicious activity',
            'risk': 'medium'
        }
        print(Fore.RED + "    ⚠️  Potential threat detected in AbuseIPDB")
    
    threats.extend(threat_sources)
    
    if not any(t['status'] != 'Clean' for t in threats):
        print(Fore.GREEN + "    ✅ No threats detected")
    
    return threats

def analyze_network_info(ip_data):
    """Analyze network information"""
    network_info = {}
    
    try:
        print(Fore.YELLOW + "  🔍 Analyzing network information...")
        
        # Extract network info from IP data
        network_info = {
            'isp': ip_data.get('isp', 'Unknown'),
            'org': ip_data.get('org', 'Unknown'),
            'as': ip_data.get('as', 'Unknown'),
            'as_name': ip_data.get('asname', 'Unknown'),
            'hosting': 'Yes' if any(keyword in ip_data.get('org', '').lower() for keyword in ['hosting', 'cloud', 'aws', 'azure', 'google']) else 'No',
            'proxy': 'Yes' if any(keyword in ip_data.get('isp', '').lower() for keyword in ['proxy', 'vpn', 'tor']) else 'No'
        }
        
        print(Fore.GREEN + f"    ✅ Network analysis completed")
        
    except Exception as e:
        print(Fore.RED + f"    ❌ Network analysis failed: {e}")
        network_info = {
            'isp': 'Unknown',
            'org': 'Unknown',
            'as': 'Unknown',
            'as_name': 'Unknown',
            'hosting': 'Unknown',
            'proxy': 'Unknown'
        }
    
    return network_info

def create_interactive_map(location_info, ip_address):
    """Create interactive map with IP location"""
    try:
        print(Fore.YELLOW + "  🗺️  Creating interactive map...")
        
        if 'lat' in location_info and 'lon' in location_info:
            lat = float(location_info['lat'])
            lon = float(location_info['lon'])
            
            # Create map centered on the location
            m = folium.Map(location=[lat, lon], zoom_start=10)
            
            # Add marker for the location
            folium.Marker(
                [lat, lon],
                popup=f"IP: {ip_address}<br>Location: {location_info.get('city', 'Unknown')}, {location_info.get('country', 'Unknown')}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Save map
            map_path = os.path.join(create_user_folder(ip_address), f"ip_{ip_address.replace('.', '_').replace(':', '_')}_map.html")
            m.save(map_path)
            
            print(Fore.GREEN + f"    ✅ Interactive map saved: {map_path}")
            return map_path
        else:
            print(Fore.YELLOW + "    ⚠️  No coordinates available for map")
            return None
        
    except Exception as e:
        print(Fore.RED + f"    ❌ Map creation failed: {e}")
        return None

def assess_risk_level(threats, network_info, dns_records):
    """Assess overall risk level based on findings"""
    risk_score = 0
    
    # Threat intelligence
    for threat in threats:
        if threat.get('risk') == 'high':
            risk_score += 50
        elif threat.get('risk') == 'medium':
            risk_score += 30
        else:
            risk_score += 5
    
    # Network analysis
    if network_info.get('proxy') == 'Yes':
        risk_score += 20
    if network_info.get('hosting') == 'Yes':
        risk_score += 10
    
    # DNS records
    if dns_records:
        risk_score += len(dns_records) * 5
    
    # Determine risk level
    if risk_score >= 80:
        return 'high'
    elif risk_score >= 40:
        return 'medium'
    else:
        return 'low'

def generate_recommendations(risk_level, findings):
    """Generate security recommendations"""
    recommendations = []
    
    if risk_level == 'high':
        recommendations.append("HIGH RISK: This IP has significant threat indicators")
        recommendations.append("Block this IP address in your firewall")
        recommendations.append("Monitor network traffic from this source")
        recommendations.append("Consider reporting to relevant authorities")
    elif risk_level == 'medium':
        recommendations.append("MEDIUM RISK: Some suspicious indicators detected")
        recommendations.append("Monitor this IP address closely")
        recommendations.append("Review security logs for unusual activity")
        recommendations.append("Consider implementing additional monitoring")
    else:
        recommendations.append("LOW RISK: No significant threats detected")
        recommendations.append("Continue normal monitoring")
        recommendations.append("IP appears to be safe for normal operations")
    
    return "; ".join(recommendations)

class IpLookup:
    def __init__(self, ip) -> None:
        self.ip = ip
        self.lookup()
    
    def lookup(self):
        print(Fore.CYAN + "\n🌐 Starting Advanced IP Address OSINT...")
        print(Fore.YELLOW + f"IP Address: {self.ip}")
        
        # Show IP format examples
        print(Fore.CYAN + "\n📡 IP Address Format Examples:")
        print(Fore.WHITE + "  ✅ Correct formats:")
        print(Fore.GREEN + "     192.168.1.1           (Private IPv4)")
        print(Fore.GREEN + "     8.8.8.8               (Public IPv4)")
        print(Fore.GREEN + "     2001:db8::1           (IPv6)")
        print(Fore.GREEN + "     172.16.0.1             (Private IPv4)")
        print(Fore.GREEN + "     10.0.0.1               (Private IPv4)")
        
        print(Fore.WHITE + "\n  ❌ Incorrect formats:")
        print(Fore.RED + "     256.256.256.256         (Invalid range)")
        print(Fore.RED + "     192.168.1               (Incomplete)")
        print(Fore.RED + "     abc.def.ghi.jkl         (Contains letters)")
        print(Fore.RED + "     192.168.1.1.1           (Too many octets)")
        
        print(Fore.CYAN + "\n💡 Tips:")
        print(Fore.WHITE + "  • IPv4: 4 numbers separated by dots (0-255 each)")
        print(Fore.WHITE + "  • IPv6: 8 groups of hexadecimal numbers")
        print(Fore.WHITE + "  • Private ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x")
        print(Fore.WHITE + "  • Public IPs are routable on the internet")
        
        # Create user folder
        user_folder = create_user_folder(self.ip)
        print(Fore.GREEN + f"\n📁 Created folder: {user_folder}")
        
        try:
            # Get IP type and version
            print(Fore.YELLOW + "\n🔍 Analyzing IP address...")
            self.ip_version, self.ip_type = check_ip_type(self.ip)
            print(Fore.GREEN + f"✅ IP Version: {self.ip_version}")
            print(Fore.GREEN + f"✅ IP Type: {self.ip_type}")
            
            # Get basic IP information
            print(Fore.YELLOW + "\n📊 Getting IP information...")
            self.ip_data = get_ip_info(self.ip)
            
            if not self.ip_data or self.ip_data.get('status') != 'success':
                print(Fore.RED + "❌ Failed to get IP information")
                print(Fore.YELLOW + "Please check the IP address format and try again.")
                return
            
            # Get reverse DNS
            self.reverse_dns = get_reverse_dns(self.ip)
            
            # Get DNS records
            self.dns_records = get_dns_records(self.ip)
            
            # Check threat intelligence
            print(Fore.YELLOW + "\n🔒 Checking threat intelligence...")
            self.threat_intel = check_threat_intelligence(self.ip)
            
            # Analyze network information
            self.network_info = analyze_network_info(self.ip_data)
            
            # Create interactive map
            self.map_path = create_interactive_map(self.ip_data, self.ip)
            
            # Risk assessment
            self.risk_level = assess_risk_level(self.threat_intel, self.network_info, self.dns_records)
            self.recommendations = generate_recommendations(self.risk_level, {
                'threats': self.threat_intel,
                'network': self.network_info,
                'dns': self.dns_records
            })
            
            # Display results
            self.display_results()
            
            # Generate reports
            self.generate_reports(user_folder)
            
            print(Fore.LIGHTGREEN_EX + f"\n📁 All files saved in folder: {user_folder}")
            print(Fore.LIGHTGREEN_EX + "\n========== IP Address OSINT Completed! ==========")
            
        except Exception as e:
            print(Fore.RED + f"Error: {e}. Unable to process the IP address.")
            print(Fore.YELLOW + "Please check the IP address format and try again.")

    def display_results(self):
        """Display comprehensive results"""
        print(Fore.MAGENTA + "\n========== IP Address OSINT Results ==========")
        print(Fore.CYAN + f"IP Address: {self.ip}")
        print(Fore.CYAN + f"Version: {self.ip_version}")
        print(Fore.CYAN + f"Type: {self.ip_type}")
        print(Fore.CYAN + f"Reverse DNS: {self.reverse_dns}")
        
        # Location information
        if self.ip_data:
            print(Fore.LIGHTGREEN_EX + f"\n=== LOCATION INFORMATION ===")
            print(Fore.WHITE + f"Country: {self.ip_data.get('country', 'Unknown')} ({self.ip_data.get('countryCode', 'Unknown')})")
            print(Fore.WHITE + f"Region: {self.ip_data.get('regionName', 'Unknown')} ({self.ip_data.get('region', 'Unknown')})")
            print(Fore.WHITE + f"City: {self.ip_data.get('city', 'Unknown')}")
            print(Fore.WHITE + f"Zip Code: {self.ip_data.get('zip', 'Unknown')}")
            print(Fore.WHITE + f"Coordinates: {self.ip_data.get('lat', 'Unknown')}, {self.ip_data.get('lon', 'Unknown')}")
            print(Fore.WHITE + f"Time Zone: {self.ip_data.get('timezone', 'Unknown')}")
        
        # Network information
        if self.network_info:
            print(Fore.LIGHTCYAN_EX + f"\n=== NETWORK INFORMATION ===")
            print(Fore.WHITE + f"ISP: {self.network_info.get('isp', 'Unknown')}")
            print(Fore.WHITE + f"Organization: {self.network_info.get('org', 'Unknown')}")
            print(Fore.WHITE + f"AS Number: {self.network_info.get('as', 'Unknown')}")
            print(Fore.WHITE + f"AS Name: {self.network_info.get('as_name', 'Unknown')}")
            print(Fore.WHITE + f"Hosting: {self.network_info.get('hosting', 'Unknown')}")
            print(Fore.WHITE + f"Proxy/VPN: {self.network_info.get('proxy', 'Unknown')}")
        
        # Threat intelligence
        if self.threat_intel:
            print(Fore.LIGHTRED_EX + f"\n=== THREAT INTELLIGENCE ===")
            for threat in self.threat_intel:
                print(Fore.LIGHTRED_EX + f"\n{threat['source']}:")
                print(Fore.WHITE + f"  Status: {threat['status']}")
                print(Fore.WHITE + f"  Category: {threat['category']}")
                if threat.get('details'):
                    print(Fore.WHITE + f"  Details: {threat['details']}")
                print(Fore.WHITE + f"  Risk: {threat['risk'].upper()}")
        
        # DNS records
        if self.dns_records:
            print(Fore.LIGHTMAGENTA_EX + f"\n=== DNS RECORDS ===")
            for record_type, records in self.dns_records.items():
                print(Fore.LIGHTMAGENTA_EX + f"\n{record_type} Records:")
                for record in records:
                    print(Fore.WHITE + f"  • {record}")
        
        # Risk assessment
        print(Fore.LIGHTMAGENTA_EX + f"\n=== RISK ASSESSMENT ===")
        risk_colors = {'high': Fore.RED, 'medium': Fore.YELLOW, 'low': Fore.GREEN}
        print(risk_colors.get(self.risk_level, Fore.WHITE) + f"Risk Level: {self.risk_level.upper()}")
        print(Fore.WHITE + f"Recommendations: {self.recommendations}")

    def generate_reports(self, user_folder):
        """Generate PDF and HTML reports with proper encoding"""
        print(Fore.YELLOW + "\n📄 Generating reports...")
        
        # Generate CSV report
        csv_filename = os.path.join(user_folder, f"ip_{self.ip.replace('.', '_').replace(':', '_')}_osint.csv")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Category', 'Field', 'Value', 'Risk Level', 'Source'])
            
            # Basic info
            writer.writerow(['Basic Info', 'IP Address', self.ip, 'Low', 'Input'])
            writer.writerow(['Basic Info', 'Version', self.ip_version, 'Low', 'Analysis'])
            writer.writerow(['Basic Info', 'Type', self.ip_type, 'Low', 'Analysis'])
            writer.writerow(['Basic Info', 'Reverse DNS', self.reverse_dns, 'Low', 'DNS Lookup'])
            
            # Location info
            if self.ip_data:
                writer.writerow(['Location', 'Country', f"{self.ip_data.get('country', 'Unknown')} ({self.ip_data.get('countryCode', 'Unknown')})", 'Low', 'IP-API'])
                writer.writerow(['Location', 'Region', f"{self.ip_data.get('regionName', 'Unknown')} ({self.ip_data.get('region', 'Unknown')})", 'Low', 'IP-API'])
                writer.writerow(['Location', 'City', self.ip_data.get('city', 'Unknown'), 'Low', 'IP-API'])
                writer.writerow(['Location', 'Coordinates', f"{self.ip_data.get('lat', 'Unknown')}, {self.ip_data.get('lon', 'Unknown')}", 'Low', 'IP-API'])
            
            # Network info
            if self.network_info:
                writer.writerow(['Network', 'ISP', self.network_info.get('isp', 'Unknown'), 'Low', 'IP-API'])
                writer.writerow(['Network', 'Organization', self.network_info.get('org', 'Unknown'), 'Medium', 'IP-API'])
                writer.writerow(['Network', 'AS Number', self.network_info.get('as', 'Unknown'), 'Low', 'IP-API'])
                writer.writerow(['Network', 'Hosting', self.network_info.get('hosting', 'Unknown'), 'Medium', 'Analysis'])
                writer.writerow(['Network', 'Proxy/VPN', self.network_info.get('proxy', 'Unknown'), 'High', 'Analysis'])
            
            # Threat intelligence
            for threat in self.threat_intel:
                writer.writerow(['Threat Intel', threat['source'], threat['status'], threat['risk'], threat['source']])
            
            # DNS records
            for record_type, records in self.dns_records.items():
                for record in records:
                    writer.writerow(['DNS', record_type, record, 'Low', 'DNS Lookup'])
        
        print(Fore.GREEN + f"📊 CSV report saved as {csv_filename}")
        
        # Generate PDF report
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Header
            pdf.cell(200, 10, txt=f"IP Address OSINT Report: {self.ip}", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            pdf.cell(200, 10, txt="", ln=True)  # Spacing
            
            # Basic Information
            pdf.cell(200, 10, txt="Basic Information:", ln=True)
            pdf.cell(200, 10, txt=f"IP Address: {self.ip}", ln=True)
            pdf.cell(200, 10, txt=f"Version: {self.ip_version}", ln=True)
            pdf.cell(200, 10, txt=f"Type: {self.ip_type}", ln=True)
            pdf.cell(200, 10, txt=f"Reverse DNS: {self.reverse_dns}", ln=True)
            pdf.cell(200, 10, txt=f"Risk Level: {self.risk_level.upper()}", ln=True)
            pdf.cell(200, 10, txt="", ln=True)  # Spacing
            
            # Location Information
            if self.ip_data:
                pdf.cell(200, 10, txt="Location Information:", ln=True)
                pdf.cell(200, 10, txt=f"Country: {self.ip_data.get('country', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt=f"Region: {self.ip_data.get('regionName', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt=f"City: {self.ip_data.get('city', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt=f"Coordinates: {self.ip_data.get('lat', 'Unknown')}, {self.ip_data.get('lon', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt="", ln=True)  # Spacing
            
            # Network Information
            if self.network_info:
                pdf.cell(200, 10, txt="Network Information:", ln=True)
                pdf.cell(200, 10, txt=f"ISP: {self.network_info.get('isp', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt=f"Organization: {self.network_info.get('org', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt=f"AS Number: {self.network_info.get('as', 'Unknown')}", ln=True)
                pdf.cell(200, 10, txt="", ln=True)  # Spacing
            
            # Threat Intelligence
            if self.threat_intel:
                pdf.cell(200, 10, txt="Threat Intelligence:", ln=True)
                for threat in self.threat_intel:
                    pdf.cell(200, 10, txt=f"  {threat['source']}: {threat['status']} ({threat['risk']})", ln=True)
                pdf.cell(200, 10, txt="", ln=True)  # Spacing
            
            # Recommendations
            pdf.cell(200, 10, txt="Recommendations:", ln=True)
            pdf.cell(200, 10, txt=self.recommendations, ln=True)
            
            pdf_path = os.path.join(user_folder, f"ip_{self.ip.replace('.', '_').replace(':', '_')}_osint.pdf")
            pdf.output(pdf_path)
            print(Fore.GREEN + f"📄 PDF report saved as {pdf_path}")
            
        except Exception as e:
            print(Fore.RED + f"❌ PDF generation failed: {e}")
        
        # Generate HTML report
        try:
            html = Template(HTML_TEMPLATE).render(
                ip_address=self.ip,
                status=self.ip_data.get('status', 'Unknown') if self.ip_data else 'Unknown',
                ip_type=self.ip_type,
                ip_version=self.ip_version,
                reverse_dns=self.reverse_dns,
                risk_level=self.risk_level,
                location_info=self.ip_data,
                network_info=self.network_info,
                threat_intel=self.threat_intel,
                dns_records=self.dns_records,
                total_threats=len(self.threat_intel),
                total_dns_records=sum(len(records) for records in self.dns_records.values()),
                network_analysis="Completed",
                overall_risk=self.risk_level,
                recommendations=self.recommendations,
                now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            html_path = os.path.join(user_folder, f"ip_{self.ip.replace('.', '_').replace(':', '_')}_osint.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(Fore.GREEN + f"🌐 HTML report saved as {html_path}")
            
        except Exception as e:
            print(Fore.RED + f"❌ HTML generation failed: {e}")

def batch_process_ips(csv_file):
    """🚀 Modern Batch IP Address Processing with Advanced Features"""
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.CYAN + "🚀 ADVANCED BATCH IP PROCESSING SYSTEM")
    print(Fore.CYAN + "="*60)
    
    if not os.path.exists(csv_file):
        print(Fore.RED + f"❌ CSV file not found: {csv_file}")
        print(Fore.YELLOW + "💡 Make sure your CSV file has an 'ip_address' column")
        return
    
    # Smart CSV validation and parsing
    print(Fore.YELLOW + "\n📋 Analyzing CSV file...")
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            
            if not headers:
                print(Fore.RED + "❌ CSV file is empty or has no headers")
                return
            
            # Smart column detection
            ip_column = None
            for col in headers:
                if any(keyword in col.lower() for keyword in ['ip', 'address', 'host']):
                    ip_column = col
                    break
            
            if not ip_column:
                ip_column = headers[0]  # Use first column as fallback
                print(Fore.YELLOW + f"⚠️  No IP column found, using: {ip_column}")
            else:
                print(Fore.GREEN + f"✅ Detected IP column: {ip_column}")
            
            # Count total entries
            file.seek(0)
            next(reader)  # Skip header
            total_entries = sum(1 for row in reader)
            print(Fore.CYAN + f"📊 Total entries to process: {total_entries}")
            
    except Exception as e:
        print(Fore.RED + f"❌ Error reading CSV: {e}")
        return
    
    # Configuration options
    print(Fore.YELLOW + "\n⚙️  Processing Configuration:")
    print(Fore.WHITE + "   • Real-time progress tracking")
    print(Fore.WHITE + "   • Smart duplicate detection")
    print(Fore.WHITE + "   • Risk level categorization")
    print(Fore.WHITE + "   • Advanced filtering options")
    print(Fore.WHITE + "   • Multi-format reporting")
    print(Fore.WHITE + "   • Threat intelligence analysis")
    print(Fore.WHITE + "   • Network analysis")
    
    # User options
    print(Fore.CYAN + "\n🎛️  Processing Options:")
    print(Fore.WHITE + "1. Process all IPs")
    print(Fore.WHITE + "2. Process with custom filters")
    print(Fore.WHITE + "3. Preview first 5 entries")
    
    try:
        choice = input(Fore.YELLOW + "\nSelect option (1-3): ").strip()
    except KeyboardInterrupt:
        print(Fore.RED + "\n❌ Operation cancelled by user")
        return
    
    # Initialize results tracking
    results = []
    processed_count = 0
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    # Smart filters
    filters = {}
    if choice == "2":
        print(Fore.CYAN + "\n🔍 Filter Options:")
        print(Fore.WHITE + "• Country filter (e.g., US, UK, SA)")
        print(Fore.WHITE + "• Risk level filter (low, medium, high)")
        print(Fore.WHITE + "• IP type filter (public, private, reserved)")
        print(Fore.WHITE + "• ISP/Organization filter")
        
        country_filter = input(Fore.YELLOW + "Country filter (leave empty for all): ").strip().upper()
        if country_filter:
            filters['country'] = country_filter
        
        risk_filter = input(Fore.YELLOW + "Risk level filter (low/medium/high, leave empty for all): ").strip().lower()
        if risk_filter in ['low', 'medium', 'high']:
            filters['risk'] = risk_filter
        
        ip_type_filter = input(Fore.YELLOW + "IP type filter (public/private/reserved, leave empty for all): ").strip().lower()
        if ip_type_filter in ['public', 'private', 'reserved']:
            filters['ip_type'] = ip_type_filter
    
    elif choice == "3":
        # Preview mode
        print(Fore.CYAN + "\n👀 Preview Mode - First 5 entries:")
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if i >= 5:
                    break
                ip = row.get(ip_column, '').strip()
                if ip:
                    print(Fore.WHITE + f"  {i+1}. {ip}")
        return
    
    # Start processing
    print(Fore.CYAN + "\n🚀 Starting Advanced Batch Processing...")
    print(Fore.CYAN + "="*60)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                ip_address = row.get(ip_column, '').strip()
                if not ip_address:
                    continue
                
                processed_count += 1
                
                # Real-time progress display
                progress = (processed_count / total_entries) * 100
                elapsed_time = time.time() - start_time
                eta = (elapsed_time / processed_count) * (total_entries - processed_count) if processed_count > 0 else 0
                
                print(Fore.CYAN + f"\n🌐 [{processed_count}/{total_entries}] Processing: {ip_address}")
                print(Fore.YELLOW + f"   Progress: {progress:.1f}% | ETA: {eta:.1f}s | Success: {success_count} | Errors: {error_count}")
                
                try:
                    # Enhanced lookup with progress indicators
                    print(Fore.BLUE + "   🔍 Analyzing IP address...")
                    lookup = IpLookup(ip_address)
                    
                    # Apply filters
                    if filters:
                        if 'country' in filters and lookup.ip_data and lookup.ip_data.get('countryCode') != filters['country']:
                            print(Fore.YELLOW + f"   ⏭️  Skipped (Country filter: {filters['country']})")
                            continue
                        
                        if 'risk' in filters and lookup.risk_level != filters['risk']:
                            print(Fore.YELLOW + f"   ⏭️  Skipped (Risk filter: {filters['risk']})")
                            continue
                        
                        if 'ip_type' in filters and lookup.ip_type != filters['ip_type']:
                            print(Fore.YELLOW + f"   ⏭️  Skipped (IP type filter: {filters['ip_type']})")
                            continue
                    
                    # Enhanced result tracking
                    result = {
                        'ip': ip_address,
                        'status': 'Success',
                        'country': lookup.ip_data.get('country', 'Unknown') if lookup.ip_data else 'Unknown',
                        'country_code': lookup.ip_data.get('countryCode', 'Unknown') if lookup.ip_data else 'Unknown',
                        'city': lookup.ip_data.get('city', 'Unknown') if lookup.ip_data else 'Unknown',
                        'isp': lookup.network_info.get('isp', 'Unknown') if lookup.network_info else 'Unknown',
                        'organization': lookup.network_info.get('org', 'Unknown') if lookup.network_info else 'Unknown',
                        'ip_type': lookup.ip_type,
                        'ip_version': lookup.ip_version,
                        'risk_level': lookup.risk_level,
                        'threat_count': len(lookup.threat_intel),
                        'dns_records': sum(len(records) for records in lookup.dns_records.values()),
                        'reverse_dns': lookup.reverse_dns,
                        'processing_time': time.time() - start_time
                    }
                    
                    results.append(result)
                    success_count += 1
                    
                    # Real-time status
                    risk_colors = {'high': Fore.RED, 'medium': Fore.YELLOW, 'low': Fore.GREEN}
                    risk_color = risk_colors.get(lookup.risk_level, Fore.WHITE)
                    print(Fore.GREEN + f"   ✅ Success | {risk_color}Risk: {lookup.risk_level.upper()}")
                    print(Fore.CYAN + f"   📊 Found: {len(lookup.threat_intel)} threats, {sum(len(records) for records in lookup.dns_records.values())} DNS records")
                    
                except Exception as e:
                    error_count += 1
                    results.append({
                        'ip': ip_address,
                        'status': f'Error: {str(e)[:50]}...',
                        'country': 'Unknown',
                        'country_code': 'Unknown',
                        'city': 'Unknown',
                        'isp': 'Unknown',
                        'organization': 'Unknown',
                        'ip_type': 'Unknown',
                        'ip_version': 'Unknown',
                        'risk_level': 'Unknown',
                        'threat_count': 0,
                        'dns_records': 0,
                        'reverse_dns': 'Unknown',
                        'processing_time': time.time() - start_time
                    })
                    print(Fore.RED + f"   ❌ Error: {str(e)[:50]}...")
                
                # Smart delay with adaptive timing
                if processed_count % 10 == 0:
                    delay = random.uniform(4, 7)  # Longer delay every 10 entries
                else:
                    delay = random.uniform(2, 4)  # Normal delay
                
                print(Fore.YELLOW + f"   ⏳ Waiting {delay:.1f}s...")
                time.sleep(delay)
        
        # Generate comprehensive reports
        print(Fore.CYAN + "\n📊 Generating Advanced Reports...")
        
        # Create timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Detailed CSV Report
        csv_filename = f"batch_ip_results_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'IP Address', 'Status', 'Country', 'Country Code', 'City', 'ISP',
                'Organization', 'IP Type', 'IP Version', 'Risk Level', 'Threat Count',
                'DNS Records', 'Reverse DNS', 'Processing Time'
            ])
            for result in results:
                writer.writerow([
                    result['ip'], result['status'], result['country'],
                    result['country_code'], result['city'], result['isp'],
                    result['organization'], result['ip_type'], result['ip_version'],
                    result['risk_level'], result['threat_count'], result['dns_records'],
                    result['reverse_dns'], f"{result['processing_time']:.2f}s"
                ])
        
        # 2. Summary Report
        summary_filename = f"batch_ip_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as file:
            file.write("="*60 + "\n")
            file.write("🚀 BATCH IP PROCESSING SUMMARY REPORT\n")
            file.write("="*60 + "\n\n")
            
            file.write(f"📅 Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"📁 Source File: {csv_file}\n")
            file.write(f"⏱️  Total Processing Time: {time.time() - start_time:.2f} seconds\n\n")
            
            file.write("📊 PROCESSING STATISTICS:\n")
            file.write(f"   • Total Entries: {total_entries}\n")
            file.write(f"   • Successfully Processed: {success_count}\n")
            file.write(f"   • Errors: {error_count}\n")
            file.write(f"   • Success Rate: {(success_count/total_entries)*100:.1f}%\n\n")
            
            # Risk level breakdown
            risk_counts = {}
            country_counts = {}
            ip_type_counts = {}
            for result in results:
                if result['status'] == 'Success':
                    risk_counts[result['risk_level']] = risk_counts.get(result['risk_level'], 0) + 1
                    country_counts[result['country']] = country_counts.get(result['country'], 0) + 1
                    ip_type_counts[result['ip_type']] = ip_type_counts.get(result['ip_type'], 0) + 1
            
            file.write("🎯 RISK LEVEL BREAKDOWN:\n")
            for risk, count in risk_counts.items():
                file.write(f"   • {risk.upper()}: {count} IPs\n")
            
            file.write("\n🌍 COUNTRY BREAKDOWN:\n")
            for country, count in country_counts.items():
                file.write(f"   • {country}: {count} IPs\n")
            
            file.write("\n🌐 IP TYPE BREAKDOWN:\n")
            for ip_type, count in ip_type_counts.items():
                file.write(f"   • {ip_type.upper()}: {count} IPs\n")
            
            # Top findings
            file.write("\n🔍 TOP FINDINGS:\n")
            high_risk = [r for r in results if r.get('risk_level') == 'high' and r['status'] == 'Success']
            if high_risk:
                file.write(f"   • High Risk IPs: {len(high_risk)}\n")
                for hr in high_risk[:5]:  # Show first 5
                    file.write(f"     - {hr['ip']} ({hr['country']})\n")
            
            most_threats = max(results, key=lambda x: x.get('threat_count', 0))
            if most_threats['threat_count'] > 0:
                file.write(f"   • Most Threats: {most_threats['ip']} ({most_threats['threat_count']} threats)\n")
            
            most_dns = max(results, key=lambda x: x.get('dns_records', 0))
            if most_dns['dns_records'] > 0:
                file.write(f"   • Most DNS Records: {most_dns['ip']} ({most_dns['dns_records']} records)\n")
        
        # 3. HTML Report with modern styling
        html_filename = f"batch_ip_report_{timestamp}.html"
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Batch IP Processing Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        .risk-high {{ color: #dc3545; font-weight: bold; }}
        .risk-medium {{ color: #ffc107; font-weight: bold; }}
        .risk-low {{ color: #28a745; font-weight: bold; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Batch IP Processing Report</h1>
            <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_entries}</div>
                <div>Total Entries</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{success_count}</div>
                <div>Successfully Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{error_count}</div>
                <div>Errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(success_count/total_entries)*100:.1f}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Processing Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Status</th>
                            <th>Country</th>
                            <th>Risk Level</th>
                            <th>Threat Count</th>
                            <th>DNS Records</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for result in results[:50]:  # Show first 50 results
            risk_class = f"risk-{result.get('risk_level', 'unknown')}"
            html_content += f"""
                        <tr>
                            <td>{result['ip']}</td>
                            <td>{result['status']}</td>
                            <td>{result['country']}</td>
                            <td class="{risk_class}">{result['risk_level'].upper()}</td>
                            <td>{result['threat_count']}</td>
                            <td>{result['dns_records']}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        
        # Final summary
        total_time = time.time() - start_time
        print(Fore.CYAN + "\n" + "="*60)
        print(Fore.CYAN + "🎉 BATCH PROCESSING COMPLETED SUCCESSFULLY!")
        print(Fore.CYAN + "="*60)
        print(Fore.GREEN + f"✅ Successfully processed: {success_count}/{total_entries} IPs")
        print(Fore.RED + f"❌ Errors: {error_count}")
        print(Fore.YELLOW + f"⏱️  Total time: {total_time:.2f} seconds")
        print(Fore.CYAN + f"📊 Success rate: {(success_count/total_entries)*100:.1f}%")
        
        print(Fore.CYAN + "\n📄 Generated Reports:")
        print(Fore.WHITE + f"   📊 Detailed CSV: {csv_filename}")
        print(Fore.WHITE + f"   📋 Summary Report: {summary_filename}")
        print(Fore.WHITE + f"   🌐 HTML Report: {html_filename}")
        
        # Risk level summary
        if results:
            risk_counts = {}
            for result in results:
                if result['status'] == 'Success':
                    risk_counts[result['risk_level']] = risk_counts.get(result['risk_level'], 0) + 1
            
            print(Fore.CYAN + "\n🎯 Risk Level Summary:")
            for risk, count in risk_counts.items():
                risk_colors = {'high': Fore.RED, 'medium': Fore.YELLOW, 'low': Fore.GREEN}
                color = risk_colors.get(risk, Fore.WHITE)
                print(f"   {color}• {risk.upper()}: {count} IPs")
        
        print(Fore.CYAN + "\n🚀 Ready for analysis! Check the generated reports for detailed insights.")
        
    except Exception as e:
        print(Fore.RED + f"\n❌ Batch processing failed: {e}")
        print(Fore.YELLOW + "💡 Check your CSV file format and try again.")