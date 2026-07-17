import os
import shutil
import urllib.request
import re

# Setup paths
base_dir = '/home/pavan/Desktop/project-1'
docs_dir = os.path.join(base_dir, 'docs')
static_src = os.path.join(base_dir, 'static')
static_dest = os.path.join(docs_dir, 'static')

def build():
    print("Building static site for GitHub Pages...")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # Copy static files
    if os.path.exists(static_dest):
        shutil.rmtree(static_dest)
    shutil.copytree(static_src, static_dest)

    # 1. Fetch Home Page
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/')
        index_html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching from local server: {e}")
        return

    # Extract all job IDs to build detail pages
    job_ids = set(re.findall(r'href="/job/(\d+)/"', index_html))
    print(f"Found {len(job_ids)} job links to build...")

    # Fix paths in index.html (Make absolute paths relative for GitHub Pages)
    # /static/ -> static/
    index_html = index_html.replace('href="/static/', 'href="static/')
    index_html = index_html.replace('src="/static/', 'src="static/')
    # /job/1/ -> job/1/
    index_html = re.sub(r'href="/job/(\d+)/"', r'href="job/\1/"', index_html)
    # Disable search and filter forms for static demo
    alert_script = 'href="#" onclick="alert(\'This is a static portfolio demo! To experience real-time MySQL database filtering by state or category, please run the full Django backend locally or deploy to Render.\'); return false;"'
    index_html = re.sub(r'href="/\?category=[^"]+"', alert_script, index_html)
    index_html = re.sub(r'href="/\?q=[^"]+"', alert_script, index_html)
    index_html = index_html.replace('action="/?"', 'action="#" onsubmit="alert(\'Search requires the Python backend!\'); return false;"')
    index_html = index_html.replace('action="/', 'action="#" onsubmit="alert(\'Search requires the Python backend!\'); return false;"')

    # Save index.html
    with open(os.path.join(docs_dir, 'index.html'), 'w') as f:
        f.write(index_html)

    # 2. Build Detail Pages
    for job_id in job_ids:
        try:
            res = urllib.request.urlopen(f'http://127.0.0.1:8000/job/{job_id}/')
            detail_html = res.read().decode('utf-8')
            
            # Fix paths for detail pages (they are 2 levels deep: /job/1/)
            # /static/ -> ../../static/
            detail_html = detail_html.replace('href="/static/', 'href="../../static/')
            detail_html = detail_html.replace('src="/static/', 'src="../../static/')
            # / -> ../../ (Home link)
            detail_html = detail_html.replace('href="/"', 'href="../../"')
            
            # Create folder and save
            job_dir = os.path.join(docs_dir, 'job', job_id)
            os.makedirs(job_dir, exist_ok=True)
            with open(os.path.join(job_dir, 'index.html'), 'w') as f:
                f.write(detail_html)
        except Exception as e:
            print(f"Failed to build job {job_id}: {e}")

    print("Static build successful! The entire site is now in docs/")

if __name__ == '__main__':
    build()
