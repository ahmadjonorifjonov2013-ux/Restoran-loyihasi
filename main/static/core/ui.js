// ============================================================
// UI YORDAMCHILARI: scroll-reveal, sticky header, toast, marquee
// ============================================================

(function () {

  // 1. STICKY HEADER — scroll'da ixchamlashadi
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('scrolled', window.scrollY > 24);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // 2. BACK-TO-TOP tugmasi
  const toTop = document.querySelector('.to-top');
  if (toTop) {
    window.addEventListener('scroll', () => {
      toTop.classList.toggle('show', window.scrollY > 600);
    }, { passive: true });
    toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // 3. SCROLL-REVEAL — elementlar ko'ringanda sekin paydo bo'ladi
  const revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  // 4. MARQUEE — izni ikki barobarga ko'paytiradi (uzluksiz aylanish uchun)
  document.querySelectorAll('.ribbon').forEach(function (ribbon) {
    const track = ribbon.querySelector('.ribbon-track');
    if (!track || track.children.length === 0) return;
    const clone = track.cloneNode(true);
    ribbon.appendChild(clone);
  });

})();

// Toast bildirishnoma (savatga qo'shilganda)
function showToast(message) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.innerHTML = '<span class="tick">✓</span>' + message;
  toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove('show'), 2200);
}