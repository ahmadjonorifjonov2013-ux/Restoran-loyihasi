// ============================================================
// SAVAT (cart) holatini boshqarish
// Holat URL manzilidagi ?cart=... parametridan o'qiladi va yoziladi.
// ============================================================

function serializeCart(cart) {
  return encodeURIComponent(JSON.stringify(cart || {}));
}

function deserializeCart(raw) {
  try {
    const parsed = JSON.parse(decodeURIComponent(raw));
    return (parsed && typeof parsed === 'object') ? parsed : {};
  } catch (err) {
    console.warn("Savat parametrini o'qib bo'lmadi:", err);
    return {};
  }
}

function readCartFromURL() {
  const params = new URLSearchParams(window.location.search);
  const raw = params.get('cart');
  if (!raw) return {};
  return deserializeCart(raw);
}

function cartTotalCount(cart) {
  return Object.values(cart || {}).reduce((sum, qty) => sum + Number(qty || 0), 0);
}

function cartTotalPrice(cart) {
  return Object.entries(cart || {}).reduce((sum, [id, qty]) => {
    const dish = typeof findDish === 'function' ? findDish(id) : null;
    if (!dish) return sum;
    const price = typeof field !== 'undefined' ? field.dishPrice(dish) : 0;
    return sum + (Number(price) || 0) * Number(qty || 0);
  }, 0);
}

function renderCartBadge(cart) {
  const badge = document.getElementById('cartCount');
  if (!badge) return;
  const total = cartTotalCount(cart);
  badge.textContent = total;
  badge.style.display = total > 0 ? '' : 'none';
}

function cartURL(base, cart) {
  const url = new URL(base, window.location.origin);
  if (Object.keys(cart || {}).length) {
    url.searchParams.set('cart', serializeCart(cart));
  } else {
    url.searchParams.delete('cart');
  }
  return url.pathname + url.search;
}

function refreshCartLinks(cart) {
  document.querySelectorAll('[data-cart-link]').forEach(link => {
    const base = link.getAttribute('data-cart-link');
    link.setAttribute('href', cartURL(base, cart));
  });
}

function syncURL(cart) {
  const url = new URL(window.location.href);
  if (Object.keys(cart || {}).length) {
    url.searchParams.set('cart', serializeCart(cart));
  } else {
    url.searchParams.delete('cart');
  }
  window.history.replaceState({}, '', url.pathname + url.search);
}

function removeFromCart(cart, id) {
  const next = { ...cart };
  delete next[id];
  return next;
}

function decrementCart(cart, id) {
  const next = { ...cart };
  if (!next[id]) return next;
  next[id] = Number(next[id]) - 1;
  if (next[id] <= 0) delete next[id];
  return next;
}

// Buyurtma berilgach savatni URL va xotiradan to'liq tozalash uchun funksiya
function clearCart() {
  const url = new URL(window.location.href);
  url.searchParams.delete('cart');
  window.history.replaceState({}, '', url.pathname + url.search);
  return {};
}