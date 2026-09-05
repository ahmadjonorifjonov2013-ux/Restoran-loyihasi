// Taomlar va kategoriyalar uchun global massivlar
let CATS = [];
let DISHES = [];

// Backend Serializer reponzidagi kalit so'zlarga mos keluvchi yordamchi obyekt
const field = {
  catId: c => c.id,
  catName: c => c.nom || c.name || c.title,
  dishId: d => d.id,
  dishCat: d => d.kategoriya || d.category || (d.category_id ? d.category_id : d.kategoriya_id),
  dishName: d => d.nom || d.name || d.title,
  dishDesc: d => d.tavsif || d.description || '',
  dishPrice: d => d.narx || d.price || 0,
  dishImg: d => d.rasm || d.image || null
};

// Summani chiroyli formatda chiqarish (masalan: 25 000)
function fmt(num) {
  return Number(num || 0).toLocaleString('ru-RU');
}

// Rasm bo'lmagan taomlar uchun standart SVG tasvir
function plateSVG(id) {
  return `
    <svg viewBox="0 0 100 100" class="plate-placeholder">
      <circle cx="50" cy="50" r="45" fill="none" stroke="#d4a94a" stroke-width="2"/>
      <circle cx="50" cy="50" r="35" fill="none" stroke="#333" stroke-width="1" stroke-dasharray="4 2"/>
      <path d="M35 50 Q50 35 65 50 Q50 65 35 50" fill="#c1440e" opacity="0.4"/>
    </svg>
  `;
}

// Backend API'dan ma'lumotlarni yuklab olish funksiyasi (/api/ prefiksiz)
async function loadMenuData() {
  try {
    const [catRes, dishRes] = await Promise.all([
      fetch('/categories/'),
      fetch('/dishes/')
    ]);

    if (!catRes.ok || !dishRes.ok) {
      throw new Error(`Server xatosi: Kategoriyalar statusi (${catRes.status}), Taomlar statusi (${dishRes.status})`);
    }

    const catData = await catRes.json();
    const dishData = await dishRes.json();

    // Agar Django REST Framework pagination ishlatsa (results) yoki to'g'ridan-to'g me'yoriy list qaytsa:
    CATS = Array.isArray(catData) ? catData : (catData.results || []);
    DISHES = Array.isArray(dishData) ? dishData : (dishData.results || []);

  } catch (err) {
    console.error("Menyu ma'lumotlarini yuklashda xatolik yuz berdi:", err);
    CATS = [];
    DISHES = [];
  }
}