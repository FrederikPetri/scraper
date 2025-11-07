from scraper import fetch, parse_jobs, DEFAULT_URL
from datetime import datetime

def generate_html() -> str:
    payload = fetch(DEFAULT_URL)
    jobs = parse_jobs(payload)

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'><head><meta charset='UTF-8'><title>Jobindex Report</title></head><body>")
    html.append(f"<h1>Jobindex Report</h1>")
    html.append(f"<p>Fetched {len(jobs)} jobs at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>")
    
    for job in jobs:
        html.append("<hr>")
        html.append(f"<h2>{job.headline}</h2>")
        if job.company:
            html.append(f"<p><strong>Company:</strong> {job.company}</p>")
        if job.area:
            html.append(f"<p><strong>Area:</strong> {job.area}</p>")
        if job.distance_km:
            html.append(f"<p><strong>Distance:</strong> {job.distance_km:.1f} km</p>")
        if job.apply_deadline:
            html.append(f"<p><strong>Deadline:</strong> {job.apply_deadline}</p>")
        if job.apply_url:
            html.append(f"<p><a href='{job.apply_url}'>Apply here</a></p>")
    
    html.append("</body></html>")
    return "\n".join(html)

if __name__ == "__main__":
    html_content = generate_html()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
