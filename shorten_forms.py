import urllib.request
import urllib.parse

forms = [
    {
        'name': 'Video Perkenalan',
        'url': 'https://docs.google.com/forms/d/12z6WvOoDwZ0iKpOMhAxmIjDuZmXhdb8zneXuRIJ13w0/viewform',
        'alias': 'VideoPerkenalanOKK2026'
    },
    {
        'name': 'Twibbon',
        'url': 'https://docs.google.com/forms/d/146uM7_rORZEUSnvRmKkBfc8Z2tlthIih46hwSJkyzS0/viewform',
        'alias': 'TwibbonOKK2026'
    }
]

for f in forms:
    # Test if form is accessible
    try:
        req = urllib.request.Request(f['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            if res.status == 200:
                print(f"{f['name']}: URL is valid.")
    except Exception as e:
        print(f"{f['name']} ERROR checking URL: {e}")

    # Shorten URL
    api_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(f['url'])}&alias={f['alias']}"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            short_url = res.read().decode('utf-8')
            print(f"{f['name']} SHORT URL: {short_url}")
    except Exception as e:
        print(f"{f['name']} ERROR shortening URL: {e}")
