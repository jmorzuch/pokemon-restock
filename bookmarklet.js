// Pokemon Restock - bookmarklet (run inside your real Chrome on a Target product page)
//
// HOW TO INSTALL (once):
//   1. Copy the ONE-LINER below.
//   2. In Chrome: right-click the bookmarks bar -> Add page...
//        Name:  Pokemon Restock Watch
//        URL:   <the one-liner, starts with javascript: >
//   3. Open the Target product page you want to watch (your normal logged-in tab).
//   4. Click the bookmark. It starts polling the page every 25s.
//   5. The instant the page flips to IN STOCK, it pings the local receiver
//      (127.0.0.1:8787) which fires your Telegram alert.
//
// NOTE: keep this tab open while you're waiting. Closing it stops the watcher.
// Open a new tab for the same product and click the bookmark again to resume.

// ---------- ONE-LINER (paste into the bookmark URL) ----------
javascript:(function(){var P=8787;var N=document.title.replace(/\s*:\s*Target.*$/,'').trim()||'Target product';function read(){var t=document.body?document.body.innerText:'';if(!t)return'?';if(/out of stock|sold out/i.test(t))return'OUT';var b=document.querySelector('[data-qa="add-to-cart"],[data-test-id="add-to-cart"],.action-button-add-to-cart,button[data-qa="add-to-cart"]');if(b&&!b.disabled)return'IN';if(/add to cart/i.test(t)||/only\s*\d+\s*left/i.test(t))return'IN';if(/preorder|pre-order|\barrives\b/i.test(t))return'PRE';return'?';}var last='?';function tick(){var s=read();if(s==='IN'&&last!=='IN'){fetch('http://127.0.0.1:'+P+'/alert',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:N,url:location.href,in_stock:true})}).then(function(r){return r.json();}).then(function(j){console.log('[restock] alerted ->',j);}).catch(function(e){console.warn('[restock] alert failed',e);});}last=s;console.log('[restock] state=',s);}if(window.__restockTimer)clearInterval(window.__restockTimer);tick();window.__restockTimer=setInterval(tick,25000);console.log('[restock] watching:',N);})();

// ---------- READABLE VERSION (same logic, for reference) ----------
(function () {
  var P = 8787;
  var N = (document.title || '').replace(/\s*:\s*Target.*$/, '').trim() || 'Target product';

  function read() {
    var t = document.body ? document.body.innerText : '';
    if (!t) return '?';
    if (/out of stock|sold out/i.test(t)) return 'OUT';
    var b = document.querySelector(
      '[data-qa="add-to-cart"],[data-test-id="add-to-cart"],' +
      '.action-button-add-to-cart,button[data-qa="add-to-cart"]');
    if (b && !b.disabled) return 'IN';
    if (/add to cart/i.test(t) || /only\s*\d+\s*left/i.test(t)) return 'IN';
    if (/preorder|pre-order|\barrives\b/i.test(t)) return 'PRE';
    return '?';
  }

  var last = '?';
  function tick() {
    var s = read();
    if (s === 'IN' && last !== 'IN') {
      fetch('http://127.0.0.1:' + P + '/alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: N, url: location.href, in_stock: true }),
      })
        .then(function (r) { return r.json(); })
        .then(function (j) { console.log('[restock] alerted ->', j); })
        .catch(function (e) { console.warn('[restock] alert failed', e); });
    }
    last = s;
    console.log('[restock] state=', s);
  }

  if (window.__restockTimer) clearInterval(window.__restockTimer);
  tick();
  window.__restockTimer = setInterval(tick, 25000);
  console.log('[restock] watching:', N);
})();
