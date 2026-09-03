import re
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup


class TrustedWebRetriever:
    """
    Retrieves evidence only from three predefined official SVU pages.
    """

    SOURCES = {
        "university_news": "https://www.svuonline.org/ar/node/506",
        "student_affairs": "https://www.svuonline.org/ar/node/231",
        "thesis_defenses": "https://www.svuonline.org/ar/node/3641",
    }

    KEYWORDS = {
        "student_affairs": [
            "أخبار شؤون الطلاب",
            "أخبار شؤون الطلبة",
            "student affairs news",
            "students affairs news",
        ],
        "thesis_defenses": [
            "أخبار مناقشة رسائل الماجستير والدكتوراه",
            "أخبار مناقشة رسائل الماجستير",
            "أخبار مناقشة رسائل الدكتوراه",
            "master thesis defense news",
            "doctoral thesis defense news",
        ],
        "university_news": [
            "أخبار الجامعة",
            "آخر أخبار الجامعة",
            "أخبار الجامعة اليوم",
            "university news",
            "latest university news",
        ],
    }

    def __init__(self, trusted_domain: str = "svuonline.org"):
        self.trusted_domain = trusted_domain
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def _clean_evidence(self, text: str) -> str:
        if not text:
            return ""

        cleaned = re.sub(r"https?://\S+", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def detect_web_intent(self, query: str) -> str:
        """
        Detects Web Intent based on strict keywords and normalized forms.
        """
        query_lower = query.lower().strip()

        # Remove common punctuation
        normalized_query = re.sub(r"['?؟!.,]", "", query_lower)
        normalized_query = re.sub(r"\s+", " ", normalized_query).strip()

        # English Intent Normalization
        normalized_query = re.sub(r"\bmasters?(?:'s)?\b", "master", normalized_query)
        normalized_query = re.sub(
            r"\b(doctoral|doctorate|phd)\b",
            "doctoral",
            normalized_query,
        )
        normalized_query = re.sub(
            r"\b(defenses|defence|defences)\b",
            "defense",
            normalized_query,
        )
        normalized_query = re.sub(
            r"\b(recent|latest|newest)\b",
            "latest",
            normalized_query,
        )

        # Arabic Intent Normalization
        arabic_normalized = normalized_query

        # Removal of common Arabic question prefixes (Fixed \\s+ to \s+)
        arabic_normalized = re.sub(
            r"^(?:ما هي|ما هو|ما آخر|ما هي آخر|ما هي أحدث)\s+",
            "",
            arabic_normalized,
        )

        # Normalize Arabic synonyms directly in UTF-8
        arabic_normalized = arabic_normalized.replace("أحدث", "آخر")
        arabic_normalized = arabic_normalized.replace("مستجدات", "أخبار")
        arabic_normalized = arabic_normalized.replace("مناقشات", "مناقشة")

        # 1. Student Affairs Intent
        student_affairs_terms = [
            "أخبار شؤون الطلاب",
            "أخبار شؤون الطلبة",
            "آخر أخبار شؤون الطلاب",
            "آخر أخبار شؤون الطلبة",
            "شؤون الطلاب",
            "شؤون الطلبة",
            "latest student affairs news",
            "recent student affairs news",
            "latest news about student affairs",
            "student affairs",
        ]

        if any(term in arabic_normalized or term in normalized_query for term in student_affairs_terms):
            return "student_affairs"

        # 2. Thesis Defenses Intent
        if (
            "مناقش" in arabic_normalized
            and "ماجستير" in arabic_normalized
            and "دكتوراه" in arabic_normalized
        ):
            return "thesis_defenses"

        thesis_terms = [
            "أخبار مناقشة رسائل الماجستير والدكتوراه",
            "أخبار مناقشة رسائل الماجستير",
            "أخبار مناقشة رسائل الدكتوراه",
            "آخر أخبار مناقشة رسائل الماجستير والدكتوراه",
            "master thesis defense news",
            "doctoral thesis defense news",
            "master thesis defense",
            "doctoral thesis defense",
            "master and doctoral thesis defense",
            "thesis defense news",
            "latest news about master and doctoral thesis defenses",
        ]

        if any(term in normalized_query or term in arabic_normalized for term in thesis_terms):
            return "thesis_defenses"

        arabic_thesis_core_terms = ["أخبار مناقشة", "آخر أخبار مناقشة"]
        if any(term in arabic_normalized for term in arabic_thesis_core_terms):
            if "الماجستير" in arabic_normalized or "الدكتوراه" in arabic_normalized:
                return "thesis_defenses"

        # 3. University News Intent
        university_news_terms = [
            "أخبار الجامعة",
            "آخر أخبار الجامعة",
            "ما الجديد في الجامعة",
            "latest university news",
            "recent university news",
            "latest news from the university",
            "what's new at the university",
        ]

        if any(term in normalized_query or term in arabic_normalized for term in university_news_terms):
            return "university_news"

        return ""

    def _select_source(self, query: str) -> str:
        intent = self.detect_web_intent(query)

        if not intent:
            return ""

        return self.SOURCES[intent]

    def _extract_page_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        text = soup.get_text(" ", strip=True)
        return self._clean_evidence(text)

    def search_trusted_web(self, query: str) -> str:
        source_url = self._select_source(query)

        if not source_url:
            print("[Web Retriever] No matching SVU Web Intent. Web search skipped.")
            return ""

        try:
            response = self.session.get(source_url, timeout=20)
            response.raise_for_status()

            page_text = self._extract_page_text(response.text)

            if len(page_text) < 30:
                return ""

            return page_text[:12000]

        except Exception as e:
            print(f"[Web Retriever Error]: {e}")
            return ""

    def search_trusted_site(self, query: str) -> str:
        return self.search_trusted_web(query)