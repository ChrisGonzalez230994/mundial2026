# ⚽ Mundial 2026 — Dashboard en Vivo

Dashboard de seguimiento en tiempo real del FIFA World Cup 2026.  
Datos automáticos via **api-football.com** · Hosting gratis en **GitHub Pages**.

## Qué incluye

- ⚡ Partidos en vivo con marcador actualizado
- 📊 Tabla de posiciones por grupo (grupos A–L)
- ✅ Últimos resultados
- 📅 Próximos partidos
- ⚽ Tabla de goleadores
- 🔄 Auto-actualización cada 60 seg (partidos en vivo) / 5 min (resto)

## Arquitectura

```
GitHub Actions (cada 5 min)
    └── scripts/fetch_data.py
         └── llama a api-football.com con RAPIDAPI_KEY (Secret)
         └── guarda en data/worldcup.json
         └── commitea al repo

index.html (GitHub Pages)
    └── fetch a ./data/worldcup.json cada 60 seg
    └── renderiza sin necesidad de backend
```

La API key **nunca se expone** en el HTML público — queda guardada como Secret en GitHub.

---

## Setup paso a paso

### 1. Fork / clonar el repo

```bash
git clone https://github.com/TU_USUARIO/mundial2026.git
cd mundial2026
```

### 2. Agregar la API Key como GitHub Secret

1. Ir a tu repo → **Settings** → **Secrets and variables** → **Actions**
2. Click en **New repository secret**
3. Nombre: `RAPIDAPI_KEY`
4. Valor: tu key de [api-football.com en RapidAPI](https://rapidapi.com/api-sports/api/api-football)
5. Guardar

### 3. Verificar el League ID del Mundial 2026

En api-football.com, el ID del torneo puede variar. Verificarlo:

```python
# Correr localmente para ver IDs disponibles
RAPIDAPI_KEY=tu_key python -c "
import requests
r = requests.get(
    'https://api-football-v1.p.rapidapi.com/v3/leagues',
    headers={'x-rapidapi-host':'api-football-v1.p.rapidapi.com','x-rapidapi-key':'TU_KEY'},
    params={'name':'World Cup','season':2026}
)
for l in r.json()['response']:
    print(l['league']['id'], l['league']['name'])
"
```

Una vez que tenés el ID correcto, actualizar en `scripts/fetch_data.py`:

```python
WC_LEAGUE_ID = 1   # <-- reemplazar con el ID real del Mundial 2026
```

### 4. Habilitar GitHub Pages

1. Ir a tu repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / Folder: `/ (root)`
4. Guardar → en unos minutos tu sitio estará en `https://TU_USUARIO.github.io/mundial2026`

### 5. Habilitar GitHub Actions

El workflow se habilita automáticamente. Para verificar:

1. Ir a **Actions** en tu repo
2. Deberías ver el workflow **Fetch World Cup Data**
3. Si no está activo, hacer click en **Enable workflow**

### 6. Primer run manual

Para no esperar 5 minutos:

1. **Actions** → **Fetch World Cup Data** → **Run workflow**
2. Verificar que `data/worldcup.json` se actualizó

---

## Notas sobre el plan gratuito de RapidAPI

El plan gratuito de api-football.com tiene **100 requests/día**.

Con el workflow corriendo cada 5 minutos: 60/5 × 24 = **288 requests/día** → excede el límite.

**Opciones:**

| Opción | Costo | Requests |
|--------|-------|----------|
| Free   | $0    | 100/día  |
| Basic  | $15/mes | 3.000/día |
| Pro    | $35/mes | 7.500/día |

**Recomendación para el Mundial:** el plan Basic ($15/mes) es suficiente.  
Alternativamente, ajustar el cron a `*/30 * * * *` (cada 30 min) para mantenerse en el free tier.

---

## Estructura del repo

```
mundial2026/
├── index.html                  # Dashboard principal
├── data/
│   └── worldcup.json           # Datos auto-generados por Actions
├── scripts/
│   └── fetch_data.py           # Script que llama a la API
└── .github/
    └── workflows/
        └── fetch_worldcup.yml  # GitHub Actions workflow
```

---

## Créditos

- Datos: [api-football.com](https://api-football.com)
- Hosting: [GitHub Pages](https://pages.github.com)
- Automatización: [GitHub Actions](https://github.com/features/actions)
