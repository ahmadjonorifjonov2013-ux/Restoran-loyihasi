/* =========================================================
   RESTORAN — savat holati
   Savat ma'lumoti sahifalar orasida URL query orqali uzatiladi
   (masalan: menyu.html?cart=101:2,103:1), shuning uchun sahifalarni
   ochish tartibi buzilmasa, savat saqlanib qoladi.
   ========================================================= */

function readCartFromURL(){
  const params = new URLSearchParams(location.search);
  const raw = params.get('cart');
  const cart = {};
  if(raw){
    raw.split(',').forEach(pair=>{
      const [id, qty] = pair.split(':');
      if(id && qty && Number(qty) > 0) cart[id] = Number(qty);
    });
  }
  return cart;
}

function serializeCart(cart){
  return Object.entries(cart)
    .filter(([,qty]) => qty > 0)
    .map(([id, qty]) => `${id}:${qty}`)
    .join(',');
}

function cartURL(page, cart){
  const s = serializeCart(cart);
  return s ? `${page}?cart=${encodeURIComponent(s)}` : page;
}

function cartCount(cart){
  return Object.values(cart).reduce((a,b)=>a+b,0);
}

/* Joriy sahifa manzilini savat holatiga mos yangilaydi (qayta yuklamasdan) */
function syncURL(cart){
  const s = serializeCart(cart);
  const url = s ? `${location.pathname}?cart=${encodeURIComponent(s)}` : location.pathname;
  history.replaceState(null, '', url);
}

/* Sahifadagi barcha ichki havolalarni (data-cart-link) joriy savat bilan yangilaydi */
function refreshCartLinks(cart){
  document.querySelectorAll('[data-cart-link]').forEach(a=>{
    const page = a.getAttribute('data-cart-link');
    a.setAttribute('href', cartURL(page, cart));
  });
}

function renderCartBadge(cart){
  const el = document.getElementById('cartCount');
  if(!el) return;
  const n = cartCount(cart);
  el.textContent = n;
  el.style.display = n > 0 ? 'flex' : 'none';
}