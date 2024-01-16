# NEXT LABS
Interaktivní Platforma pro Výuku

**NEXT LABS** je platforma inspirována funkcionalitou TryHackMe a správou serverů na styl Pterodactyl Panelu. Cílem je nabídnout uživatelům moderní a flexibilní prostředí pro učení a praxi v oblasti IT.


Projekt je rozdělen do 3 hlavních částí:
- **Frontend** - Next.js
- **Backend** - Docker API
- **Databáze** - Prisma


V Prosinci jsem testoval knihovnu `dockerode`. Použil jsem jednoduchý express server. Díky němu dokážu vytvářet, spouštět, zastavovat a mazat kontejnery. Při použití v Next.js se projekt nepostavil. Problém stále řeším. Při nejhorším zkusím jinou knihovnu. Další možnosti jsou použití externí express api. Poslední možnost je použití Docker Engine REST API


## Použité technologie:
- Next.js
- Tailwind
- Auth.js
- Prisma
- Docker

## Rozpis cílů
### Říjen
Docker CLI
- Vytvoření kontejneru
- Start / Stop kontejneru
- Snapshot kontejneru
- Spuštění příkazu
- Logy
- Kopírování souborů
- Uspěšné vytvoření a spuštění 3 různých Docker kontejnerů

### Listopad
Docker Dockerfile
- Stažení os image
- Image update
- Tagy
- Argumenty
- Mount souboru do kontejneru

Compose file
- Volumes
- Networks
- Restart
- Environment
- Image
- Ports
- Services
- Deploy

### Prosinec
Docker Compose
- Sestavení skupiny služeb
- Zobrazení logů

Docker API
- Vytvoření kontejneru
- Zastavení kontejneru
- Restart kontejneru
- Smazání kontejneru
- Filtrování kontejneru 

### Leden
Základy Next.js
- ToDo app pro nauceni zakladu
- Napojeni na Databazi
- Databazove Modely

### Únor
- Stylování ToDo app side projektu pro naučení Tailwind CSS
- Uživatelské rozhraní pomocí Tailwind CSS s responzivním designem pro minimálně 3 různé rozměry obrazovky

### Březen
- Implementace NextAuth.js
- Third Party Login
- Správa uživatelů

### Duben
Spojení Docker API a Next.js, Endpointy:
- Status serveru
- Kill serveru
- List dostupných imagů
- Spuštění image

Zabezpečení API s minimálně 2 metodami (např. token autentizace, rate limiting)

### Květen
- Tvorba contentu pro moduly
- QA TESTING - Získání zpětné vazby od 5 testujících uživatelů

### Červen
- Další 2 moduly
- Live deploy
- Monitorování platformy a problémů v reálném čase


Do budoucna:
Implementace vizualizace datových sítí -> eve-ng nebo Kathara