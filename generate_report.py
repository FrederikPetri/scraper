import io
from scraper import fetch, parse_jobs, print_jobs, DEFAULT_URL

def generate_markdown() -> str:
    payload = fetch(DEFAULT_URL)
    jobs = parse_jobs(payload)
    buffer = io.StringIO()
    buffer.write(f"# Jobindex Results\n\n")
    buffer.write(f"Fetched {len(jobs)} jobs.\n\n")
    for job in jobs:
        buffer.write(f"## {job.headline}\n")
        if job.company:
            buffer.write(f"**Company:** {job.company}\n\n")
        if job.area:
            buffer.write(f"**Area:** {job.area}\n\n")
        if job.distance_km:
            buffer.write(f"**Distance:** {job.distance_km:.1f} km\n\n")
        if job.apply_deadline:
            buffer.write(f"**Deadline:** {job.apply_deadline}\n\n")
        if job.apply_url:
            buffer.write(f"[Apply here]({job.apply_url})\n\n")
        buffer.write("---\n")
    return buffer.getvalue()

if __name__ == "__main__":
    md = generate_markdown()
    with open("index.md", "w", encoding="utf-8") as f:
        f.write(md)
