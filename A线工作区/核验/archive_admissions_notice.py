"""Archive public admission evidence without logging in or sending personal data."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / "官方来源"
SOURCES = {
    "2027第一批_20260926": "https://www.westlake.edu.cn/admissions/graduate/brochure/general/202608/t20260813_68957.html",
    "普博列表_20260926": "https://www.westlake.edu.cn/admissions/graduate/brochure/general/",
}


def main():
    ROOT.mkdir(exist_ok=True)
    for name, url in SOURCES.items():
        raw_path = ROOT / f"{name}.html"
        if raw_path.exists():
            raise FileExistsError(raw_path)
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=25) as response:
            raw = response.read()
            final_url = response.url
            status = response.status
        html = raw.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        article = None
        for script in soup.find_all("script"):
            source = script.string or script.get_text()
            marker = "detailContent:"
            if marker in source:
                value, _ = json.JSONDecoder().raw_decode(source.split(marker, 1)[1].lstrip())
                article = BeautifulSoup(value, "html.parser")
                break
        with raw_path.open("xb") as stream:
            stream.write(raw)
        metadata = {"url": url, "final_url": final_url, "retrieved_date_local": "2026-09-26",
                    "http_status": status, "sha256": hashlib.sha256(raw).hexdigest()}
        with (ROOT / f"{name}.json").open("x", encoding="utf-8") as stream:
            json.dump(metadata, stream, ensure_ascii=False, indent=2)
        if article:
            paragraphs = [p.get_text("", strip=True) for p in article.find_all("p")]
            text = "\n\n".join(p for p in paragraphs if p)
            with (ROOT / f"{name}_正文.txt").open("x", encoding="utf-8") as stream:
                stream.write(text)
            print(text)
            print("ARTICLE_LINKS", [(a.get_text(), a.get("href")) for a in article.find_all("a", href=True)])
        else:
            print("LIST_PAGE", len(raw), [(a.get_text("", strip=True), a.get("href"))
                                        for a in soup.find_all("a", href=True)])
        print("ARCHIVED", raw_path, metadata)


if __name__ == "__main__":
    main()
