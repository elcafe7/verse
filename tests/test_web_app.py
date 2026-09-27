import unittest

from web_app import create_app, parse_web_reference


class ReferenceParsingTests(unittest.TestCase):
    def test_normalizes_common_book_aliases(self):
        self.assertEqual(parse_web_reference("jn 3:16"), ("John", 3, 16))
        self.assertEqual(parse_web_reference("Ps 23.1"), ("Psalm", 23, 1))
        self.assertEqual(parse_web_reference("1 cor 13 4"), ("1 Corinthians", 13, 4))

    def test_rejects_incomplete_reference(self):
        with self.assertRaises(ValueError):
            parse_web_reference("John 3")


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app({"TESTING": True})
        cls.client = cls.app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A focused Bible reader", response.data)
        self.assertIn(b"Minimalist mode", response.data)

    def test_home_page_honors_reverse_proxy_subpath(self):
        response = self.client.get("/", headers={"X-Forwarded-Prefix": "/verse"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/verse/"', response.data)
        self.assertIn(b'href="/verse/static/styles.css?v=', response.data)

    def test_pretty_share_urls_boot_reader_with_200(self):
        for path in ("/John-3-16", "/kjv/Ps-23-1", "/gen/1-John-3-16"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"A focused Bible reader", response.data)

    def test_pretty_routes_do_not_swallow_api(self):
        response = self.client.get("/api/nope")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertEqual(response.get_json()["editions"], 5)

    def test_editions(self):
        response = self.client.get("/api/editions")
        editions = response.get_json()["editions"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual({edition["id"] for edition in editions}, {"esv", "gen", "kj16", "kjv", "nasb"})

    def test_geneva_is_the_api_default(self):
        response = self.client.get("/api/verse", query_string={"reference": "John 3:16"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["edition"]["id"], "gen")

    def test_book_name_suggestions(self):
        response = self.client.get("/api/books", query_string={"q": "joh"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["books"][:2], ["John", "1 John"])

        response = self.client.get("/api/books", query_string={"q": "1 cor"})
        self.assertEqual(
            response.get_json()["books"], ["1 Corinthians"]
        )

    def test_bundled_databases_work_from_a_read_only_tree(self):
        response = self.client.get(
            "/api/verse", query_string={"edition": "esv", "reference": "John 3:16"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("God so loved the world", response.get_json()["text"])

    def test_reads_a_verse_with_navigation(self):
        response = self.client.get(
            "/api/verse", query_string={"edition": "kjv", "reference": "John 3:16"}
        )
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("God so loved the world", payload["text"])
        self.assertEqual(payload["reference"]["display"], "John 3:16")
        self.assertEqual(payload["neighbors"]["previous"]["display"], "John 3:15")
        self.assertEqual(payload["neighbors"]["next"]["display"], "John 3:17")
        self.assertIsNone(payload["source"])

    def test_reads_greek_source(self):
        response = self.client.get(
            "/api/verse",
            query_string={
                "edition": "esv",
                "reference": "John 3:16",
                "source": "1",
            },
        )
        source = response.get_json()["source"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(source["language"], "greek")
        self.assertTrue(source["text"])
        self.assertTrue(source["transliteration"])

    def test_reads_hebrew_source_with_psalm_alias(self):
        response = self.client.get(
            "/api/verse",
            query_string={
                "edition": "nasb",
                "reference": "Psalms 23:1",
                "source": "true",
            },
        )
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["source"]["language"], "hebrew")

    def test_psalm_navigation_populates_for_plural_database_references(self):
        for edition in ("kjv", "kj16"):
            with self.subTest(edition=edition):
                response = self.client.get(
                    "/api/verse",
                    query_string={"edition": edition, "reference": "Psalm 1:1"},
                )
                payload = response.get_json()
                self.assertEqual(response.status_code, 200)
                self.assertIsNotNone(payload["neighbors"]["previous"])
                self.assertEqual(payload["neighbors"]["next"]["display"], "Psalm 1:2")

    def test_rejects_unknown_edition(self):
        response = self.client.get(
            "/api/verse", query_string={"edition": "unknown", "reference": "John 3:16"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown edition", response.get_json()["error"])

    def test_reports_missing_verse(self):
        response = self.client.get(
            "/api/verse", query_string={"edition": "kjv", "reference": "John 99:99"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Verse not found", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
