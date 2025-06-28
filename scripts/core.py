#!/usr/bin/env python3
# Imports
import pyfiglet
import logging
import os
import subprocess
import sys
from colorama import Fore, Style

# Class Imports
from social_intelligence import SearchInsta
from web_intelligence import WebSearch
from phone_intelligence import Lookup, batch_process_phones
from ip_intelligence import IpLookup, batch_process_ips
from username_intelligence import SearchUsername

# ScayNum by Scayar
# Owner & Creator: Scayar
# GitHub: https://github.com/Scayar
# Website: https://scayar.com
# Email: Scayar.exe@gmail.com
# Telegram Group: https://t.me/im_scayar

def check_git_available():
    """Check if git is available on the system"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_git_repository():
    """Check if current directory is a git repository"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, text=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_current_version():
    """Get current version/commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "Unknown"

def get_remote_url():
    """Get the remote repository URL"""
    try:
        result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def update_scaynum():
    """Update ScayNum to the latest version"""
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.CYAN + "🔄 SCAYNUM UPDATE SYSTEM")
    print(Fore.CYAN + "="*60)
    
    # Check if git is available
    if not check_git_available():
        print(Fore.RED + "❌ Git is not installed or not available in PATH")
        print(Fore.YELLOW + "💡 Please install Git from: https://git-scm.com/")
        print(Fore.WHITE + "   Then try updating again.")
        return False
    
    # Check if this is a git repository
    if not check_git_repository():
        print(Fore.RED + "❌ This directory is not a Git repository")
        print(Fore.YELLOW + "💡 To enable updates, clone the repository using:")
        print(Fore.WHITE + "   git clone https://github.com/Scayar/ScayNum.git")
        return False
    
    # Get current version
    current_version = get_current_version()
    print(Fore.CYAN + f"📋 Current version: {current_version}")
    
    # Get remote URL
    remote_url = get_remote_url()
    if remote_url:
        print(Fore.CYAN + f"🌐 Remote repository: {remote_url}")
    
    print(Fore.YELLOW + "\n🔄 Checking for updates...")
    
    try:
        # Fetch latest changes
        print(Fore.BLUE + "   📥 Fetching latest changes...")
        result = subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(Fore.RED + f"❌ Failed to fetch updates: {result.stderr}")
            return False
        
        # Check if there are updates
        result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], capture_output=True, text=True)
        commits_behind = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
        if commits_behind == 0:
            print(Fore.GREEN + "✅ ScayNum is already up to date!")
            print(Fore.CYAN + f"   Current version: {current_version}")
            return True
        
        print(Fore.YELLOW + f"📦 Found {commits_behind} new commit(s)")
        
        # Show what's new
        print(Fore.CYAN + "\n📋 Recent changes:")
        result = subprocess.run(['git', 'log', 'HEAD..origin/main', '--oneline', '--max-count=5'], capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(Fore.WHITE + f"   • {line}")
        
        # Ask for confirmation
        print(Fore.YELLOW + "\n⚠️  Do you want to update ScayNum? (y/n): ", end='')
        confirm = input().lower().strip()
        
        if confirm not in ['y', 'yes']:
            print(Fore.YELLOW + "❌ Update cancelled by user")
            return False
        
        # Perform the update
        print(Fore.BLUE + "\n🔄 Updating ScayNum...")
        
        # Pull latest changes
        result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(Fore.RED + f"❌ Update failed: {result.stderr}")
            return False
        
        # Get new version
        new_version = get_current_version()
        
        print(Fore.GREEN + "\n✅ Update completed successfully!")
        print(Fore.CYAN + f"   Previous version: {current_version}")
        print(Fore.CYAN + f"   New version: {new_version}")
        
        # Check for new dependencies
        if os.path.exists('requirements.txt'):
            print(Fore.YELLOW + "\n📦 Checking for new dependencies...")
            print(Fore.WHITE + "   Run 'pip install -r requirements.txt' to install new dependencies")
        
        print(Fore.CYAN + "\n🚀 ScayNum has been updated! Restart the application to use the latest features.")
        return True
        
    except Exception as e:
        print(Fore.RED + f"❌ Update failed with error: {str(e)}")
        print(Fore.YELLOW + "💡 Please try updating manually or contact support.")
        return False

def main():
    """Main function to run ScayNum"""
    # Print the banner
    nameOfTheScript = "ScayNum by Scayar"
    banner = pyfiglet.figlet_format(nameOfTheScript, font = "slant")
    
    # ASCII Art Logo
    ascii_logo = """
______________¶¶¶
_____________¶¶_¶¶¶¶
____________¶¶____¶¶¶
___________¶¶¶______¶¶
___________¶¶¶_______¶¶
__________¶¶¶¶________¶¶
__________¶_¶¶_________¶¶
__________¶__¶¶_________¶¶____¶¶
__________¶__¶¶__________¶¶¶¶¶¶¶
_________¶¶__¶¶¶______¶¶¶¶¶¶___¶
_________¶¶___¶¶__¶¶¶¶¶¶__¶¶
_______¶¶_¶____¶¶¶¶________¶¶
______¶¶__¶¶___¶¶__________¶¶
_____¶¶____¶¶___¶¶__________¶¶
___¶¶_______¶¶___¶¶_________¶¶
___¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶_________¶
_¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶_¶¶________¶¶
¶¶__¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶______¶¶
¶¶¶¶¶___¶______¶___¶¶¶¶¶_____¶¶
________¶¶¶¶¶¶¶¶______¶¶¶¶¶_¶¶
______¶¶¶¶¶¶¶¶¶¶¶________¶¶¶¶
______¶¶¶¶¶¶¶¶¶¶¶¶
______¶__¶¶_¶¶¶¶¶¶
_____¶¶______¶___¶
_____¶¶_____¶¶___¶
_____¶______¶¶___¶
____¶¶______¶¶___¶¶
____¶¶______¶¶___¶¶
___¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶
__¶¶¶¶¶¶¶¶¶_¶¶¶¶¶¶¶¶
__¶¶________¶¶¶____¶¶
____¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶
"""
    
    # Split banner into lines
    banner_lines = banner.split('\n')
    
    # Print the banner with colors
    print(Fore.CYAN + ascii_logo)
    print(Fore.MAGENTA + banner)
    print(Fore.YELLOW + "="*60)
    print(Fore.CYAN + "🚀 Advanced OSINT Tool for Educational Purposes")
    print(Fore.CYAN + "📧 Email: Scayar.exe@gmail.com")
    print(Fore.CYAN + "🌐 Website: https://scayar.com")
    print(Fore.CYAN + "📱 Telegram: https://t.me/im_scayar")
    print(Fore.YELLOW + "="*60)
    
    # Check for updates
    print(Fore.BLUE + "\n🔄 Checking for updates...")
    if check_git_available() and check_git_repository():
        try:
            result = subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True)
            if result.returncode == 0:
                result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], capture_output=True, text=True)
                commits_behind = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                if commits_behind > 0:
                    print(Fore.YELLOW + f"📦 {commits_behind} update(s) available!")
                    print(Fore.CYAN + "💡 Run 'python main.py --update' to update")
                else:
                    print(Fore.GREEN + "✅ ScayNum is up to date!")
        except:
            print(Fore.YELLOW + "⚠️  Could not check for updates")
    else:
        print(Fore.YELLOW + "⚠️  Update checking disabled (not a git repository)")
    
    # Main menu
    while True:
        print(Fore.MAGENTA + "\n" + "="*60)
        print(Fore.CYAN + "🎯 SCAYNUM MAIN MENU")
        print(Fore.MAGENTA + "="*60)
        print(Fore.WHITE + "1. 📱 Phone Number OSINT")
        print(Fore.WHITE + "2. 🌐 IP Address Lookup")
        print(Fore.WHITE + "3. 🔍 Web Search")
        print(Fore.WHITE + "4. 📸 Instagram OSINT")
        print(Fore.WHITE + "5. 👤 Username Search")
        print(Fore.WHITE + "6. 📊 Batch Processing")
        print(Fore.WHITE + "7. 🔄 Update ScayNum")
        print(Fore.WHITE + "8. ❌ Exit")
        print(Fore.MAGENTA + "="*60)
        
        choice = input(Fore.YELLOW + "🎯 Select an option (1-8): " + Style.RESET_ALL).strip()
        
        if choice == "1":
            print(Fore.CYAN + "\n📱 Phone Number OSINT")
            print(Fore.YELLOW + "Enter phone number (with country code, e.g., +1234567890):")
            phone = input(Fore.WHITE + "📞 Phone: " + Style.RESET_ALL).strip()
            if phone:
                try:
                    Lookup(phone)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
            else:
                print(Fore.RED + "❌ Please enter a valid phone number")
                
        elif choice == "2":
            print(Fore.CYAN + "\n🌐 IP Address Lookup")
            print(Fore.YELLOW + "Enter IP address:")
            ip = input(Fore.WHITE + "🌐 IP: " + Style.RESET_ALL).strip()
            if ip:
                try:
                    IpLookup(ip)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
            else:
                print(Fore.RED + "❌ Please enter a valid IP address")
                
        elif choice == "3":
            print(Fore.CYAN + "\n🔍 Web Search")
            print(Fore.YELLOW + "Enter search query:")
            query = input(Fore.WHITE + "🔍 Query: " + Style.RESET_ALL).strip()
            if query:
                try:
                    WebSearch(query)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
            else:
                print(Fore.RED + "❌ Please enter a search query")
                
        elif choice == "4":
            print(Fore.CYAN + "\n📸 Instagram OSINT")
            print(Fore.YELLOW + "Enter Instagram username:")
            username = input(Fore.WHITE + "📸 Username: " + Style.RESET_ALL).strip()
            if username:
                try:
                    SearchInsta(username)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
            else:
                print(Fore.RED + "❌ Please enter a valid username")
                
        elif choice == "5":
            print(Fore.CYAN + "\n👤 Username Search")
            print(Fore.YELLOW + "Enter username to search across platforms:")
            username = input(Fore.WHITE + "👤 Username: " + Style.RESET_ALL).strip()
            if username:
                try:
                    SearchUsername(username)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
            else:
                print(Fore.RED + "❌ Please enter a valid username")
                
        elif choice == "6":
            print(Fore.CYAN + "\n📊 Batch Processing")
            print(Fore.YELLOW + "Select batch processing type:")
            print(Fore.WHITE + "1. Phone Numbers (CSV)")
            print(Fore.WHITE + "2. IP Addresses (CSV)")
            print(Fore.WHITE + "3. Back to main menu")
            
            batch_choice = input(Fore.YELLOW + "Select (1-3): " + Style.RESET_ALL).strip()
            
            if batch_choice == "1":
                csv_file = input(Fore.CYAN + "📁 Enter CSV file path: " + Style.RESET_ALL).strip()
                if csv_file and os.path.exists(csv_file):
                    try:
                        batch_process_phones(csv_file)
                    except Exception as e:
                        print(Fore.RED + f"❌ Error: {e}")
                else:
                    print(Fore.RED + "❌ File not found")
                    
            elif batch_choice == "2":
                csv_file = input(Fore.CYAN + "📁 Enter CSV file path: " + Style.RESET_ALL).strip()
                if csv_file and os.path.exists(csv_file):
                    try:
                        batch_process_ips(csv_file)
                    except Exception as e:
                        print(Fore.RED + f"❌ Error: {e}")
                else:
                    print(Fore.RED + "❌ File not found")
                    
        elif choice == "7":
            update_scaynum()
            
        elif choice == "8":
            print(Fore.GREEN + "\n👋 Thank you for using ScayNum!")
            print(Fore.CYAN + "🌐 Visit https://scayar.com for more tools")
            print(Fore.YELLOW + "📱 Join our Telegram: https://t.me/im_scayar")
            break
            
        else:
            print(Fore.RED + "❌ Invalid option. Please select 1-8")
        
        # Ask if user wants to continue
        if choice in ["1", "2", "3", "4", "5", "6"]:
            print(Fore.YELLOW + "\n" + "="*60)
            continue_choice = input(Fore.CYAN + "🔄 Continue with another search? (y/n): " + Style.RESET_ALL).lower().strip()
            if continue_choice not in ['y', 'yes']:
                print(Fore.GREEN + "\n👋 Thank you for using ScayNum!")
                print(Fore.CYAN + "🌐 Visit https://scayar.com for more tools")
                print(Fore.YELLOW + "📱 Join our Telegram: https://t.me/im_scayar")
                break

if __name__ == "__main__":
    main() 