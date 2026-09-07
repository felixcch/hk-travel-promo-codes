# 旅行慳家 — 香港旅遊優惠碼集合

AdSense-optimized static demo site (Traditional Chinese / Hong Kong) listing travel promo codes for Trip.com, Agoda, Klook, KKday, Booking.com and Expedia.

## Build

```bash
python3 build.py      # regenerates all HTML + ads.txt, robots.txt, sitemap.xml
python3 -m http.server 8080
```

Edit coupons in the `COUPONS` list and set `ADSENSE_CLIENT`, `SITE_URL`, `AFFILIATE_TAG` in `build.py`, and `ADSENSE_CLIENT` in `assets/main.js`.

## AdSense / SEO features

- Consent-gated, lazy-loaded AdSense (no script until the visitor accepts)
- Fixed-height ad containers (no CLS), leaderboard + in-feed + sidebar slots
- `ads.txt`, `robots.txt` (Mediapartners-Google allowed), `sitemap.xml`
- Canonical/OG tags, `zh-Hant-HK` lang, WebSite/CollectionPage/Article JSON-LD
- Privacy & cookie policy, terms, about and contact pages
- Coupon cards: copy-to-clipboard, verified date, client-side expiry hiding, `rel="nofollow sponsored"` affiliate links
