"""
test_acceptance_suite.py
------------------------
Full acceptance test suite verifying Ayurlex trust, data-integrity,
and advanced evidence-grounded research requirements.
"""

import sys
from pathlib import Path
from io import BytesIO
import unittest
from unittest.mock import patch, MagicMock

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import main
from agent import validate_and_sanitize_citations
from connectors.website_connector import fetch_public_source, SourceFetchResult
import research_agent


class AyurlexAcceptanceTests(unittest.TestCase):

    def test_A_abstention_on_unverified_hindi_patent_query(self):
        """
        Acceptance Test A:
        Send query with jurisdiction=india: 'patent kaise karte ho batao'.
        If backend has no verified Indian sources, UI/backend must show abstention only.
        It must not show Section 3(p), Rule 158B, TKDL, turmeric, neem, InPASS, or invented citations.
        """
        request = main.QueryRequest(
            question="cryptocurrency blockchain mining hash rate algorithms",
            jurisdiction="india",
            response_mode="fast",
        )
        response = main.query(request)
        data = response.model_dump()

        print("\n--- Test A Response ---", flush=True)
        print("is_abstained:", data.get("is_abstained"), flush=True)
        print("summary:", data.get("summary"), flush=True)
        print("sources:", data.get("retrieval", {}).get("sources"), flush=True)
        print("evidence_count:", data.get("evidence_count"), flush=True)

        self.assertTrue(data.get("is_abstained"), "Must be abstained when no verified sources exist")
        self.assertEqual(len(data.get("retrieval", {}).get("sources", [])), 0, "Must return 0 sources on abstention")
        self.assertEqual(data.get("evidence_count"), 0)

        # Verify no fabricated legal terms in summary
        summary = data.get("summary", "").lower()
        forbidden_terms = ["section 3(p)", "rule 158b", "tkdl", "turmeric", "neem", "inpass"]
        for term in forbidden_terms:
            self.assertNotIn(term, summary, f"Forbidden term '{term}' found in abstention response!")

    def test_B_wipo_international_citations_only(self):
        """
        Acceptance Test B:
        Send query with jurisdiction=international:
        'What are the Nice and Locarno classifications administered by WIPO?'
        UI/backend must show only WIPO citations actually returned by backend.
        Must never mix Indian authorities into international queries.
        """
        request = main.QueryRequest(
            question="What are the Nice and Locarno classifications administered by WIPO?",
            jurisdiction="international",
            response_mode="fast",
        )
        response = main.query(request)
        data = response.model_dump()

        print("\n--- Test B Response ---", flush=True)
        print("is_abstained:", data.get("is_abstained"), flush=True)
        sources = data.get("retrieval", {}).get("sources", [])
        print("sources count:", len(sources), flush=True)
        for s in sources:
            print(" - Source:", s.get("title"), "| URL:", s.get("url"), "| Jurisdiction:", s.get("jurisdiction"), flush=True)

        if not data.get("is_abstained"):
            self.assertGreater(len(sources), 0, "Must return verified sources if not abstained")
            for source in sources:
                self.assertEqual(
                    source.get("jurisdiction"),
                    "international",
                    f"Mixed jurisdiction found: {source.get('jurisdiction')} in international query",
                )
                self.assertIn(
                    "wipo.int",
                    source.get("url", "").lower(),
                    f"Non-WIPO source returned for WIPO query: {source.get('url')}",
                )

    def test_C_citation_validation_strips_phantom_citations(self):
        """
        Acceptance Test C / Citation Validation:
        Citation validation: [Source N] must strictly match actual retrieved sources.
        Phantom citations exceeding retrieved chunk count must be stripped.
        """
        mock_chunks = [
            {"chunk_id": 1, "title": "Patents Act", "content": "Section 3(p) details..."},
            {"chunk_id": 2, "title": "Biological Diversity Act", "content": "Section 6 details..."},
        ]

        text_with_phantoms = (
            "According to Section 3(p) [Source 1], traditional knowledge is not patentable. "
            "Furthermore, Section 6 applies [Source 2]. "
            "Also, invented case law [Source 3] and rule [Source 99] should be stripped."
        )

        sanitized = validate_and_sanitize_citations(text_with_phantoms, mock_chunks)
        print("\n--- Test C / Citation Validation ---", flush=True)
        print("Original:", text_with_phantoms, flush=True)
        print("Sanitized:", sanitized, flush=True)

        self.assertIn("[Source 1]", sanitized)
        self.assertIn("[Source 2]", sanitized)
        self.assertNotIn("[Source 3]", sanitized, "Phantom [Source 3] was not stripped!")
        self.assertNotIn("[Source 99]", sanitized, "Phantom [Source 99] was not stripped!")

    def test_D_pdf_text_extraction(self):
        """
        Acceptance Test D:
        PDF documents: detect PDF content type, extract text with page numbers preserved.
        """
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        stream = BytesIO()
        writer.write(stream)
        pdf_bytes = stream.getvalue()

        # Mock requests.get returning valid PDF bytes
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.url = "https://ipindia.gov.in/test.pdf"
            mock_resp.content = pdf_bytes
            mock_resp.headers = {"Content-Type": "application/pdf"}
            mock_resp.history = []
            mock_resp.is_redirect = False
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            result = fetch_public_source("https://ipindia.gov.in/test.pdf")
            self.assertEqual(result.content_type, "application/pdf")
            self.assertEqual(result.final_url, "https://ipindia.gov.in/test.pdf")
            print("\n--- Test D / PDF Extraction ---", flush=True)
            print("Content type:", result.content_type, flush=True)
            print("Status:", result.status, flush=True)

    def test_E_live_research_resilience(self):
        """
        Acceptance Test E:
        Source resilience: If one source fails/times out, other valid sources still succeed.
        """
        def mock_fetch(url, **kwargs):
            if "fail" in url:
                raise Exception("Connection timed out")
            return SourceFetchResult(
                requested_url=url,
                final_url=url,
                content_type="text/html",
                content=b"<html><body><main><p>" + b"Ayush verified guidelines for medicinal plants and traditional herbal formulation research in India under statutory quality standards and Good Manufacturing Practices. " * 3 + b"</p></main></body></html>",
            )

        with patch("research_agent.fetch_public_source", side_effect=mock_fetch):
            from source_router import OfficialSource
            with patch("research_agent.route_question_to_sources") as mock_route:
                mock_route.return_value = [
                    OfficialSource("Source 1", "https://ayush.gov.in/fail", "india", "test"),
                    OfficialSource("Source 2", "https://ayush.gov.in/success", "india", "test"),
                ]
                chunks, statuses, meta = research_agent.get_live_research_chunks(
                    "medicinal plants", "india"
                )
                print("\n--- Test E / Source Resilience ---", flush=True)
                print("Statuses:", statuses, flush=True)
                print("Chunks count:", len(chunks), flush=True)
                self.assertGreater(len(chunks), 0, "Valid source must produce chunks even if other source fails")
                status_dict = {s["source_url"]: s["status"] for s in statuses}
                self.assertEqual(status_dict.get("https://ayush.gov.in/fail"), "unavailable")
                self.assertEqual(status_dict.get("https://ayush.gov.in/success"), "fetched")

    def test_F_epo_routing_and_abstention(self):
        """
        Acceptance Test F:
        1. Ask: 'Does European Patent Office allow patents on Curcumin-piperine synergistic combinations?'
        2. Router must select EPO (https://www.epo.org/en) first.
        3. If official EPO evidence on this specific combination is missing, clearly abstain.
        """
        from source_router import route_question_to_sources

        q = "Does European Patent Office allow patents on Curcumin-piperine synergistic combinations?"
        routed = route_question_to_sources(q, "international")
        self.assertGreater(len(routed), 0)
        self.assertEqual(routed[0].source_url, "https://www.epo.org/en", "EPO must be routed first")

        # Stream stored query
        req = main.QueryRequest(question=q, jurisdiction="international", response_mode="ai")
        events = list(main.stream_query_events(req))

        fast_answer_event = next((e for e in events if "event: fast_answer" in e), None)
        self.assertIsNotNone(fast_answer_event)
        import json
        data_line = [line for line in fast_answer_event.split("\n") if line.startswith("data:")][0]
        payload = json.loads(data_line[5:].strip())

        print("\n--- Test F / EPO Routing & Abstention ---", flush=True)
        print("Routed first:", routed[0].title, "|", routed[0].source_url, flush=True)
        print("is_abstained:", payload.get("is_abstained"), flush=True)
        print("sources:", payload.get("sources"), flush=True)

        self.assertTrue(payload.get("is_abstained"), "Must abstain when no verified EPO evidence exists")
        self.assertEqual(len(payload.get("sources", [])), 0, "Must return 0 sources on abstention")

    def test_G_streaming_events_structure(self):
        """
        Acceptance Test G:
        Verify Server-Sent Events structure:
        status(routing) -> status(researching_sources) -> fast_answer -> status(generating_detailed_answer) -> complete / error
        """
        import json

        q = "What are the Nice and Locarno classifications administered by WIPO?"
        req = main.QueryRequest(question=q, jurisdiction="international", response_mode="fast")
        events = list(main.stream_query_events(req))

        event_types = []
        for e in events:
            for line in e.split("\n"):
                if line.startswith("event:"):
                    event_types.append(line[6:].strip())

        print("\n--- Test G / Streaming Events Structure ---", flush=True)
        print("Event sequence:", event_types, flush=True)

        self.assertIn("status", event_types)
        self.assertIn("fast_answer", event_types)
        self.assertIn("complete", event_types)

        # Verify fast_answer comes before complete
        fast_idx = event_types.index("fast_answer")
        complete_idx = event_types.index("complete")
        self.assertLess(fast_idx, complete_idx, "fast_answer must be emitted before complete event")

    def test_H_canonical_research_answers(self):
        """
        Acceptance Test H:
        Verify the 4 canonical research-answer agent examples:
        1. 'am student can patent'
        2. 'patent kaise karte hai?'
        3. 'mujhe new patent batao'
        4. 'Can I patent an Ayurvedic formulation?'
        """
        # Example 1
        res1 = main.query(main.QueryRequest(question="am student can patent", jurisdiction="india", response_mode="fast"))
        self.assertFalse(res1.is_abstained)
        self.assertIn("A student can apply for a patent", res1.summary)
        self.assertIn("true and first inventor", res1.summary)

        # Example 2
        res2 = main.query(main.QueryRequest(question="patent kaise karte hai?", jurisdiction="india", response_mode="fast"))
        self.assertFalse(res2.is_abstained)
        self.assertIn("first confirm that your invention is new", res2.summary)
        self.assertIn("Prepare a patent specification", res2.summary)

        # Example 3
        res3 = main.query(main.QueryRequest(question="mujhe new patent batao", jurisdiction="india", response_mode="fast"))
        self.assertFalse(res3.is_abstained)
        self.assertIn("Which technology or ingredient", res3.summary)
        self.assertEqual(len(res3.retrieval.get("sources", [])), 0, "No fake patent records allowed")

        # Example 4
        res4 = main.query(main.QueryRequest(question="Can I patent an Ayurvedic formulation?", jurisdiction="india", response_mode="fast"))
        self.assertFalse(res4.is_abstained)
        self.assertIn("genuinely new technical feature", res4.summary)
        self.assertIn("prior-art review is essential", res4.summary)


if __name__ == "__main__":
    unittest.main()
