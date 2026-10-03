import os, sys, unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from agents.browser import minify_html
from agents.content_select import smart_minify
from core.config import settings


def _amazon_like(n_cards=24):
    menu = "".join(f'<div class="nav-menu-item"><a class="nav-a" href="/gp/browse/{i}" data-nav-role="x{i}" '
                   f'data-csa-c-type="link" data-csa-c-slot-id="slot{i}">Category number {i} electronics and more</a></div>'
                   for i in range(120))
    filters = "".join(f'<li class="a-spacing-micro"><span class="a-list-item"><a href="/s?rh=n{i}" class="a-link-normal">'
                      f'<span class="a-size-base a-color-base">Filter option {i} brand</span></a></span></li>' for i in range(40))
    cards = ""
    for i in range(n_cards):
        extra = " AdHolder" if i % 7 == 0 else ""
        cards += (f'<div data-asin="B0{i:08d}" data-index="{i}" data-uuid="uuid-{i}-abcdef" data-component-type="s-search-result" '
                  f'class="sg-col-4-of-24 s-result-item s-asin{extra}"><div class="a-section a-spacing-base">'
                  f'<a class="a-link-normal s-no-outline" href="/dp/B0{i:08d}/ref=sr_1_{i}?crid=ABC&sprefix=lenovo"><img src="https://m.media-amazon.com/{i}.jpg" alt="x"></a>'
                  f'<h2 class="a-size-mini"><a class="a-link-normal" href="/dp/B0{i:08d}"><span class="a-size-medium a-color-base a-text-normal">'
                  f'Lenovo LOQ Model {i} 12th Gen Core i5 16GB RAM 512GB SSD RTX 3050 Gaming Laptop</span></a></h2>'
                  f'<span class="a-price"><span class="a-offscreen">\u20b9{60000+i*137:,}</span></span>'
                  f'<span class="a-icon-alt">4.{i%10} out of 5 stars</span><span>{1000+i} ratings</span></div></div>')
    return (f'<html><head><title>Amazon.in : lenovo loq</title><script>var a=1;</script></head><body>'
            f'<div id="nav-belt">{menu}</div><div class="sidebar"><ul>{filters}</ul></div>'
            f'<div class="s-main-slot s-result-list">{cards}</div><footer><a href="/help">Help</a></footer></body></html>')


def _flipkart_like(rows=8):
    html = '<html><head><title>Lenovo Loq - Buy Products Online | Flipkart.com</title></head><body><div class="_hdr">' + \
           "".join(f'<a class="_1AtVbE" href="/c{i}">Menu entry {i} with a fairly long descriptive label here</a>' for i in range(150)) + '</div><div class="_1YokD2">'
    for r in range(rows):
        html += '<div class="_1AtVbE _2g3Xyz">'
        for c in range(4):
            k = r * 4 + c
            html += (f'<div data-id="MOB{k}" class="_4ddWXP"><a class="s1Q9rs" href="/lenovo-loq-{k}/p/itm{k}" title="Lenovo LOQ {k}">'
                     f'Lenovo LOQ {k} Intel Core i5 12th Gen 16 GB/512 GB SSD/Windows 11 Home/6 GB Graphics</a>'
                     f'<div class="_3I9_wc">\u20b9{58990+k*100:,}</div><div class="_3LWZlK">4.{k%10}</div></div>')
        html += '</div>'
    return html + '</div></body></html>'


class TestSmartContentSelection(unittest.TestCase):
    def setUp(self):
        self._orig = getattr(settings, "SMART_CONTENT_SELECTION", False)

    def tearDown(self):
        settings.SMART_CONTENT_SELECTION = self._orig

    def test_legacy_loses_the_grid_smart_keeps_it_amazon(self):
        html = _amazon_like()
        settings.SMART_CONTENT_SELECTION = False
        legacy = minify_html(html)
        settings.SMART_CONTENT_SELECTION = True
        smart = minify_html(html)
        self.assertLessEqual(len(smart), 14000 + 40)
        self.assertLess(legacy.count("/dp/B0"), 2, "legacy path should (wrongly) miss the product grid")
        self.assertGreaterEqual(smart.count("/dp/B0"), 8, "smart path must keep many product cards")
        self.assertIn("Lenovo LOQ Model", smart)

    def test_flipkart_like_grid(self):
        html = _flipkart_like()
        settings.SMART_CONTENT_SELECTION = True
        smart = minify_html(html)
        self.assertGreaterEqual(smart.count("/p/itm"), 12)

    def test_small_pages_are_byte_identical_to_legacy(self):
        small = "<html><body><ul>" + "".join(f"<li><a href='/x{i}'>Item {i}</a></li>" for i in range(10)) + "</ul></body></html>"
        settings.SMART_CONTENT_SELECTION = False
        a = minify_html(small)
        settings.SMART_CONTENT_SELECTION = True
        b = minify_html(small)
        self.assertEqual(a, b)

    def test_flag_off_is_exactly_legacy_for_big_pages(self):
        html = _amazon_like()
        settings.SMART_CONTENT_SELECTION = False
        out = minify_html(html)
        self.assertTrue(out.endswith("<!-- TRUNCATED -->"))

    def test_table_header_kept(self):
        rows = "".join(f"<tr><td><a href='/r{i}'>Row {i} company name pvt ltd</a></td><td>Mumbai office location address {i}</td></tr>" for i in range(200))
        html = f"<html><body><div>{'x'*20000}</div><table><thead><tr><th>Company</th><th>Address</th></tr></thead><tbody>{rows}</tbody></table></body></html>"
        out = smart_minify(html, 6000)
        self.assertIn("Company", out)
        self.assertIn("Row 0", out)
        self.assertLessEqual(len(out), 6000)

    def test_no_cluster_falls_back_to_truncation(self):
        html = "<html><body><article>" + "<p>Long paragraph text. </p>" * 3000 + "</article></body></html>"
        out = smart_minify(html, 5000)
        self.assertLessEqual(len(out), 5000 + 30)

    def test_json_ld_preserved(self):
        ld = '<script type="application/ld+json">{"@type":"Product","name":"Lenovo LOQ","offers":{"price":"61990"}}</script>'
        html = _amazon_like().replace("</head>", ld + "</head>")
        out = smart_minify(html, 14000)
        self.assertIn('"name":"Lenovo LOQ"', out)

    def test_garbage_html_never_raises(self):
        for junk in ["", "<", "<<<>>>", "\x00\x01", "<html><body><div>" * 500]:
            try:
                smart_minify(junk, 1000)
            except Exception as e:  # pragma: no cover
                self.fail(f"smart_minify raised on junk input: {e}")


if __name__ == "__main__":
    unittest.main()
