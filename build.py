#!/usr/bin/env python3
"""香港旅遊優惠碼示範網站 — 靜態頁面產生器。

所有頁面共用同一個外框（head、導覽、頁尾、Cookie 同意橫幅、廣告位），
令 AdSense 位置與 SEO 標籤在每個網址都保持一致。
執行：python3 build.py
"""

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent
SITE_NAME = "旅行慳家"
SITE_TAGLINE = "香港旅遊優惠碼集合"
SITE_URL = "https://example.com"
ADSENSE_CLIENT = "ca-pub-0000000000000000"
AFFILIATE_TAG = "?aid=DEMO-AFFILIATE-ID"  # 換成各平台聯盟連結的追蹤參數

# ---------------------------------------------------------------------------
# 平台與優惠碼資料（示範用，實際上線前請逐一核實）
# ---------------------------------------------------------------------------

PLATFORMS = {
    "trip": ("Trip.com", "https://hk.trip.com", "機票、酒店、高鐵一站式預訂，港人最常用的旅遊平台之一。"),
    "agoda": ("Agoda", "https://www.agoda.com/zh-hk", "亞洲酒店選擇最多，經常有 App 限定同信用卡優惠。"),
    "klook": ("Klook", "https://www.klook.com/zh-HK", "景點門票、當地體驗、JR Pass、Wi-Fi 蛋一次過搞掂。"),
    "kkday": ("KKday", "https://www.kkday.com/zh-hk", "台灣、日本、韓國一日遊同交通票券特別多。"),
    "booking": ("Booking.com", "https://www.booking.com/index.zh-tw.html", "免費取消房源多，Genius 會員有長期折扣。"),
    "expedia": ("Expedia", "https://www.expedia.com.hk", "機票加酒店套票折扣大，適合一次過預訂。"),
}

# expires 用 ISO 日期；瀏覽器端會自動隱藏已過期優惠。
COUPONS = [
    dict(platform="trip", title="酒店預訂即減 8%", code="HKHOTEL8", discount="減 8%",
         conditions="適用於指定海外酒店，最高減 HK$300，需經 App 預訂。", verified="2026-09-06", expires="2026-10-31"),
    dict(platform="trip", title="新用戶機票立減 HK$100", code="TRIPNEW100", discount="減 HK$100",
         conditions="首次預訂機票，訂單滿 HK$1,000。", verified="2026-09-06", expires="2026-12-31"),
    dict(platform="trip", title="HSBC 信用卡酒店額外 5% 折扣", code="HSBC5", discount="額外減 5%",
         conditions="以 HSBC 信用卡付款，每月首 2,000 個名額。", verified="2026-09-05", expires="2026-09-30"),
    dict(platform="agoda", title="App 限定酒店 10% Off", code="AGODAAPP10", discount="減 10%",
         conditions="只限 Agoda App 首次預訂，部分酒店除外。", verified="2026-09-06", expires="2026-11-30"),
    dict(platform="agoda", title="日本酒店限時 12% 折扣", code="JAPAN12", discount="減 12%",
         conditions="入住日期 2026 年 10 月至 12 月，訂單滿 HK$1,500。", verified="2026-09-04", expires="2026-10-15"),
    dict(platform="agoda", title="恆生信用卡專享 7%", code="HANGSENG7", discount="減 7%",
         conditions="以恆生信用卡全數付款。", verified="2026-09-03", expires="2026-12-31"),
    dict(platform="klook", title="新用戶首單即減 HK$50", code="KLOOKHK50", discount="減 HK$50",
         conditions="首次下單滿 HK$400 即可使用。", verified="2026-09-06", expires="2026-12-31"),
    dict(platform="klook", title="日本 JR Pass 及交通票 5% Off", code="JRPASS5", discount="減 5%",
         conditions="適用於指定日本交通產品，每個帳戶限用一次。", verified="2026-09-05", expires="2026-10-31"),
    dict(platform="klook", title="環球影城／迪士尼門票減 HK$80", code="THEMEPARK80", discount="減 HK$80",
         conditions="訂單滿 HK$1,200，限指定樂園門票。", verified="2026-09-02", expires="2026-09-30"),
    dict(platform="kkday", title="全站 8% 折扣（滿 HK$500）", code="KKDAYHK8", discount="減 8%",
         conditions="上限 HK$150，不適用於部分交通票券。", verified="2026-09-06", expires="2026-11-15"),
    dict(platform="kkday", title="台灣高鐵 + 一日遊套票 10% Off", code="TAIWAN10", discount="減 10%",
         conditions="限台灣行程，需於出發前 3 日預訂。", verified="2026-09-01", expires="2026-10-31"),
    dict(platform="booking", title="Genius 會員額外 10% 折扣", code="無需優惠碼", discount="減 10%–20%",
         conditions="登入 Booking.com 帳戶自動享有，完成 2 次住宿即升級。", verified="2026-09-06", expires="2027-12-31"),
    dict(platform="expedia", title="機票加酒店套票即減 HK$400", code="EXPEDIAHK400", discount="減 HK$400",
         conditions="套票訂單滿 HK$5,000。", verified="2026-09-05", expires="2026-10-31"),
    dict(platform="expedia", title="已過期示範：夏日酒店 15% Off", code="SUMMER15", discount="減 15%",
         conditions="此優惠碼用來示範前端會自動隱藏過期優惠。", verified="2026-07-01", expires="2026-08-31"),
]

NAV = [
    ("index.html", "全部優惠"),
    ("trip.html", "Trip.com"),
    ("agoda.html", "Agoda"),
    ("klook.html", "Klook"),
    ("kkday.html", "KKday"),
    ("guides/stacking.html", "慳錢攻略"),
    ("about.html", "關於"),
]


def ad_slot(slot_id: str, css_class: str, fmt: str = "auto") -> str:
    layout = ' data-ad-layout="in-article"' if fmt == "fluid" else ""
    responsive = ' data-full-width-responsive="true"' if fmt == "auto" else ""
    return f"""<div class="ad-slot {css_class}">
        <ins class="adsbygoogle"
             data-ad-client="{ADSENSE_CLIENT}"
             data-ad-slot="{slot_id}"
             data-ad-format="{fmt}"{layout}{responsive}></ins>
      </div>"""


def fmt_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{y}年{int(m)}月{int(d)}日"


def coupon_card(c: dict, depth: int) -> str:
    name, url, _ = PLATFORMS[c["platform"]]
    has_code = c["code"] != "無需優惠碼"
    code_block = (
        f'<button class="copy-code" type="button" data-code="{c["code"]}" aria-label="複製優惠碼 {c["code"]}">'
        f'<span class="code">{c["code"]}</span><span class="copy-label">複製</span></button>'
        if has_code
        else '<span class="no-code">無需優惠碼，自動折扣</span>'
    )
    return f"""          <article class="coupon" data-expires="{c['expires']}">
            <div class="coupon-main">
              <div class="coupon-platform">{name}</div>
              <h3>{c['title']}</h3>
              <p class="coupon-conditions">{c['conditions']}</p>
              <p class="coupon-meta">
                <span class="verified">✓ {fmt_date(c['verified'])} 已核實</span>
                <span class="expires">有效至 {fmt_date(c['expires'])}</span>
              </p>
            </div>
            <div class="coupon-side">
              <div class="discount">{c['discount']}</div>
              {code_block}
              <a class="btn-go" href="{url}{AFFILIATE_TAG}" rel="nofollow sponsored noopener" target="_blank">前往 {name}</a>
            </div>
          </article>"""


def coupon_list(coupons, depth: int, ad_every: int = 3) -> str:
    parts = []
    for i, c in enumerate(coupons):
        parts.append(coupon_card(c, depth))
        if (i + 1) % ad_every == 0 and i + 1 < len(coupons):
            parts.append("          " + ad_slot("3344556677", "ad-in-article", "fluid"))
    return "\n".join(parts)


def platform_card(key: str, depth: int) -> str:
    name, _, blurb = PLATFORMS[key]
    count = sum(1 for c in COUPONS if c["platform"] == key)
    return f"""          <a class="card" href="{rel(depth, key + '.html')}">
            <div class="card-body">
              <div class="meta">{count} 個優惠</div>
              <h3>{name} 優惠碼</h3>
              <p>{blurb}</p>
            </div>
          </a>"""


# ---------------------------------------------------------------------------
# 頁面外框
# ---------------------------------------------------------------------------


@dataclass
class Page:
    path: str
    title: str
    description: str
    heading: str
    intro: str
    body: str
    sidebar: bool = True
    extra_head: str = ""


def rel(depth: int, target: str) -> str:
    return ("../" * depth) + target


def render(page: Page) -> str:
    depth = page.path.count("/")
    canonical = f"{SITE_URL}/{page.path}"
    nav = "\n          ".join(
        f'<a href="{rel(depth, href)}"'
        + (' aria-current="page"' if href == page.path else "")
        + f">{label}</a>"
        for href, label in NAV
    )
    platform_links = "".join(
        f'<li><a href="{rel(depth, k + ".html")}">{v[0]} 優惠碼</a></li>' for k, v in PLATFORMS.items()
    )
    sidebar = (
        f"""
      <aside class="sidebar">
        <div class="widget">
          <h4>按平台瀏覽</h4>
          <ul>{platform_links}</ul>
        </div>
        <div class="widget">
          <h4>慳錢攻略</h4>
          <ul>
            <li><a href="{rel(depth, 'guides/stacking.html')}">優惠碼疊加：信用卡 + App + 平台碼</a></li>
            <li><a href="{rel(depth, 'guides/sale-calendar.html')}">2026 下半年旅遊大減價日曆</a></li>
          </ul>
        </div>
        {ad_slot('2233445566', 'ad-sidebar', 'auto')}
      </aside>"""
        if page.sidebar
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-Hant-HK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page.title}</title>
<meta name="description" content="{page.description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_HK">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{page.title}">
<meta property="og:description" content="{page.description}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
<link rel="preconnect" href="https://googleads.g.doubleclick.net" crossorigin>
<link rel="dns-prefetch" href="https://pagead2.googlesyndication.com">
<link rel="stylesheet" href="{rel(depth, 'assets/style.css')}">
<script defer src="{rel(depth, 'assets/main.js')}"></script>
{page.extra_head}</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{rel(depth, 'index.html')}">旅行<span>慳家</span></a>
      <nav class="nav" aria-label="主導覽">
          {nav}
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="container">
      <h1>{page.heading}</h1>
      <p>{page.intro}</p>
    </div>
  </section>

  <div class="container">
    {ad_slot('1122334455', 'ad-leaderboard', 'auto')}
    <div class="layout">
      <main>
{page.body}
      </main>{sidebar}
    </div>
  </div>

  <footer class="site-footer">
    <div class="container footer-inner">
      <span>&copy; 2026 {SITE_NAME}。部分連結為聯盟連結，經此預訂本站或會收取佣金，價格不受影響。</span>
      <span>
        <a href="{rel(depth, 'privacy.html')}">私隱及 Cookie 政策</a> ·
        <a href="{rel(depth, 'terms.html')}">使用條款</a> ·
        <a href="{rel(depth, 'contact.html')}">聯絡我們</a>
      </span>
    </div>
  </footer>

  <div class="consent" role="dialog" aria-live="polite" aria-label="Cookie 同意">
    <p>本站使用 Cookie 以個人化內容及廣告，並分析流量。接受後才會載入廣告。
       詳情請看<a href="{rel(depth, 'privacy.html')}">私隱及 Cookie 政策</a>。</p>
    <div class="consent-actions">
      <button class="btn-ghost" data-consent="denied">拒絕</button>
      <button class="btn-primary" data-consent="granted">接受</button>
    </div>
  </div>
  <div class="toast" role="status" aria-live="polite"></div>
</body>
</html>
"""


def guide(slug, title, description, heading, intro, date, sections):
    parts = ['        <article class="article">',
             f'          <p class="byline">旅行慳家編輯部 · 更新於 {fmt_date(date)}</p>']
    for i, (h2, paragraphs) in enumerate(sections):
        parts.append(f"          <h2>{h2}</h2>")
        parts.extend(f"          {p}" for p in paragraphs)
        if i == 0:
            parts.append("          " + ad_slot("3344556677", "ad-in-article", "fluid"))
    parts.append('          <p class="note">優惠條款以各平台官方頁面為準，落單前請再次核對金額。</p>')
    parts.append("        </article>")
    schema = (
        '<script type="application/ld+json">\n'
        f'{{"@context":"https://schema.org","@type":"Article","headline":"{heading}","description":"{description}",'
        f'"inLanguage":"zh-Hant-HK","author":{{"@type":"Organization","name":"{SITE_NAME}"}},'
        f'"publisher":{{"@type":"Organization","name":"{SITE_NAME}"}},"datePublished":"{date}",'
        f'"mainEntityOfPage":"{SITE_URL}/guides/{slug}.html"}}\n</script>\n'
    )
    return Page(path=f"guides/{slug}.html", title=title, description=description, heading=heading,
                intro=intro, body="\n".join(parts), extra_head=schema)


def platform_page(key: str) -> Page:
    name, _, blurb = PLATFORMS[key]
    coupons = [c for c in COUPONS if c["platform"] == key]
    body = f"""        <section class="coupon-section">
          <h2>{name} 最新優惠碼（{len(coupons)} 個）</h2>
          <p class="section-intro">{blurb} 以下優惠碼由編輯部人手測試，每日更新；過期優惠會自動隱藏。</p>
          <div class="coupon-list">
{coupon_list(coupons, 0)}
          </div>
          <p class="empty-state" hidden>暫時未有有效優惠碼，請稍後再回來看看。</p>
        </section>
        <section class="article">
          <h2>{name} 優惠碼使用方法</h2>
          <ol>
            <li>按「複製」按鈕複製優惠碼。</li>
            <li>按「前往 {name}」開啟平台，揀好酒店、機票或行程。</li>
            <li>去到付款頁面，在「優惠碼／Promo code」欄貼上並確認折扣已扣減。</li>
            <li>用指定信用卡付款，可以同信用卡優惠疊加（見<a href="guides/stacking.html">疊加攻略</a>）。</li>
          </ol>
        </section>"""
    schema = (
        '<script type="application/ld+json">\n'
        f'{{"@context":"https://schema.org","@type":"CollectionPage","name":"{name} 優惠碼","inLanguage":"zh-Hant-HK",'
        f'"url":"{SITE_URL}/{key}.html","isPartOf":{{"@type":"WebSite","name":"{SITE_NAME}","url":"{SITE_URL}/"}}}}\n</script>\n'
    )
    return Page(
        path=f"{key}.html",
        title=f"{name} 優惠碼 2026 年 9 月｜最新折扣碼、信用卡優惠 — {SITE_NAME}",
        description=f"{name} 香港最新優惠碼、折扣碼及信用卡優惠，每日人手核實，過期自動下架。",
        heading=f"{name} 優惠碼",
        intro=f"{blurb}",
        body=body,
        extra_head=schema,
    )


def build_pages():
    platform_cards = "\n".join(platform_card(k, 0) for k in PLATFORMS)
    home_body = f"""        <section class="coupon-section">
          <h2>今日精選優惠碼</h2>
          <p class="section-intro">全部優惠碼均由編輯部人手測試，標明核實日期；過期優惠會自動隱藏。</p>
          <div class="coupon-list">
{coupon_list(COUPONS, 0, ad_every=4)}
          </div>
          <p class="empty-state" hidden>暫時未有有效優惠碼，請稍後再回來看看。</p>
        </section>
        <section>
          <h2>按平台瀏覽</h2>
          <div class="card-grid">
{platform_cards}
          </div>
        </section>
        <section class="article">
          <h2>關於旅行慳家</h2>
          <p>旅行慳家是一個專為香港旅客而設的優惠碼集合站。我們每日檢查 Trip.com、Agoda、Klook、KKday、Booking.com
          及 Expedia 的最新優惠碼同信用卡推廣，只保留仍然有效、真正可以用到的折扣，並清楚寫明使用條件。</p>
          <p>想再慳多一步？睇睇<a href="guides/stacking.html">優惠碼疊加攻略</a>，學識點樣將信用卡優惠、App 限定折扣同平台優惠碼一齊用。</p>
        </section>"""

    pages = [
        Page(
            path="index.html",
            title=f"{SITE_NAME} — {SITE_TAGLINE}｜Trip.com、Agoda、Klook 優惠碼每日更新",
            description="香港旅遊優惠碼集合：Trip.com、Agoda、Klook、KKday、Booking.com、Expedia 最新折扣碼及信用卡優惠，每日人手核實。",
            heading="訂機票酒店前，先過來拎個優惠碼",
            intro="每日核實的香港旅遊優惠碼：Trip.com、Agoda、Klook、KKday 折扣碼同信用卡優惠，一按複製，過期自動下架。",
            body=home_body,
            extra_head=(
                '<script type="application/ld+json">\n'
                f'{{"@context":"https://schema.org","@type":"WebSite","name":"{SITE_NAME}","url":"{SITE_URL}/","inLanguage":"zh-Hant-HK"}}\n</script>\n'
            ),
        ),
        *[platform_page(k) for k in PLATFORMS],
        guide(
            "stacking",
            f"優惠碼疊加攻略：信用卡 + App + 平台碼點樣一齊用 — {SITE_NAME}",
            "教你將旅遊平台優惠碼、App 限定折扣同香港信用卡推廣疊加使用，酒店機票隨時慳多 15% 以上。",
            "優惠碼疊加攻略：信用卡 + App + 平台碼",
            "大部分人只會用一個優惠碼。其實只要次序正確，三層折扣可以同時生效。",
            "2026-09-05",
            [
                ("三層折扣的次序", [
                    "<p>旅遊平台的折扣一般分三層：<strong>平台優惠碼</strong>（付款頁輸入）、<strong>App 限定價</strong>（只限手機 App 顯示）同<strong>信用卡推廣</strong>（付款後回贈或即時折扣）。"
                    "三層之間通常互不排斥，因為前兩層由平台承擔，第三層由銀行承擔。</p>",
                    "<p>正確次序係：先用 App 開啟商品確認有 App 價，再輸入平台優惠碼，最後揀選有推廣的信用卡付款。倒轉次序好多時會令優惠碼欄消失。</p>",
                ]),
                ("香港信用卡常見旅遊優惠", [
                    "<ul><li><strong>HSBC</strong>：Trip.com、Agoda 指定日子額外 5%–8%，通常需要輸入銀行專屬碼。</li>"
                    "<li><strong>恆生</strong>：Agoda、Klook 全年 7%–8%，每月名額有限，月初用較穩陣。</li>"
                    "<li><strong>渣打／DBS</strong>：Expedia、Booking.com 現金回贈，多數係簽賬後回贈而非即減。</li>"
                    "<li><strong>Citi</strong>：Klook 同 KKday 不時有 HK$100 至 HK$200 即減碼。</li></ul>",
                    "<p>銀行碼同平台碼多數只可以二揀一輸入，但銀行碼的折扣通常較大，所以先試銀行碼，再比較。</p>",
                ]),
                ("實戰例子", [
                    "<p>假設一間日本酒店 Trip.com 網頁價 HK$2,000，App 價 HK$1,900（減 5%）。輸入 HKHOTEL8 再減 8%，變成 HK$1,748。"
                    "用 HSBC 信用卡付款享 5% 回贈，實際成本約 HK$1,660，比網頁價慳 17%。</p>",
                    "<p>記得截圖付款頁面顯示的最終金額，如果回贈遲遲未到，可以憑截圖向銀行查詢。</p>",
                ]),
            ],
        ),
        guide(
            "sale-calendar",
            f"2026 下半年旅遊大減價日曆：9.9、11.11、雙 12 幾時買最抵 — {SITE_NAME}",
            "整理 Trip.com、Agoda、Klook、KKday 2026 年下半年大型促銷日期，話你知機票酒店幾時落單最抵。",
            "2026 下半年旅遊大減價日曆",
            "旅遊平台的減價有固定節奏。知道日子，就唔會在大減價前一日落單。",
            "2026-09-01",
            [
                ("9 月至 10 月", [
                    "<ul><li><strong>9 月 9 日（9.9）</strong>：Klook、KKday 東南亞行程同 Wi-Fi 蛋大減價，多數 9 月 5 日開始預熱。</li>"
                    "<li><strong>10 月上旬</strong>：Trip.com 十一黃金週後清貨，日韓酒店最抵。</li>"
                    "<li><strong>10 月 10 日（10.10）</strong>：Agoda「十月十折」App 限定，通常凌晨開賣。</li></ul>",
                ]),
                ("11 月：全年最大", [
                    "<p><strong>11 月 11 日</strong>係全年折扣最深的一日。Trip.com 會推出限量 HK$1 機票同酒店券，Klook 有「買一送一」門票，Agoda 有低至 3 折的神秘酒店。"
                    "策略係 11 月 1 日起每日檢查優惠券頁面，先領券再等 11.11 當日落單。</p>",
                    "<p>另外 11 月尾的<strong>黑色星期五</strong>同<strong>Cyber Monday</strong>，Expedia 同 Booking.com 較積極，歐美酒店折扣尤其大。</p>",
                ]),
                ("12 月", [
                    "<ul><li><strong>12 月 12 日（雙 12）</strong>：Klook、KKday 再減一波，主打聖誕同農曆新年行程。</li>"
                    "<li><strong>聖誕後至除夕</strong>：Trip.com 會為明年首季推早鳥機票優惠，適合計劃復活節旅行。</li></ul>",
                ]),
            ],
        ),
        Page(
            path="about.html",
            title=f"關於我們 — {SITE_NAME}",
            description="旅行慳家係一個獨立經營的香港旅遊優惠碼網站，介紹我們的核實流程、收入來源同編採原則。",
            heading="關於旅行慳家",
            intro="由兩位港人兼職營運的旅遊優惠碼集合站——唔賣旅行團，唔收平台廣告費寫軟文。",
            body="""        <article class="article">
          <h2>我們點樣核實優惠碼</h2>
          <p>每一個優惠碼上架前，編輯都會親自在該平台行到付款頁面，確認折扣真正扣減；每日早上再重新檢查一次。
          核實日期會顯示在每張優惠卡上，過期優惠會由系統自動隱藏。</p>
          <h2>收入來源</h2>
          <p>網站有兩個收入來源：一、經聯盟連結預訂後平台支付的佣金（價格對你完全一樣）；二、Google AdSense 展示廣告。
          廣告商同平台都無權影響我們列出或刪除哪些優惠碼。</p>
          <h2>聯絡</h2>
          <p>發現優惠碼失效、或者有新優惠想我們加入，歡迎<a href="contact.html">聯絡我們</a>。</p>
        </article>""",
        ),
        Page(
            path="contact.html",
            title=f"聯絡我們 — {SITE_NAME}",
            description="回報失效優惠碼、提供新優惠或商務合作，請聯絡旅行慳家編輯部。",
            heading="聯絡我們",
            intro="優惠碼失效？有新優惠想分享？直接電郵我們，一般三個工作天內回覆。",
            body="""        <article class="article">
          <h2>電郵</h2>
          <p>編輯部及優惠回報：<a href="mailto:editors@example.com">editors@example.com</a><br>
          廣告及私隱查詢：<a href="mailto:privacy@example.com">privacy@example.com</a></p>
          <h2>回報失效優惠碼</h2>
          <p>請在電郵內註明平台、優惠碼、嘗試日期同錯誤訊息截圖，我們會在 24 小時內覆核並更新。</p>
          <h2>通訊地址</h2>
          <p>旅行慳家<br>香港九龍觀塘道 123 號示範大廈 8 樓</p>
        </article>""",
        ),
        Page(
            path="privacy.html",
            title=f"私隱及 Cookie 政策 — {SITE_NAME}",
            description="旅行慳家如何使用 Cookie、Google AdSense 如何投放個人化廣告，以及如何選擇退出。",
            heading="私隱及 Cookie 政策",
            intro="最後更新：2026 年 9 月 1 日。本政策說明我們收集甚麼資料、用途，以及如何退出個人化廣告。",
            body="""        <article class="article">
          <h2>我們收集甚麼</h2>
          <p>本站無需登入亦不會要求個人資料。流量分析只以匯總形式記錄頁面網址、來源、大約地區及裝置類型。
          你發給我們的電郵只會保留至問題處理完畢。</p>
          <h2>廣告 Cookie</h2>
          <p>本站透過 Google AdSense 展示廣告。包括 Google 在內的第三方供應商會使用 Cookie，根據你先前瀏覽本站及其他網站的記錄投放廣告。
          Google 使用廣告 Cookie 讓其及合作夥伴能根據你在本站及互聯網上其他網站的瀏覽記錄向你展示廣告。</p>
          <ul>
            <li>你可以在 <a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google 廣告設定</a>選擇退出個人化廣告。</li>
            <li>你亦可以在 <a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info/choices</a> 退出第三方供應商 Cookie。</li>
            <li>Google 的做法詳見 <a href="https://policies.google.com/technologies/partner-sites" rel="nofollow noopener" target="_blank">Google 私隱權與條款</a>。</li>
          </ul>
          <h2>聯盟連結</h2>
          <p>「前往平台」按鈕為聯盟連結，平台會透過 Cookie 記錄你由本站前往。你支付的價格不會因此改變。</p>
          <h2>同意機制</h2>
          <p>在你按「接受」之前，本站不會載入任何廣告程式碼。如選擇「拒絕」，本裝置將不會請求 AdSense 程式庫。清除本站的瀏覽器儲存資料即可再次看到提示。</p>
          <h2>你的權利</h2>
          <p>根據香港《個人資料（私隱）條例》，你有權查閱及改正我們持有的個人資料。請電郵 <a href="mailto:privacy@example.com">privacy@example.com</a>。</p>
        </article>""",
        ),
        Page(
            path="terms.html",
            title=f"使用條款 — {SITE_NAME}",
            description="使用旅行慳家網站的條款，包括優惠資訊的準確性聲明及責任限制。",
            heading="使用條款",
            intro="簡單講清楚你可以點樣使用本站，以及本站內容的限制。",
            body="""        <article class="article">
          <h2>優惠資訊</h2>
          <p>所有優惠碼及條款均按核實當日的資料整理，平台可隨時更改或終止。最終折扣以各平台付款頁面顯示為準。</p>
          <h2>內容使用</h2>
          <p>歡迎在註明出處及附上連結的情況下引用短段落。整篇轉載或用作商業用途須事先取得書面同意。</p>
          <h2>責任限制</h2>
          <p>本站按「現況」提供。我們不會就優惠碼失效、平台價格變動或任何依賴本站資訊而引致的損失承擔責任。</p>
        </article>""",
        ),
    ]
    return pages


def main():
    pages = build_pages()
    for page in pages:
        out = ROOT / page.path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(page), encoding="utf-8")

    (ROOT / "ads.txt").write_text(
        f"google.com, {ADSENSE_CLIENT.replace('ca-pub-', 'pub-')}, DIRECT, f08c47fec0942fa0\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nUser-agent: Mediapartners-Google\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{p.path}</loc><changefreq>daily</changefreq></url>" for p in pages
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8",
    )
    print(f"built {len(pages)} pages + ads.txt, robots.txt, sitemap.xml")


if __name__ == "__main__":
    main()
