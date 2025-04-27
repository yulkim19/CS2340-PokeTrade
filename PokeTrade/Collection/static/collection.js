const modal       = document.querySelector('.modal');
const modalTitle  = document.querySelector('.modal-title');
const modalImage  = document.querySelector('.modal-image');
const searchInput = document.getElementById("search-field");
const searchButton = document.getElementById("search-button");
const autocompleteList = document.getElementById("autocomplete-list");
const pokemonCards = document.querySelectorAll('.pokemon-card');
const pokemonNames = Array.from(pokemonCards).map(card => card.getAttribute('data-name'));

document.querySelectorAll('.pokemon-card').forEach(card => {
  card.addEventListener('click', () => {
    modalTitle.textContent = `${card.dataset.name} (Rarity: ${card.dataset.rarity})`;
    modalImage.src = card.dataset.sprite;
    modalImage.alt = card.dataset.name;
    modal.showModal();

    localStorage.setItem('offered_pokemon_name', card.dataset.name);
    localStorage.setItem('offered_pokemon_sprite', card.dataset.sprite);
    localStorage.setItem('offered_pokemon_rarity', card.dataset.rarity);
  });
});

modal.addEventListener('click', e => { if (e.target === modal) modal.close(); });
window.addEventListener('keydown', e => { if (e.key === 'Escape' && modal.open) modal.close(); });

const pokemonName = localStorage.getItem('offered_pokemon_name');
const tradeButton = document.querySelector('.modal-content .nes-btn.is-primary');
if (tradeButton && pokemonName) {
    tradeButton.addEventListener('click', () => {
        window.location.href = `/trading/create_trade/${pokemonName}/`;
    });
}

const SPRITES = [
  { cls:'tree-big-1',   w:70, h:88,  sway:true  },
  { cls:'tree-big-2',   w:85, h:107, sway:true  },
  { cls:'tree-big-3',   w:75, h:104, sway:true  },
  { cls:'tree-pine',    w:66, h:128, sway:true  },
  { cls:'tree-dead',    w:66, h:99,  sway:true  },
  { cls:'tree-small-1', w:43, h:58,  sway:false },
  { cls:'tree-small-2', w:61, h:88,  sway:false },
  { cls:'log',          w:32, h:16,  sway:false }
];

function spawnDecorations() {
  const layer = document.getElementById('bg-layer');
  if (!layer) return;

  const vw = window.innerWidth, vh = window.innerHeight;
  const count = Math.floor(Math.random()*7)+16;

  for (let i=0;i<count;i++) {
    const spec = SPRITES[Math.floor(Math.random()*SPRITES.length)];
    const el   = document.createElement('div');
    el.className = `bg-sprite ${spec.cls}` + (spec.sway ? ' sway':'');
    el.style.left = Math.random()*(vw-spec.w)+'px';
    el.style.top  = Math.random()*(vh-spec.h)+'px';
    layer.appendChild(el);
  }
}

function spawnRunner() {
  const pool = [...document.querySelectorAll('.pokemon-sprite')].map(i => i.src);
  if (!pool.length) return;

  const active = new Set(
    [...document.querySelectorAll('img.runner')].map(r => r.src)
  );

  const available = pool.filter(src => !active.has(src));
  if (!available.length) return;

  const runner = document.createElement('img');
  runner.src        = available[Math.floor(Math.random() * available.length)];
  runner.className  = 'runner';

  const SIZE = 96;
  const vw = window.innerWidth, vh = window.innerHeight;

  const inside = () => ({
    x: Math.random() * (vw - SIZE),
    y: Math.random() * (vh - SIZE)
  });

  let start;
  const edge = Math.floor(Math.random() * 4);
  switch (edge) {
    case 0: start = { x: -SIZE,    y: Math.random() * vh }; break;
    case 1: start = { x: vw + SIZE, y: Math.random() * vh }; runner.dataset.flip = '1'; break;
    case 2: start = { x: Math.random() * vw, y: -SIZE }; break;
    case 3: start = { x: Math.random() * vw, y: vh + SIZE }; break;
  }

  const hops = Math.floor(Math.random() * 4) + 2;
  const pts  = [start];
  for (let i = 0; i < hops; i++) pts.push(inside());
  const last = pts[pts.length - 1];
  pts.push({
    x: last.x < vw / 2 ? -SIZE : vw + SIZE,
    y: last.y < vh / 2 ? -SIZE : vh + SIZE
  });

  runner.style.left = start.x + 'px';
  runner.style.top  = start.y + 'px';
  document.body.appendChild(runner);

  const applyFlip = dirX => runner.style.transform = dirX < 0 ? 'scaleX(-1)' : '';

  const animateTo = (dx, dy, ms) =>
    runner.animate(
      [
        { transform: 'translate(0,0)' },
        { transform: `translate(${dx}px, ${dy}px)` }
      ],
      { duration: ms, easing: 'linear', fill: 'forwards' }
    ).finished;

  (async () => {
    for (let i = 1; i < pts.length; i++) {
      const dx = pts[i].x - pts[i - 1].x;
      const dy = pts[i].y - pts[i - 1].y;
      const dist = Math.hypot(dx, dy);
      const ms   = dist * 12 + 800;

      applyFlip(dx);
      await animateTo(dx, dy, ms);

      runner.style.left = pts[i].x + 'px';
      runner.style.top  = pts[i].y + 'px';
      runner.style.transform = runner.style.transform.includes('scaleX') ? runner.style.transform : '';
    }
    runner.remove();
  })();
}

function delay(){ return Math.random()*6000 + 6000; }
function startLoop(){
  setTimeout(function loop(){
    if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      spawnRunner();
    }
    setTimeout(loop, delay());
  }, delay());
}

window.addEventListener('load', ()=>{
  spawnDecorations();
  window.addEventListener('resize',()=>{
    const layer=document.getElementById('bg-layer');
    if(layer){ layer.innerHTML=''; spawnDecorations(); }
  });
  startLoop();
});

searchButton.addEventListener("click", function () {
    const search = searchInput.value.trim().toLowerCase();
    if (!search) return;

    let found = false;
    pokemonCards.forEach(card => {
        const name = card.getAttribute("data-name").toLowerCase();
        if (name.includes(search)) {
            card.click();
            found = true;
        }
    });
    if (!found) {
        alert("No Pokemon found for: " + search);
    }
});

searchInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        searchButton.click();
    }
});

searchInput.addEventListener("input", function () {
    const query = this.value.trim().toLowerCase();
    autocompleteList.innerHTML = "";

    if (!query) return;

    const matchingNames = pokemonNames.filter(name =>
        name.toLowerCase().startsWith(query)
    );

    matchingNames.forEach(name => {
        const suggestion = document.createElement("div");
        suggestion.textContent = name;
        suggestion.classList.add('autocomplete-item');


        suggestion.addEventListener("click", function () {
            searchInput.value = name;
            autocompleteList.innerHTML = "";
        });

        autocompleteList.appendChild(suggestion);
    });
});

document.addEventListener("click", (e) => {
    if (!autocompleteList.contains(e.target) && e.target !== searchInput) {
        autocompleteList.innerHTML = "";
    }
});