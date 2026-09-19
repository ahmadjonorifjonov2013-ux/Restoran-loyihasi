// Taomlar va kategoriyalar uchun global massivlar (dastlab keshdan o'qiladi)
let CATS = JSON.parse(localStorage.getItem('RESTO_CATS') || '[]');
let DISHES = JSON.parse(localStorage.getItem('RESTO_DISHES') || '[]');

// Backend serializerdagi kalit so'zlarga mos keluvchi yordamchi obyekt
const field = {
  catId: c => c.id,
  catName: c => c.nom || c.name || c.title,
  dishId: d => d.id,
  dishCat: d => d.kategoriya || d.category || (d.category_id ? d.category_id : d.kategoriya_id),
  dishName: d => d.nom || d.name || d.title,
  dishDesc: d => d.tavsif || d.description || '',
  dishPrice: d => d.narx || d.price || 0,
  dishImg: d => d.rasm || d.image || null,
  dishCatName: d => d.kategoriya_nomi || d.category_name || d.kategoriya?.nom || '',
  dishTime: d => d.tayyorlash_vaqti || d.prep_minutes || 0
};

// Summani chiroyli formatda chiqarish (masalan: 25 000)
function fmt(num) {
  return Number(num || 0).toLocaleString('ru-RU');
}

// ID bo'yicha taomni topish yordamchisi (cart.js va savat.html uchun kerak)
function findDish(id) {
  return DISHES.find(d => String(field.dishId(d)) === String(id));
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

// Backend API'dan ma'lumotlarni yuklab olish va KESHGA saqlash.
// Xatolik bo'lsa shu yerda ushlanmaydi — chaqiruvchi (.then/.catch) o'zi
// hal qiladi, shunda menyu.html/savat.html foydalanuvchiga xabar bera oladi.
async function loadMenuData() {
  const [resCats, resDishes] = await Promise.all([
    fetch('/categories/'),
    fetch('/dishes/')
  ]);

  if (!resCats.ok || !resDishes.ok) {
    throw new Error(`Server xatosi: kategoriyalar (${resCats.status}), taomlar (${resDishes.status})`);
  }

  const catData = await resCats.json();
  const dishData = await resDishes.json();

  CATS = Array.isArray(catData) ? catData : (catData.results || []);
  DISHES = Array.isArray(dishData) ? dishData : (dishData.results || []);

  localStorage.setItem('RESTO_CATS', JSON.stringify(CATS));
  localStorage.setItem('RESTO_DISHES', JSON.stringify(DISHES));
}