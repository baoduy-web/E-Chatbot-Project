import json
import re
import ssl
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
}


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.reset()
        self.fed: list[str] = []
        self.ignore: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ["script", "style", "noscript"]:
            self.ignore = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ["script", "style", "noscript"]:
            self.ignore = False
        elif tag in ["p", "br", "div", "h1", "h2", "h3", "h4", "li", "tr"]:
            self.fed.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignore:
            self.fed.append(data)

    def get_text(self) -> str:
        text = "".join(self.fed)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()


def strip_html(html_str: str) -> str:
    extractor = HTMLTextExtractor()
    extractor.feed(html_str)
    return extractor.get_text()


def fetch_url(url: str) -> str | None:
    if not url.startswith("http"):
        url = "https://benhviene.com" + ("/" if not url.startswith("/") else "") + url
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return str(resp.read().decode("utf-8"))
    except (OSError, urllib.error.URLError):
        return None


def fetch_page_content(alias_or_url: str) -> dict[str, object] | None:
    html = fetch_url(alias_or_url)
    if not html:
        return None

    # Check Next.js data
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if m:
        try:
            next_data = json.loads(m.group(1))
            props = next_data.get("props", {}).get("pageProps", {})
            # Look for article or content in pageProps
            for key in ["pageContent", "article", "news", "data", "content"]:
                if key in props and props[key]:
                    return props[key]
            return props
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Fallback: extract title and body text from HTML
    title_m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    title = title_m.group(1) if title_m else ""
    return {"title": title, "raw_text": strip_html(html)}


out_dir = Path("data/hospital_e")
out_dir.mkdir(parents=True, exist_ok=True)
articles_dir = out_dir / "articles"
articles_dir.mkdir(parents=True, exist_ok=True)

TARGET_PAGES = [
    {
        "id": "intro",
        "title": "Giới thiệu chung Bệnh viện E",
        "path": "/trang-noi-dung/gioi-thieu-benh-vien-20200317085545978.html",
        "category": "about",
    },
    {
        "id": "directors",
        "title": "Ban giám đốc Bệnh viện E",
        "path": "/trang-noi-dung/ban-giam-doc-20260123020629981.html",
        "category": "about",
    },
    {
        "id": "hospital_map",
        "title": "Sơ đồ Bệnh viện E",
        "path": "/trang-noi-dung/so-do-benh-vien-20220617055626754",
        "category": "facilities",
    },
    {
        "id": "org_chart",
        "title": "Sơ đồ khoa phòng & Cơ cấu tổ chức",
        "path": "/so-do-khoa-phong",
        "category": "departments",
    },
    {
        "id": "workflow_bhyt",
        "title": "Quy trình khám chữa bệnh BHYT",
        "path": "/trang-noi-dung/quy-trinh-kham-chua-benh-tai-benh-vien-e-20240821012151281.html",
        "category": "workflows",
    },
    {
        "id": "workflow_ondemand",
        "title": "Quy trình khám theo yêu cầu",
        "path": "/trang-noi-dung/quy-trinh-kham-benh-theo-yeu-cau-tai-benh-vien-e-20201014050907241.html",
        "category": "workflows",
    },
    {
        "id": "pricing_general",
        "title": "Bảng giá dịch vụ khám bệnh chữa bệnh BVE",
        "path": "/trang-noi-dung/bang-gia-dich-vu-kham-benh-chua-benh-ap-dung-tai--20250108011439915.html",
        "category": "pricing",
    },
    {
        "id": "pricing_ondemand",
        "title": "Bảng giá dịch vụ khám chữa bệnh theo yêu cầu",
        "path": "/trang-noi-dung/bang-gia-cac-dich-vu-kham-benh-chua-benh-theo-yeu-20250108011558131.html",
        "category": "pricing",
    },
    {
        "id": "pricing_updates_2025",
        "title": "Bổ sung giá và sửa đổi tên giá dịch vụ 2025",
        "path": "/trang-noi-dung/bo-sung-gia-va-sua-doi-ten-gia-ghi-chu-dich-vu-k-20250212041416309.html",
        "category": "pricing",
    },
    {
        "id": "guide_admission",
        "title": "Hướng dẫn nhập viện Bệnh viện E",
        "path": "/trang-noi-dung/huong-dan-nhap-vien-20250107112657842.html",
        "category": "guides",
    },
    {
        "id": "guide_discharge",
        "title": "Hướng dẫn xuất viện Bệnh viện E",
        "path": "/trang-noi-dung/huong-dan-xuat-vien-20250107113056534.html",
        "category": "guides",
    },
    {
        "id": "guide_visiting",
        "title": "Quy định giờ thăm người bệnh nội trú",
        "path": "/trang-noi-dung/quy-dinh-gio-tham-nguoi-benh-dieu-tri-noi-tru-20250413105244587.html",
        "category": "guides",
    },
    {
        "id": "guide_bhyt_vneid",
        "title": "Các hình thức sử dụng thay thế thẻ BHYT giấy (VNeID/VssID)",
        "path": "/trang-noi-dung/cac-hinh-thuc-su-dung-thay-the-the-bao-hiem-y-te-g-20250518041936837.html",
        "category": "guides",
    },
    {
        "id": "guide_medical_records",
        "title": "Thủ tục trích sao hồ sơ bệnh án",
        "path": "/trang-noi-dung/thu-tuc-trich-sao-ho-so-benh-an-20240721102852171.html",
        "category": "guides",
    },
    {
        "id": "dept_rheumatology",
        "title": "Khoa Nội Cơ Xương Khớp",
        "path": "/trang-noi-dung/khoa-noi-co-xuong-khop-20200505052241638.html",
        "category": "departments",
    },
    {
        "id": "health_checkup_work",
        "title": "Khám sức khỏe đi làm, đi học",
        "path": "/trang-noi-dung/kham-cap-giay-chung-nhan-suc-khoe-cho-nguoi-di-lam-20201013032755395.html",
        "category": "services",
    },
    {
        "id": "health_checkup_driving",
        "title": "Khám sức khỏe lái xe",
        "path": "/trang-noi-dung/kham-cap-giay-suc-khoe-lam-(doi)-giay-phep-lai-xe-20201013044006104.html",
        "category": "services",
    },
]

scraped_manifest = []

for item in TARGET_PAGES:
    time.sleep(0.5)
    data = fetch_page_content(item["path"])
    if data:
        # Save JSON
        json_path = out_dir / f"{item['id']}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "url": f"https://benhviene.com{item['path']}",
                    "category": item["category"],
                    "content": data,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        # Save readable markdown article
        md_path = articles_dir / f"{item['id']}.md"
        content_text = ""
        if isinstance(data, dict):
            if "content" in data and isinstance(data["content"], str):
                content_text = strip_html(data["content"])
            elif "raw_text" in data:
                content_text = str(data["raw_text"])

            else:
                content_text = json.dumps(data, ensure_ascii=False, indent=2)
        elif isinstance(data, str):
            content_text = strip_html(data)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {item['title']}\n\n")
            f.write(f"- Nguồn: https://benhviene.com{item['path']}\n")
            f.write(f"- Phân loại: {item['category']}\n\n")
            f.write(content_text)

        scraped_manifest.append(
            {
                "id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "json_path": str(json_path),
                "md_path": str(md_path),
                "content_length": len(content_text),
            }
        )

with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(scraped_manifest, f, ensure_ascii=False, indent=2)

print(f"Scraped {len(scraped_manifest)} pages successfully into {out_dir}")
