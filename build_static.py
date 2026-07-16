import os
import django
from django.conf import settings
from django.test import Client
import shutil

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

def build():
    # Create docs directory
    base_dir = settings.BASE_DIR
    docs_dir = os.path.join(base_dir, 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # Copy static files
    static_src = os.path.join(base_dir, 'static')
    static_dest = os.path.join(docs_dir, 'static')
    if os.path.exists(static_dest):
        shutil.rmtree(static_dest)
    shutil.copytree(static_src, static_dest)

    # Render home page using urllib (since the server is already running on 8000)
    import urllib.request
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/')
        html_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching from local server (is it running?): {e}")
        return

    # Fix static paths for GitHub pages (relative)
    html_content = html_content.replace('href="/static/', 'href="static/')
    html_content = html_content.replace('src="/static/', 'src="static/')
    
    # Also fix the links in the UI so they don't break or just point to #
    import re
    html_content = re.sub(r'href="/jobs/\d+/"', 'href="#"', html_content)
    html_content = re.sub(r'href="\?category=[^"]+"', 'href="#"', html_content)
    html_content = re.sub(r'href="\?q=[^"]+"', 'href="#"', html_content)

    # Write index.html
    with open(os.path.join(docs_dir, 'index.html'), 'w') as f:
        f.write(html_content)

    print("Static build successful! Files in docs/")

if __name__ == '__main__':
    build()
