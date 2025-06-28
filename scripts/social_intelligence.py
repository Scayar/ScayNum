# Imports
import instaloader
import re
from fpdf import FPDF
from PIL import Image
import os
from colorama import Fore, Style, init
from tabulate import tabulate
from jinja2 import Template
import datetime
import csv
import time
from collections import Counter
import random

init(autoreset=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Instagram Report for {{ username }}</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; color: #222; }
        .container { background: #fff; max-width: 700px; margin: 40px auto; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px #ccc; }
        h1 { color: #e1306c; }
        .profile-pic { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 3px solid #e1306c; }
        .section { margin-top: 30px; }
        .posts img { width: 120px; border-radius: 8px; margin-right: 10px; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .table th, .table td { border: 1px solid #eee; padding: 8px; text-align: left; }
        .table th { background: #f2f2f2; }
        .summary { background: #e1306c; color: #fff; padding: 10px; border-radius: 8px; margin-top: 20px; }
        .hashtags { background: #f0f0f0; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .engagement { background: #4CAF50; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
        .warning { background: #ff9800; color: #fff; padding: 10px; border-radius: 8px; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Instagram Report for {{ username }}</h1>
    <img src="{{ profile_pic }}" class="profile-pic" alt="Profile Picture">
    <div class="section">
        <b>Full Name:</b> {{ full_name }}<br>
        <b>Bio:</b> {{ bio }}<br>
        <b>Followers:</b> {{ followers }}<br>
        <b>Following:</b> {{ following }}<br>
        <b>Is Private:</b> {{ is_private }}<br>
        <b>Is Verified:</b> {{ is_verified }}<br>
        <b>Links in bio:</b> {{ links }}<br>
        <b>Emails in bio:</b> {{ emails }}<br>
        <b>Phones in bio:</b> {{ phones }}<br>
        <div class="engagement">
            <b>Engagement Rate:</b> {{ engagement_rate }}%<br>
            <b>Average Likes:</b> {{ avg_likes }}<br>
            <b>Average Comments:</b> {{ avg_comments }}
        </div>
        <div class="hashtags">
            <b>Top Hashtags:</b> {{ top_hashtags }}
        </div>
        {% if warnings %}
        <div class="warning">
            <b>Warnings:</b> {{ warnings }}
        </div>
        {% endif %}
    </div>
    <div class="section posts">
        <h2>Last 3 Posts</h2>
        {% for post in posts %}
            <div style="margin-bottom: 10px;">
                <img src="{{ post.img_path }}" alt="Post Image">
                <b>Date:</b> {{ post.date }}<br>
                <b>Likes:</b> {{ post.likes }}<br>
                <b>Comments:</b> {{ post.comments }}<br>
                <b>Caption:</b> {{ post.caption }}<br>
                <b>Hashtags:</b> {{ post.hashtags }}<br>
            </div>
        {% endfor %}
    </div>
    <div class="section summary">
        <b>Summary:</b> {{ summary }}
    </div>
    <div class="section">
        <b>Report generated at:</b> {{ now }}
    </div>
</div>
</body>
</html>
'''

def filter_latin(text):
    # Remove all non-latin-1 characters (for FPDF)
    if not text:
        return ''
    return text.encode('latin-1', 'ignore').decode('latin-1')

def extract_hashtags(text):
    if not text:
        return []
    return re.findall(r'#\w+', text)

def calculate_engagement_rate(followers, avg_likes, avg_comments):
    if followers == 0:
        return 0
    return round(((avg_likes + avg_comments) / followers) * 100, 2)

def create_user_folder(username):
    # Create folder with format "username_results"
    folder_name = f"{username}_results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def safe_download_with_retry(loader, profile, target_folder, max_retries=3):
    """Safely download profile picture with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            loader.download_profilepic(profile, target=target_folder)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(Fore.YELLOW + f"Attempt {attempt + 1} failed, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                print(Fore.RED + f"Failed after {max_retries} attempts: {e}")
                return False

def safe_get_posts_with_retry(profile, max_retries=3):
    """Safely get posts with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(2, 5))
            return list(profile.get_posts())[:3]
        except Exception as e:
            if attempt < max_retries - 1:
                print(Fore.YELLOW + f"Attempt {attempt + 1} failed, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                print(Fore.RED + f"Failed to fetch posts after {max_retries} attempts: {e}")
                return []

class SearchInsta:
    def __init__(self, username) -> None:
        self.username = username
        self.lookup()
    
    def lookup(self):
        # Configure instaloader with better settings
        L = instaloader.Instaloader(
            download_pictures=False,  # Don't download pictures by default
            download_videos=False,    # Don't download videos by default
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3,
            request_timeout=30
        )
        
        login = input(Fore.YELLOW + "Do you want to login to Instagram for private accounts? (y/n): " + Style.RESET_ALL).lower()
        if login == 'y':
            user = input(Fore.CYAN + "Enter your Instagram username: " + Style.RESET_ALL)
            pwd = input(Fore.CYAN + "Enter your Instagram password: " + Style.RESET_ALL)
            try:
                print(Fore.YELLOW + "Attempting to login...")
                L.login(user, pwd)
                print(Fore.GREEN + "Login successful!")
            except instaloader.exceptions.TwoFactorAuthRequiredException:
                print(Fore.YELLOW + "Two-factor authentication required.")
                code = input(Fore.CYAN + "Enter the 2FA authentication code sent to your device: " + Style.RESET_ALL)
                try:
                    L.two_factor_login(code)
                    print(Fore.GREEN + "2FA login successful!")
                except Exception as e:
                    print(Fore.RED + f"2FA failed: {e}")
                    return
            except Exception as e:
                print(Fore.RED + f"Login failed: {e}")
                print(Fore.YELLOW + "Continuing without login (some features may be limited)...")
        
        # Create user folder
        user_folder = create_user_folder(self.username)
        print(Fore.GREEN + f"\n📁 Created folder: {user_folder}")
        
        try:
            print(Fore.YELLOW + "Fetching profile information...")
            profile = instaloader.Profile.from_username(L.context, self.username)
            print(Fore.MAGENTA + "\n========== Instagram Lookup Results ==========")
            print(Fore.CYAN + f"Username: {profile.username}")
            print(Fore.CYAN + f"Full Name: {profile.full_name}")
            print(Fore.CYAN + f"Bio: {profile.biography}")
            print(Fore.YELLOW + f"Followers: {profile.followers}")
            print(Fore.YELLOW + f"Following: {profile.followees}")
            print(Fore.GREEN + f"Is Private: {profile.is_private}")
            print(Fore.GREEN + f"Is Verified: {profile.is_verified}")
            print(Fore.CYAN + f"Profile Pic URL: {profile.profile_pic_url}")

            # Download profile picture to user folder with retry mechanism
            pic_path = os.path.join(user_folder, f"{self.username}_profile_pic.jpg")
            print(Fore.YELLOW + "Downloading profile picture...")
            if safe_download_with_retry(L, profile, user_folder):
                print(Fore.GREEN + f"📸 Profile picture saved as {pic_path}")
            else:
                print(Fore.RED + "Could not download profile picture (Instagram may be blocking requests).")
                pic_path = None

            # Last 3 posts with retry mechanism
            posts = []
            post_data = []
            all_hashtags = []
            total_likes = 0
            total_comments = 0
            post_count = 0
            warnings = []
            
            print(Fore.YELLOW + "Fetching posts...")
            posts = safe_get_posts_with_retry(profile)
            
            if not posts:
                warnings.append("Could not fetch posts - Instagram may be blocking requests or login required for private accounts.")
                print(Fore.RED + "Could not fetch posts (Instagram may be blocking requests or login required for private accounts).")
            else:
                for idx, post in enumerate(posts, 1):
                    print(Fore.MAGENTA + f"\nPost #{idx}:")
                    print(Fore.YELLOW + f"  Date: {post.date}")
                    print(Fore.YELLOW + f"  Likes: {post.likes}")
                    print(Fore.YELLOW + f"  Comments: {post.comments}")
                    print(Fore.CYAN + f"  Caption: {post.caption[:100] if post.caption else ''}")
                    
                    # Extract hashtags from post
                    post_hashtags = extract_hashtags(post.caption) if post.caption else []
                    all_hashtags.extend(post_hashtags)
                    print(Fore.BLUE + f"  Hashtags: {post_hashtags}")
                    
                    total_likes += post.likes
                    total_comments += post.comments
                    post_count += 1
                    
                    post_img_path = os.path.join(user_folder, f"{self.username}_post{idx}.jpg")
                    try:
                        # Add delay before downloading post
                        time.sleep(random.uniform(1, 2))
                        L.download_post(post, target=user_folder)
                        print(Fore.GREEN + f"  📸 Post image saved")
                    except Exception as e:
                        print(Fore.RED + f"  Could not download post image: {e}")
                        post_img_path = None
                        
                    post_data.append({
                        'date': post.date,
                        'likes': post.likes,
                        'comments': post.comments,
                        'caption': post.caption,
                        'hashtags': post_hashtags,
                        'img_path': post_img_path
                    })

            # Calculate engagement metrics
            avg_likes = total_likes // post_count if post_count > 0 else 0
            avg_comments = total_comments // post_count if post_count > 0 else 0
            engagement_rate = calculate_engagement_rate(profile.followers, avg_likes, avg_comments)
            
            print(Fore.LIGHTGREEN_EX + f"\n=== ENGAGEMENT ANALYTICS ===")
            print(Fore.LIGHTGREEN_EX + f"Average Likes: {avg_likes}")
            print(Fore.LIGHTGREEN_EX + f"Average Comments: {avg_comments}")
            print(Fore.LIGHTGREEN_EX + f"Engagement Rate: {engagement_rate}%")

            # Extract links/emails/phones from bio
            links = re.findall(r'(https?://\S+)', profile.biography)
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', profile.biography)
            phones = re.findall(r'\+?\d[\d\s\-]{7,}\d', profile.biography)
            bio_hashtags = extract_hashtags(profile.biography)
            all_hashtags.extend(bio_hashtags)
            
            print(Fore.BLUE + f"\nLinks in bio: {links}")
            print(Fore.BLUE + f"Emails in bio: {emails}")
            print(Fore.BLUE + f"Phones in bio: {phones}")
            print(Fore.BLUE + f"Hashtags in bio: {bio_hashtags}")

            # Hashtag analysis
            hashtag_counts = Counter(all_hashtags)
            top_hashtags = [tag for tag, count in hashtag_counts.most_common(5)]
            print(Fore.LIGHTMAGENTA_EX + f"\n=== HASHTAG ANALYSIS ===")
            print(Fore.LIGHTMAGENTA_EX + f"Top hashtags: {top_hashtags}")
            print(Fore.LIGHTMAGENTA_EX + f"Total hashtags used: {len(all_hashtags)}")

            # Activity analysis
            freq = 'N/A'
            last_post = 'N/A'
            if post_data:
                dates = [p['date'] for p in post_data if p['date']]
                if len(dates) > 1:
                    freq = (dates[0] - dates[-1]).days / max(len(dates)-1,1)
                last_post = dates[0] if dates else 'N/A'
                print(Fore.GREEN + f"\nPosting frequency: {freq} days/post")
                print(Fore.GREEN + f"Last post date: {last_post}")
            else:
                print(Fore.RED + "No posts found.")

            # Fake account detection (simple)
            fake_score = 0
            if profile.followers < 50 and profile.followees > 500:
                fake_score += 1
            if not profile.profile_pic_url:
                fake_score += 1
            if profile.is_private and profile.followers < 20:
                fake_score += 1
            print(Fore.LIGHTRED_EX + f"\nFake account suspicion score: {fake_score}/3 (higher = more suspicious)")

            # Smart summary
            summary = []
            if fake_score == 0:
                summary.append("This account appears genuine.")
            elif fake_score == 1:
                summary.append("Some suspicious signs detected.")
            else:
                summary.append("This account may be fake or a bot.")
            if freq != 'N/A' and isinstance(freq, (int, float)):
                if freq < 2:
                    summary.append("Very active account.")
                elif freq < 7:
                    summary.append("Moderately active account.")
                else:
                    summary.append("Rarely posts.")
            if profile.is_verified:
                summary.append("Verified account.")
            if profile.is_private:
                summary.append("Private account.")
            if engagement_rate > 5:
                summary.append("High engagement rate.")
            elif engagement_rate > 2:
                summary.append("Moderate engagement rate.")
            else:
                summary.append("Low engagement rate.")
            print(Fore.LIGHTMAGENTA_EX + f"\nSummary: {' '.join(summary)}")

            # Table output for posts
            if post_data:
                table = [[idx+1, p['date'], p['likes'], p['comments'], (p['caption'][:40] + '...') if p['caption'] else '', len(p['hashtags'])] for idx, p in enumerate(post_data)]
                print(Fore.LIGHTCYAN_EX + tabulate(table, headers=["#", "Date", "Likes", "Comments", "Caption", "Hashtags"], tablefmt="fancy_grid"))

            # Export to CSV in user folder
            csv_filename = os.path.join(user_folder, f"{self.username}_analytics.csv")
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Username', profile.username])
                writer.writerow(['Full Name', profile.full_name])
                writer.writerow(['Followers', profile.followers])
                writer.writerow(['Following', profile.followees])
                writer.writerow(['Is Private', profile.is_private])
                writer.writerow(['Is Verified', profile.is_verified])
                writer.writerow(['Engagement Rate', f"{engagement_rate}%"])
                writer.writerow(['Average Likes', avg_likes])
                writer.writerow(['Average Comments', avg_comments])
                writer.writerow(['Fake Score', fake_score])
                writer.writerow(['Top Hashtags', ', '.join(top_hashtags)])
                writer.writerow(['Total Hashtags', len(all_hashtags)])
                writer.writerow(['Links in Bio', ', '.join(links)])
                writer.writerow(['Emails in Bio', ', '.join(emails)])
                writer.writerow(['Phones in Bio', ', '.join(phones)])
                if warnings:
                    writer.writerow(['Warnings', '; '.join(warnings)])
            print(Fore.GREEN + f"📊 CSV analytics saved as {csv_filename}")

            # Export to PDF in user folder
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=filter_latin(f"Instagram Report for {profile.username}"), ln=True, align='C')
            pdf.cell(200, 10, txt=filter_latin(f"Full Name: {profile.full_name}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Bio: {profile.biography}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Followers: {profile.followers}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Following: {profile.followees}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Is Private: {profile.is_private}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Is Verified: {profile.is_verified}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Engagement Rate: {engagement_rate}%"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Average Likes: {avg_likes}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Average Comments: {avg_comments}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Profile Pic URL: {profile.profile_pic_url}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Links in bio: {links}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Emails in bio: {emails}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Phones in bio: {phones}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Top Hashtags: {top_hashtags}"), ln=True)
            if post_data:
                pdf.cell(200, 10, txt=filter_latin(f"Posting frequency: {freq} days/post"), ln=True)
                pdf.cell(200, 10, txt=filter_latin(f"Last post date: {last_post}"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Fake account suspicion score: {fake_score}/3"), ln=True)
            pdf.cell(200, 10, txt=filter_latin(f"Summary: {' '.join(summary)}"), ln=True)
            if warnings:
                pdf.cell(200, 10, txt=filter_latin(f"Warnings: {'; '.join(warnings)}"), ln=True)
            if pic_path and os.path.exists(pic_path):
                pdf.image(pic_path, x=10, y=pdf.get_y(), w=30)
                pdf.ln(35)
            for idx, pdata in enumerate(post_data, 1):
                if pdata['img_path'] and os.path.exists(pdata['img_path']):
                    pdf.cell(200, 10, txt=filter_latin(f"Post #{idx}"), ln=True)
                    pdf.image(pdata['img_path'], x=10, y=pdf.get_y(), w=30)
                    pdf.ln(35)
            pdf_path = os.path.join(user_folder, f"{self.username}_report.pdf")
            pdf.output(pdf_path)
            print(Fore.GREEN + f"📄 PDF report saved as {pdf_path}")

            # Export to HTML in user folder
            html = Template(HTML_TEMPLATE).render(
                username=profile.username,
                full_name=profile.full_name,
                bio=profile.biography,
                followers=profile.followers,
                following=profile.followees,
                is_private=profile.is_private,
                is_verified=profile.is_verified,
                engagement_rate=engagement_rate,
                avg_likes=avg_likes,
                avg_comments=avg_comments,
                profile_pic=pic_path if pic_path and os.path.exists(pic_path) else profile.profile_pic_url,
                links=links,
                emails=emails,
                phones=phones,
                top_hashtags=top_hashtags,
                posts=[{
                    'date': str(p['date']),
                    'likes': p['likes'],
                    'comments': p['comments'],
                    'caption': p['caption'],
                    'hashtags': p['hashtags'],
                    'img_path': p['img_path'] if p['img_path'] and os.path.exists(p['img_path']) else ''
                } for p in post_data],
                summary=' '.join(summary),
                warnings='; '.join(warnings) if warnings else None,
                now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            html_path = os.path.join(user_folder, f"{self.username}_report.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(Fore.GREEN + f"🌐 HTML report saved as {html_path}")
            
            print(Fore.LIGHTGREEN_EX + f"\n📁 All files saved in folder: {user_folder}")
            if warnings:
                print(Fore.YELLOW + f"⚠️  Warnings: {'; '.join(warnings)}")
            print(Fore.LIGHTGREEN_EX + "\n========== Search Completed! ==========")
        except Exception as e:
            print(Fore.RED + f"Error: {e}. Unable to make a request to Instagram.")
            print(Fore.YELLOW + "This may be due to Instagram's rate limiting or anti-bot measures.")
            print(Fore.YELLOW + "Try again later or use a different account for login.")

