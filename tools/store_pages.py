"""Customer store pages: account, orders, order detail, tracking, thank-you, favorites, contact, unsubscribe
and the policies. Called from build.py (``store_pages.build(module)``) so it can reuse head/header/footer/chrome_end.

Pages that need the store read window.LHH_FIREBASE through assets/store.js; while it is empty they show a
friendly "opening soon" state. Everything here is static HTML; the scripts fill in the states.
"""
import json

B = None   # the build module, set by build()
E = None

NOINDEX = '<meta name="robots" content="noindex">\n</head>'
UPDATED = "October 10, 2026"
SUPPORT = "support@littlehivehouse.com"


def page(path, title, desc, active, body, scripts=(), noindex=False, prefix=""):
    pg = B.Page(prefix)
    h = B.head(pg, title, desc, path)
    if noindex:
        h = h.replace("</head>", NOINDEX, 1)
    if "orders.js" in scripts:   # collection names for order items (orders keep the collection slug)
        cols = json.dumps({c["slug"]: c["name"] for c in B.COLLECTIONS}, separators=(",", ":"), ensure_ascii=False)
        body += f"<script>window.LHH_COLS={cols};</script>\n"
    B.write(path, h + B.header(pg, active) + body + B.footer(pg) + B.chrome_end(pg, tuple(scripts)))


def head_block(crumb, h1, lede="", eyebrow="", h1_id="page-title", lede_id="page-lede", extra=""):
    crumbs = '<li><a href="index.html">Home</a></li>' + "".join(
        f'<li><a href="{href}">{E(t)}</a></li>' if href else f'<li aria-current="page"{" id=" + chr(34) + "crumb-order" + chr(34) if t == "Order" else ""}>{E(t)}</li>'
        for t, href in crumb)
    eb = f'<p class="eyebrow">{eyebrow}</p>\n    ' if eyebrow else ""
    ld = f'\n    <p class="lede" id="{lede_id}">{lede}</p>' if lede else ""
    return f"""<div class="wrap page-head">
    <ol class="crumbs">{crumbs}</ol>
    {eb}<h1 id="{h1_id}">{h1}</h1>{ld}{extra}
  </div>"""


def soon(title, text, actions):
    return f"""<div class="panel soon" id="st-soon" hidden>
        <span class="soon-hex" aria-hidden="true"></span>
        <div>
          <h2>{title}</h2>
          <p>{text}</p>
          <div class="row">{actions}</div>
        </div>
      </div>"""


LOADING = """<div class="panel loading" id="st-loading" role="status"><span class="spin" aria-hidden="true"></span>Loading…</div>"""
ERROR = """<div class="panel" id="st-error" hidden><h2>Something went wrong</h2><p class="msg err" id="st-error-msg" role="alert"></p>
        <div class="row"><button type="button" class="btn btn-small" onclick="location.reload()">Try again</button><a class="btn btn-ghost btn-small" href="contact.html">Contact us</a></div></div>"""
NOSCRIPT = """<noscript><p class="panel">This page needs JavaScript. You can always email us at <a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a>.</p></noscript>"""


# ------------------------------------------------------------------ account
def page_account():
    body = f"""
<main id="main" data-page="account">
  {head_block([("Your account", None)], "Your account", "Sign in to see your orders and tracking, and keep your favorite designs on every device.")}
  <section class="tight">
    <div class="wrap">
      {NOSCRIPT}
      {LOADING}
      {soon("Accounts are opening soon", "We’re putting the finishing touches on customer accounts. Until then you can shop as usual, and save designs with the heart on any magnet: your favorites stay on this device.",
            '<a class="btn btn-small" href="shop.html">Shop all designs</a><a class="btn btn-ghost btn-small" href="favorites.html">Your favorites</a>')}
      {ERROR}

      <div class="auth" id="st-auth" hidden>
        <div class="panel auth-card">
          <div class="auth-tabs" id="auth-tabs" role="tablist" aria-label="Sign in or create an account">
            <button type="button" role="tab" id="tab-in" aria-controls="pane-in" aria-selected="true">Sign in</button>
            <button type="button" role="tab" id="tab-up" aria-controls="pane-up" aria-selected="false" tabindex="-1">Create account</button>
          </div>

          <form class="auth-form" id="pane-in" role="tabpanel" aria-labelledby="tab-in" novalidate>
            <div class="field"><label for="in-email">Email</label><input id="in-email" type="email" autocomplete="email" inputmode="email" required></div>
            <div class="field">
              <div class="field-top"><label for="in-pw">Password</label><a href="#" class="linkish" data-go="reset">Forgot password?</a></div>
              <div class="pw"><input id="in-pw" type="password" autocomplete="current-password" required><button type="button" class="pw-toggle" data-reveal="in-pw" aria-pressed="false" aria-label="Show password">Show</button></div>
            </div>
            <p class="msg" id="in-msg" role="alert" hidden></p>
            <button type="submit" class="btn btn-honey" id="in-go">Sign in</button>
            <p class="auth-switch">New here? <a href="#" class="linkish" data-go="tab-up">Create an account</a></p>
          </form>

          <form class="auth-form" id="pane-up" role="tabpanel" aria-labelledby="tab-up" novalidate hidden>
            <div class="field"><label for="up-name">Your name</label><input id="up-name" autocomplete="name" required></div>
            <div class="field"><label for="up-email">Email</label><input id="up-email" type="email" autocomplete="email" inputmode="email" required></div>
            <div class="field">
              <label for="up-pw">Choose a password</label>
              <div class="pw"><input id="up-pw" type="password" autocomplete="new-password" minlength="8" required aria-describedby="up-pw-hint"><button type="button" class="pw-toggle" data-reveal="up-pw" aria-pressed="false" aria-label="Show password">Show</button></div>
              <p class="field-hint" id="up-pw-hint">At least 8 characters.</p>
            </div>
            <label class="check" for="up-mkt"><input type="checkbox" id="up-mkt"><span>Email me about new designs and offers. You can stop anytime.</span></label>
            <p class="msg" id="up-msg" role="alert" hidden></p>
            <button type="submit" class="btn btn-honey" id="up-go">Create account</button>
            <p class="auth-fine">By creating an account you agree to our <a href="terms.html">terms</a> and <a href="privacy.html">privacy policy</a>.</p>
          </form>

          <form class="auth-form" id="pane-reset" novalidate hidden aria-labelledby="reset-h">
            <h2 id="reset-h">Reset your password</h2>
            <p class="muted">Enter the email you use for your account and we’ll send you a link to choose a new password.</p>
            <div class="field"><label for="reset-email">Email</label><input id="reset-email" type="email" autocomplete="email" inputmode="email" required></div>
            <p class="msg" id="reset-msg" role="status" hidden></p>
            <button type="submit" class="btn btn-honey" id="reset-go">Email me a reset link</button>
            <p class="auth-switch"><a href="#" class="linkish" data-go="tab-in">← Back to sign in</a></p>
          </form>
        </div>
        <aside class="auth-side" aria-label="Why create an account">
          <ul class="perks">
            <li><strong>Every order in one place</strong><span>See what you ordered, where it is and the tracking link.</span></li>
            <li><strong>Favorites on every device</strong><span>Tap the heart on any magnet and find it again later.</span></li>
            <li><strong>Order again in one tap</strong><span>Put a past order back in your cart with “Buy again”.</span></li>
          </ul>
          <p class="note">Ordered without an account? <a href="track.html">Track your order</a> with the order number and your email.</p>
        </aside>
      </div>

      <div id="st-home" hidden>
        <div class="verify-banner" id="verify-banner" hidden>
          <p><strong>Please confirm your email.</strong> We sent a link to <span id="verify-email"></span>. Confirming it keeps your account safe and brings in any orders you placed as a guest with this email.</p>
          <div class="row">
            <button type="button" class="btn btn-small" id="verify-resend">Resend the email</button>
            <button type="button" class="btn btn-ghost btn-small" id="verify-check">I’ve confirmed it</button>
          </div>
          <p class="msg" id="verify-msg" role="status" hidden></p>
        </div>
        <div class="acct-grid">
          <section class="panel acct-orders" aria-labelledby="recent-h">
            <div class="panel-head"><h2 id="recent-h">Recent orders</h2><a class="linkish" href="orders.html" id="recent-more" hidden>See all orders</a></div>
            <p class="muted" id="recent-loading" role="status">Loading your orders…</p>
            <ul class="olist" id="recent"></ul>
            <div class="empty-mini" id="recent-empty" hidden><p>No orders yet. When you order while signed in, it shows up here with its tracking.</p><a class="btn btn-small" href="shop.html">Shop all designs</a></div>
          </section>
          <div class="acct-side">
            <a class="panel acct-link-card" href="favorites.html">
              <span class="fav-badge" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 20.3s-7.6-4.6-9.2-9.4C1.7 7.6 3.8 4.4 7.1 4.4c2 0 3.6 1.1 4.9 2.9 1.3-1.8 2.9-2.9 4.9-2.9 3.3 0 5.4 3.2 4.3 6.5-1.6 4.8-9.2 9.4-9.2 9.4z"/></svg></span>
              <span><strong>Favorites</strong><span><span data-fav-count>0</span> saved designs</span></span>
              <span class="ocard-go" aria-hidden="true">›</span>
            </a>
            <section class="panel" aria-labelledby="me-h">
              <h2 id="me-h">Your details</h2>
              <dl class="me">
                <div><dt>Name</dt><dd id="me-name"></dd></div>
                <div><dt>Email</dt><dd id="me-email"></dd></div>
              </dl>
              <label class="check" for="me-mkt"><input type="checkbox" id="me-mkt" disabled><span>Email me about new designs and offers</span></label>
              <p class="msg" id="me-msg" role="status" hidden></p>
              <div class="row">
                <button type="button" class="btn btn-ghost btn-small" id="me-reset">Change password</button>
                <button type="button" class="btn btn-ghost btn-small" id="me-out">Sign out</button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    page("account.html", "Your account", "Sign in to see your Little Hive House orders, tracking and favorites.", None, body,
         ("orders.js", "account.js"), noindex=True)


# ------------------------------------------------------------------ orders
def signin_box(next_page):
    return f"""<div class="panel soon" id="st-signin" hidden>
        <span class="soon-hex" aria-hidden="true"></span>
        <div>
          <h2>Sign in to see your orders</h2>
          <p>Your orders and their tracking live in your account. Ordered as a guest? Track it with the order number from your confirmation email.</p>
          <div class="row"><a class="btn btn-small" id="signin-link" href="account.html?next={next_page}">Sign in</a><a class="btn btn-ghost btn-small" href="track.html">Track a guest order</a></div>
        </div>
      </div>"""


SOON_ORDERS = soon("Order history is opening soon",
                   f"Customer accounts are almost ready. Need to know where an order is? Email us at <a href=\"mailto:{SUPPORT}\">{SUPPORT}</a> with your name and we’ll reply within one business day.",
                   '<a class="btn btn-small" href="contact.html">Contact us</a><a class="btn btn-ghost btn-small" href="shipping.html">Shipping times</a>')


def page_orders():
    body = f"""
<main id="main" data-page="orders">
  {head_block([("Your account", "account.html"), ("Orders", None)], "Your orders", "Everything you’ve ordered while signed in, newest first.")}
  <section class="tight">
    <div class="wrap narrow">
      {NOSCRIPT}
      {LOADING}
      {SOON_ORDERS}
      {signin_box("orders.html")}
      {ERROR}
      <div id="st-content" hidden></div>
    </div>
  </section>
</main>
"""
    page("orders.html", "Your orders", "Your Little Hive House orders.", None, body, ("orders.js",), noindex=True)


def page_order():
    meta = '\n    <div class="order-meta" id="order-meta" hidden></div>'
    body = f"""
<main id="main" data-page="order">
  {head_block([("Your account", "account.html"), ("Orders", "orders.html"), ("Order", None)], "Your order", extra=meta)}
  <section class="tight">
    <div class="wrap">
      {NOSCRIPT}
      {LOADING}
      {SOON_ORDERS}
      {signin_box("orders.html")}
      {ERROR}
      <div id="st-content" hidden></div>
    </div>
  </section>
</main>
"""
    page("order.html", "Your order", "Order details and tracking.", None, body, ("orders.js",), noindex=True)


def page_track():
    body = f"""
<main id="main" data-page="track">
  {head_block([("Track an order", None)], "Track your order", "No account needed. Use the order number from your confirmation email (it looks like LHH&#8209;1042) and the email you ordered with.")}
  <section class="tight">
    <div class="wrap">
      {NOSCRIPT}
      {soon("Order tracking is opening soon", f"Until then, email us at <a href=\"mailto:{SUPPORT}\">{SUPPORT}</a> with your name and we’ll tell you exactly where your order is. Every package also gets a tracking email from us when it ships.",
            '<a class="btn btn-small" href="contact.html">Contact us</a><a class="btn btn-ghost btn-small" href="shipping.html">Shipping times</a>')}
      <div id="st-content" hidden>
        <form class="panel track-form" id="track-form" novalidate>
          <div class="field"><label for="t-num">Order number</label><input id="t-num" name="number" placeholder="LHH-1042" autocomplete="off" autocapitalize="characters" spellcheck="false" required></div>
          <div class="field"><label for="t-email">Email</label><input id="t-email" name="email" type="email" autocomplete="email" inputmode="email" required></div>
          <button type="submit" class="btn btn-honey">Track order</button>
          <p class="msg err" id="track-msg" role="alert" hidden></p>
        </form>
        <p class="track-alt">Have an account? <a href="account.html?next=orders.html">Sign in</a> to see all your orders.</p>
        <div id="track-result" class="track-result" hidden></div>
      </div>
    </div>
  </section>
</main>
"""
    page("track.html", "Track your order", "Track a Little Hive House order with your order number and email.", None, body, ("orders.js",))


def page_thanks():
    body = f"""
<main id="main" data-page="thanks">
  <div class="wrap page-head thanks-head">
    <div class="thanks-seal" aria-hidden="true"><svg viewBox="0 0 60 60"><path d="M30 3l23.4 13.5v27L30 57 6.6 43.5v-27z" class="th-hex"/><path d="M19 30.5l7.5 7.5L42 22.5" class="th-tick"/></svg></div>
    <p class="eyebrow">Order placed</p>
    <h1 id="page-title">Thank you!</h1>
    <p class="lede" id="thanks-lede">Your order is in. We sent a receipt to your email.</p>
  </div>
  <section class="tight">
    <div class="wrap">
      {NOSCRIPT}
      {LOADING}
      <div id="st-content" hidden>
        <div class="thanks-grid">
          <div>
            <h2 class="sub-h">What happens next</h2>
            <ol class="steps">
              <li><div><h3>We make your magnets</h3><p>We print, press and pack every magnet by hand. Most orders ship within 3 to 5 business days.</p></div></li>
              <li id="thanks-pkg" hidden><div><h3>We plan your design together</h3><p>For big-order packages we email you within one business day to get your names, date, logo or photos, and send a proof to approve before we print.</p></div></li>
              <li><div><h3>You get a tracking link</h3><p>When your package ships we email you the USPS tracking link.</p></div></li>
              <li><div><h3>It arrives at your door</h3><p>Something not right? Tell us within 30 days and we’ll fix it. See our <a href="returns.html">returns policy</a>.</p></div></li>
            </ol>
            <div class="panel soon thanks-account" id="thanks-account" hidden>
              <span class="soon-hex" aria-hidden="true"></span>
              <div>
                <h2>Keep track of your orders</h2>
                <p>Create a free account to see your future orders and tracking in one place and save favorite designs.</p>
                <div class="row"><a class="btn btn-small" id="thanks-create" href="account.html?tab=create">Create an account</a><a class="btn btn-ghost btn-small" id="thanks-track" href="track.html">Track this order</a></div>
              </div>
            </div>
            <p class="thanks-more"><a class="btn btn-ghost btn-small" id="thanks-mine" href="orders.html">See your orders</a> <a class="btn btn-ghost btn-small" href="shop.html">Keep shopping</a></p>
          </div>
          <div class="thanks-order ocol side" id="thanks-order" hidden></div>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    page("thank-you.html", "Thank you", "Thank you for your order.", None, body, ("orders.js",), noindex=True)


# ------------------------------------------------------------------ favorites
def page_favorites():
    designs = {f'{c["slug"]}/{s}': [B.title_for(c, s), c["name"]] for c in B.COLLECTIONS for s in c["order"]}
    data = json.dumps(designs, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    body = f"""
<main id="main" data-page="favorites">
  {head_block([("Favorites", None)], "Your favorites", "Tap the heart on any magnet to save it here. Mix them into a set: any 3 designs are $12.",
              extra='''
    <div class="head-row"><span class="count" id="fav-count" aria-live="polite"></span><button type="button" class="btn btn-small btn-honey" id="fav-all" hidden>Add all to cart</button></div>''')}
  <section class="tight">
    <div class="wrap">
      <div class="fridge" hidden>
        <ul class="products four" id="fav-grid"></ul>
      </div>
      <div class="panel soon" id="fav-empty" hidden>
        <span class="soon-hex heart" aria-hidden="true"></span>
        <div>
          <h2>No favorites yet</h2>
          <p>Tap the heart on any magnet in the shop and it waits for you here.</p>
          <div class="row"><a class="btn btn-small" href="shop.html">Shop all designs</a><a class="btn btn-ghost btn-small" href="collections/index.html">Browse collections</a></div>
        </div>
      </div>
      <p class="note fav-sync" id="fav-sync" hidden><span data-guest>Your favorites are saved on this device. <a href="account.html?next=favorites.html">Sign in</a> to keep them on all your devices.</span><span data-signed hidden>Your favorites are saved to your account, so they show up on every device you sign in on.</span></p>
    </div>
  </section>
</main>
<script>window.LHH_DESIGNS={data};</script>
"""
    page("favorites.html", "Your favorites", "Your favorite Little Hive House magnet designs.", None, body, ("favorites.js",), noindex=True)


# ------------------------------------------------------------------ contact + unsubscribe
def page_contact():
    body = f"""
<main id="main" data-page="contact">
  {head_block([("Contact", None)], "Say hello", "Questions about an order, a custom idea or a big event? We’re two people in a little house near Atlanta, and we answer every message ourselves.")}
  <section class="tight">
    <div class="wrap contact-grid">
      <div class="contact-info">
        <ul class="perks">
          <li><strong>We reply within one business day</strong><span>Monday to Friday. Weekend messages get an answer on Monday.</span></li>
          <li><strong>Email us directly</strong><span><a href="mailto:{SUPPORT}">{SUPPORT}</a></span></li>
          <li><strong>Where’s my order?</strong><span><a href="track.html">Track it here</a> with your order number and email.</span></li>
          <li><strong>Something arrived damaged?</strong><span>Send a photo and we’ll reprint it or refund you. See <a href="returns.html">returns</a>.</span></li>
        </ul>
      </div>
      <div>
        <form class="panel contact-form" id="contact-form" novalidate>
          <div class="field"><label for="c-name">Your name</label><input id="c-name" name="name" autocomplete="name" required></div>
          <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" inputmode="email" required></div>
          <div class="field"><label for="c-topic">What’s it about?</label>
            <select id="c-topic" name="topic">
              <option value="order">An order I placed</option>
              <option value="photos">Photo magnets</option>
              <option value="big-order">A big order or event</option>
              <option value="wholesale">Wholesale or shops</option>
              <option value="other" selected>Something else</option>
            </select></div>
          <div class="field"><label for="c-order">Order number <small>if you have one</small></label><input id="c-order" name="order" placeholder="LHH-1042" autocomplete="off" autocapitalize="characters"></div>
          <div class="hp" aria-hidden="true"><label for="c-web">Leave this empty</label><input id="c-web" name="website" tabindex="-1" autocomplete="off"></div>
          <div class="field full"><label for="c-msg">Message</label><textarea id="c-msg" name="message" rows="6" required maxlength="5000"></textarea></div>
          <p class="msg full" id="contact-msg" role="alert" hidden></p>
          <div class="full contact-foot"><button type="submit" class="btn btn-honey">Send message</button><span class="hint" id="contact-hint">We’ll email you back within one business day.</span></div>
        </form>
        <div class="panel soon" id="contact-done" tabindex="-1" hidden>
          <span class="soon-hex ok" aria-hidden="true"></span>
          <div>
            <h2>Thanks, <span id="contact-done-name"></span>!</h2>
            <p>We got your message and will reply to <strong id="contact-done-email"></strong> within one business day.</p>
            <div class="row"><a class="btn btn-small" href="shop.html">Back to the shop</a></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    page("contact.html", "Contact us", "Contact Little Hive House. We reply within one business day.", None, body, ("forms.js",))


def page_unsubscribe():
    body = f"""
<main id="main" data-page="unsubscribe">
  {head_block([("Email preferences", None)], "Email preferences")}
  <section class="tight">
    <div class="wrap narrow" id="unsub">
      {NOSCRIPT}
      <div class="panel soon" id="un-ask" hidden>
        <span class="soon-hex" aria-hidden="true"></span>
        <div>
          <h2>Unsubscribe from our emails?</h2>
          <p>We’ll stop sending news and offers to <strong id="un-email"></strong>. You’ll still get emails about orders you place, like receipts and tracking.</p>
          <p class="msg" id="un-msg" role="alert" hidden></p>
          <div class="row"><button type="button" class="btn btn-small" id="un-go">Unsubscribe</button><a class="btn btn-ghost btn-small" href="index.html">Keep me on the list</a></div>
        </div>
      </div>
      <div class="panel soon" id="un-done" tabindex="-1" hidden>
        <span class="soon-hex ok" aria-hidden="true"></span>
        <div>
          <h2>You’re unsubscribed</h2>
          <p><strong id="un-done-email"></strong> won’t get marketing emails from us anymore. Sorry to see you go, and thank you for being here.</p>
          <div class="row"><a class="btn btn-small" href="shop.html">Visit the shop</a></div>
        </div>
      </div>
      <div class="panel soon" id="un-bad" hidden>
        <span class="soon-hex" aria-hidden="true"></span>
        <div>
          <h2>This link looks incomplete</h2>
          <p>Please use the unsubscribe link at the bottom of one of our emails, or write to <a href="mailto:{SUPPORT}?subject=Unsubscribe">{SUPPORT}</a> and we’ll take you off the list by hand.</p>
        </div>
      </div>
      <div class="panel soon" id="un-soon" hidden>
        <span class="soon-hex" aria-hidden="true"></span>
        <div>
          <h2>Want fewer emails?</h2>
          <p>Write to <a href="mailto:{SUPPORT}?subject=Unsubscribe">{SUPPORT}</a> and we’ll take you off the list right away.</p>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    page("unsubscribe.html", "Email preferences", "Unsubscribe from Little Hive House emails.", None, body, ("forms.js",), noindex=True)


# ------------------------------------------------------------------ policies
POLICIES = [("shipping.html", "Shipping"), ("returns.html", "Returns & refunds"), ("privacy.html", "Privacy"), ("terms.html", "Terms")]


def policy(path, title, desc, lede, sections):
    tabs = "".join(f'<a class="tab" href="{href}"{B.CUR if href == path else ""}>{E(t)}</a>' for href, t in POLICIES)
    toc = "".join(f'<li><a href="#{sid}">{E(h)}</a></li>' for sid, h, _ in sections)
    secs = "\n".join(f'<section id="{sid}" aria-labelledby="{sid}-h"><h2 id="{sid}-h">{E(h)}</h2>\n{html}\n</section>' for sid, h, html in sections)
    body = f"""
<main id="main" data-page="policy">
  {head_block([(title, None)], E(title), lede, eyebrow="Policies")}
  <div class="tabs-bar">
    <nav class="wrap tabs" aria-label="Policies">{tabs}</nav>
  </div>
  <section class="tight">
    <div class="wrap policy-grid">
      <nav class="policy-toc" aria-label="On this page"><p class="eyebrow">On this page</p><ol>{toc}</ol></nav>
      <article class="prose">
{secs}
        <p class="prose-foot">Last updated {UPDATED}. Questions? Email <a href="mailto:{SUPPORT}">{SUPPORT}</a> or use our <a href="contact.html">contact form</a>.</p>
      </article>
    </div>
  </section>
</main>
"""
    page(path, title, desc, None, body)


def page_policies():
    policy("shipping.html", "Shipping", "How Little Hive House makes and ships your order: production times, USPS Ground Advantage, costs and tracking.",
           "Every order is made by hand in our little house near Atlanta, Georgia, then sent with USPS.", [
        ("making", "How long it takes to make", """<p>Most orders are printed, pressed and packed within <strong>3 to 5 business days</strong> (Monday to Friday, not counting US holidays). Photo magnets take the same time.</p>
<p>Big-order packages (weddings, businesses, parties, teams) ship <strong>7 to 10 business days after you approve the proof</strong>. If you have a date in mind, tell us when you order and we’ll say honestly whether we can make it.</p>"""),
        ("delivery", "Delivery", """<p>We ship with <strong>USPS Ground Advantage</strong>, which usually arrives <strong>2 to 5 business days</strong> after it ships. Add the time to make your order and most packages arrive within one to two weeks.</p>
<p>We ship to addresses in the United States (including APO/FPO) and Canada. Canadian orders travel with USPS international service, usually take 1 to 3 weeks, and any customs fees are paid on delivery.</p>"""),
        ("cost", "Shipping cost", """<ul>
<li><strong>$4.95</strong> flat rate per order.</li>
<li><strong>Free</strong> when your order is $35 or more after discounts.</li>
</ul>
<p>The cart shows exactly how much more you need for free shipping, and the total you see at checkout is the total you pay.</p>"""),
        ("tracking", "Tracking your package", """<p>When your order ships we email you a tracking link. You can also see it any time on the <a href="track.html">track your order</a> page with your order number and email, or in <a href="account.html">your account</a> if you ordered while signed in.</p>"""),
        ("problems", "Late, lost or damaged packages", """<p>If tracking hasn’t moved for <strong>7 business days</strong>, or it says delivered but you can’t find it, check with neighbors and your mailroom first, then <a href="contact.html">write to us</a>. We’ll open a claim with USPS and send a replacement or a refund. You won’t be left waiting on the claim.</p>
<p>Something arrived broken? Send us a photo within 30 days and we’ll reprint it or refund you. See <a href="returns.html">returns &amp; refunds</a>.</p>"""),
        ("address", "Changing your address", """<p>Typed the wrong address? Email us as soon as you can with your order number. We can change it any time before the package ships. Once it ships we can’t redirect it, and packages returned to us for a wrong address are reshipped once the new shipping cost is paid.</p>"""),
    ])

    policy("returns.html", "Returns & refunds", "Little Hive House returns and refund policy: reprints or refunds for damaged or wrong items within 30 days.",
           "We want you to love every magnet. If something isn’t right, tell us within 30 days and we’ll make it right.", [
        ("promise", "Our promise", """<p>If your order arrives <strong>damaged, misprinted, defective or isn’t what you ordered</strong>, contact us within <strong>30 days of delivery</strong> and we’ll send a free reprint or give you a full refund for those items, your choice. You don’t need to send anything back. A photo of the problem is all we need.</p>"""),
        ("custom", "Custom and photo items", """<p>Photo magnets and big-order packages are made just for you from your photos, names or artwork, so we can’t take them back if you change your mind. We’ll always reprint or refund them if they arrive damaged or have a defect we caused, such as a printing error, a misaligned frame or a wrong caption.</p>
<p>Because we print exactly what you upload, blurry or low-resolution photos are not a defect. Our photo builder warns you when a photo looks too small, and if a photo looks like it will print poorly we try to let you know before we print it.</p>"""),
        ("change", "Changed your mind?", """<p>Ready-made designs from the shop can be returned unused, in their original packaging, within <strong>30 days of delivery</strong>. <a href="contact.html">Write to us</a> first and we’ll send the return address. Return shipping is paid by you, and we refund the price of the returned items once they reach us. Original shipping isn’t refunded.</p>"""),
        ("cancel", "Canceling an order", """<p>You can cancel for a full refund until we start making your order, usually within the first business day. Email us with your order number as soon as you can. Once printing has started we can’t cancel photo magnets or packages.</p>"""),
        ("how", "How refunds work", """<p>Refunds go back to your original payment method through Stripe, our payment processor. We email you when we issue a refund; it usually shows on your statement within <strong>5 to 10 business days</strong>, depending on your bank.</p>
<p>If you used a discount code, the refund is the amount you actually paid for those items.</p>"""),
        ("start", "Start a return or report a problem", """<ol>
<li>Email <a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a> or use the <a href="contact.html">contact form</a> within 30 days of delivery.</li>
<li>Include your order number (it looks like LHH&#8209;1042) and a photo if something is damaged or wrong.</li>
<li>We reply within one business day with a reprint, a refund or return instructions.</li>
</ol>"""),
    ])

    policy("privacy.html", "Privacy", "How Little Hive House collects, uses and protects your information and photos.",
           "We’re a two-person shop. We collect only what we need to make and ship your order, and we never sell your information.", [
        ("collect", "What we collect", """<ul>
<li><strong>Order details:</strong> your name, email, shipping address, phone number if you give one, what you ordered, gift messages and notes.</li>
<li><strong>Account details</strong> if you create an account: your name, email, a securely stored password (we can’t see it), your favorite designs and your email preference.</li>
<li><strong>Photos you upload</strong> for photo magnets, with the frames and captions you chose.</li>
<li><strong>Messages</strong> you send us through the contact or quote forms.</li>
</ul>
<p>We don’t collect or store your card number. Payments are handled entirely by Stripe.</p>"""),
        ("use", "How we use it", """<ul>
<li>To make, ship and support your order, and to send receipts, shipping updates and replies to your messages.</li>
<li>To send news and offers, <strong>only if you said yes</strong>. Every marketing email has an unsubscribe link, and you can also turn it off in your account.</li>
<li>To keep the shop safe, for example to prevent fraud, and to keep the records the law requires.</li>
</ul>
<p>We never sell or rent your information, and we don’t use advertising trackers.</p>"""),
        ("photos", "Your photos", """<p>Photos you upload are used <strong>only to print your order</strong>. We don’t share them, post them, use them in marketing or use them to train any AI. Only the two of us can see them.</p>
<p>Uploaded photos are <strong>deleted automatically 90 days after upload</strong>, which gives us time to make, ship and reprint if needed. Want them gone sooner? Email us and we’ll delete them right away.</p>"""),
        ("partners", "Services we use", """<p>We use a few trusted services to run the shop. Each one only gets what it needs:</p>
<ul>
<li><strong>Google Firebase</strong> stores customer accounts, orders and uploaded photos on secure Google Cloud servers, and runs the small programs behind checkout.</li>
<li><strong>Stripe</strong> processes payments and receives your payment and billing details directly. See <a href="https://stripe.com/privacy" rel="noopener">Stripe’s privacy policy</a>.</li>
<li><strong>Resend</strong> delivers our emails (receipts, shipping updates, password resets) and receives your email address and the message.</li>
<li><strong>USPS</strong> receives your name and address to deliver your package.</li>
<li><strong>Google Fonts</strong> serves the fonts on our website, which means your browser asks Google for them.</li>
</ul>"""),
        ("storage", "Cookies and storage on your device", """<p>We don’t use advertising or tracking cookies. Your browser keeps a few small things for you: your cart, your favorite designs, the light or dark theme, and, if you sign in, your sign-in session.</p>"""),
        ("keep", "How long we keep things", """<ul>
<li>Uploaded photos: 90 days, then deleted automatically.</li>
<li>Order records: 7 years, because tax and accounting rules require it.</li>
<li>Your account: until you ask us to delete it.</li>
<li>Email list: until you unsubscribe.</li>
</ul>"""),
        ("rights", "Your choices and rights", """<p>You can ask us to show you, correct or delete the information we have about you, or to close your account, by emailing <a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a>. We’ll answer within 30 days, usually much sooner. We keep only what the law requires us to keep, like order records for taxes.</p>
<p>Our shop isn’t meant for children under 13, and we don’t knowingly collect their information.</p>"""),
        ("changes", "Changes to this policy", """<p>If we change this policy in a way that matters, we’ll update the date below and, for big changes, email account holders.</p>"""),
    ])

    policy("terms.html", "Terms", "The terms for shopping at Little Hive House.",
           "The plain-English rules for shopping with us. By placing an order or creating an account you agree to them.", [
        ("who", "Who we are", """<p>Little Hive House is a small handmade business, a husband-and-wife studio near Atlanta, Georgia, USA. You can reach us at <a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a>.</p>"""),
        ("orders", "Orders and prices", """<p>Prices are in US dollars. Discounts (any 3 designs for $12, and 10%, 20% or 25% off orders of 20, 50 or 100+ magnets) are applied automatically, and the total is confirmed on the secure Stripe checkout page before you pay.</p>
<p>Your order is accepted once payment goes through and we email your confirmation. If we can’t make something, or a price was clearly wrong because of a mistake, we’ll tell you and refund you in full.</p>"""),
        ("custom", "Your photos and custom content", """<p>When you upload photos or send names, logos or artwork, you confirm that you took them or have permission to print them. You keep all rights to your content; you give us permission only to use it to make your order.</p>
<p>We may decline content that is hateful, explicit, violent, infringes someone else’s rights (like professional photos, logos or characters you don’t own) or is otherwise unlawful. If we decline an order, we refund it in full.</p>"""),
        ("proofs", "Big orders and proofs", """<p>For big-order packages we send a digital proof before printing. Please check names, dates and spelling carefully: we print exactly what you approve. Changes after approval may be charged as a new order.</p>"""),
        ("art", "Our designs", """<p>All designs in our shop are original artwork by Little Hive House. Buying a magnet lets you enjoy and give it; it doesn’t give you the right to copy, resell or reproduce the design.</p>"""),
        ("shipping", "Shipping, returns and refunds", """<p>Making times, delivery and shipping costs are explained in our <a href="shipping.html">shipping policy</a>. Damaged, defective and wrong items are covered by our <a href="returns.html">returns &amp; refunds policy</a>.</p>"""),
        ("accounts", "Accounts", """<p>Keep your password private and use an email address you check. You’re responsible for orders placed from your account. We may close accounts that are used for fraud or abuse.</p>"""),
        ("care", "Using your magnets", """<p>Our magnets are decorations for fridges and other metal surfaces. Keep them away from small children who might swallow them, and away from pacemakers, credit cards and electronics. Wipe with a dry or slightly damp cloth.</p>"""),
        ("liability", "Our responsibility", """<p>We stand behind our work as described in our returns policy. To the extent the law allows, our total responsibility for any order is limited to the amount you paid for it, and we aren’t responsible for indirect losses. Nothing in these terms limits rights you have under consumer protection laws.</p>"""),
        ("law", "Governing law and changes", """<p>These terms are governed by the laws of the State of Georgia, USA. We may update them from time to time; the version on this page when you place an order applies to that order.</p>"""),
    ])


def build(module):
    global B, E
    B = module
    E = module.E
    page_account()
    page_orders()
    page_order()
    page_track()
    page_thanks()
    page_favorites()
    page_contact()
    page_unsubscribe()
    page_policies()
