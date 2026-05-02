const rulesEl = document.getElementById('rules');
const categoriesEl = document.getElementById('categories');

async function load() {
  const res = await fetch('/api/manifest');
  if (!res.ok) {
    rulesEl.textContent = 'No se pudo cargar manifest. Ejecutá npm run build:data.';
    return;
  }
  const manifest = await res.json();

  rulesEl.innerHTML = `<p>Fuente: <code>${manifest.contentRoot}/rules</code></p><pre>${(manifest.rulesSummary || 'Sin resumen disponible.').replaceAll('\n','\n')}</pre>`;

  categoriesEl.innerHTML = '';
  for (const cat of manifest.categories) {
    const section = document.createElement('article');
    section.className = 'category';
    section.innerHTML = `<h3>${cat.category}</h3><div class="grid"></div>`;
    const grid = section.querySelector('.grid');

    for (const img of cat.images) {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `<img src="${img.url}" alt="${img.label}" /><p>${img.label}</p>`;
      grid.appendChild(card);
    }
    categoriesEl.appendChild(section);
  }
}

document.getElementById('classicBtn').addEventListener('click', () => document.body.classList.remove('wacky'));
document.getElementById('wackyBtn').addEventListener('click', () => document.body.classList.add('wacky'));

load();
