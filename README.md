<div align="center">
  <img src="frontend/src/assets/brand/civis-logo.svg" alt="CiVis logotipas" width="120" />

  <h1>CiVis</h1>

  <p><strong>Darbo paieška ir kandidatų atranka vienoje vietoje.</strong></p>

  <p>
    Platforma padeda darbo ieškantiems asmenims pristatyti savo patirtį,
    o darbdaviams — patogiai valdyti įmonės skelbimus ir paraiškas.
  </p>
</div>

---

## Kas yra CiVis?

**CiVis** — tai internetinė įdarbinimo platforma, sujungianti darbo ieškančius žmones
ir darbdavius. Svarbiausia platformos savybė — **dirbtiniu intelektu grįstas kandidatų
ir skelbimų suderinamumo įvertinimas**: sistema automatiškai perskaito kandidato CV,
išskiria jo įgūdžius ir apskaičiuoja, kaip gerai jis atitinka konkretų darbo pasiūlymą
(įvertinimas nuo 0 iki 100).

Taip darbo ieškantis asmuo iš karto mato, kur jo profilis tinka labiausiai, o darbdavys
gauna pagal atitikimą surikiuotą kandidatų sąrašą ir sutaupo laiko atrankai.

## Kam skirta platforma?

### 👤 Darbo ieškantiems asmenims
- Susikurti profilį ir įkelti savo CV (PDF formatu).
- Dirbtinis intelektas automatiškai išanalizuoja CV ir išskiria įgūdžius.
- Naršyti atvirus darbo skelbimus ir matyti savo **atitikimo įvertinimą** kiekvienam iš jų.
- Pateikti paraiškas ir patogiai sekti jų būseną (laukiama, priimta, atmesta).

### 🏢 Darbdaviams
- Sukurti įmonės profilį ir skelbti darbo pasiūlymus.
- Aprašyti reikalaujamus bei pageidaujamus įgūdžius.
- Matyti visus kandidatus, **surikiuotus pagal atitikimą** skelbimui.
- Ieškoti, rūšiuoti, archyvuoti paraiškas ir keisti jų būseną.

## Kaip veikia atitikimo įvertinimas?

1. **CV analizė** — įkeltas CV perskaitomas ir dirbtinis intelektas iš teksto išskiria
   įgūdžius (techninius, socialinius bei patirtį).
2. **Reikšminis palyginimas** — kiekvienas įgūdis paverčiamas skaitine „reikšmės išraiška“
   (angl. *embedding*), leidžiančia palyginti prasmę, o ne tik tikslius žodžius
   (pvz. „JS“ ir „JavaScript“ atpažįstami kaip tas pats).
3. **Įvertinimo skaičiavimas** — pagal skelbimo reikalavimus apskaičiuojamas galutinis
   0–100 balo suderinamumo įvertinimas, atsižvelgiant į privalomus įgūdžius, jų svarbą
   ir bendrą CV aktualumą.

## Technologijos

Projektas sukurtas naudojant šiuolaikinį atvirojo kodo technologijų rinkinį ir yra
visiškai paruoštas paleisti su **Docker**.

| Sritis | Technologijos |
| --- | --- |
| **Vartotojo sąsaja** (frontend) | Vue 3, TypeScript, Vue Router, Tailwind CSS, Vite |
| **Serverio dalis** (backend) | Python, Django, Django REST Framework |
| **Duomenų bazė** | PostgreSQL su [`pgvector`](https://github.com/pgvector/pgvector) plėtiniu (reikšmių paieškai) |
| **Dirbtinis intelektas** | OpenAI (CV įgūdžių išskyrimas ir reikšmės išraiškos) |
| **Failų saugykla** | MinIO / S3 (CV dokumentams) |
| **Mokėjimai** | Stripe |
| **Infrastruktūra** | Docker, Docker Compose |

## Paleidimas

> Reikalinga įdiegti [Docker ir Docker Compose](https://docs.docker.com/get-docker/).

```bash
# Sukurti ir paleisti visus servisus
docker compose up --build

# Pirmą kartą — atlikti duomenų bazės migracijas
docker compose exec backend python manage.py migrate

# (Neprivaloma) Sukurti administratoriaus paskyrą
docker compose exec backend python manage.py createsuperuser
```

Paleidus, platforma pasiekiama šiais adresais:

| Servisas | Adresas |
| --- | --- |
| Vartotojo sąsaja | http://localhost:5173 |
| API | http://localhost:8000/api/ |
| Administravimas | http://localhost:8000/admin/ |

## Dokumentacija kūrėjams

Išsamesnė techninė informacija — projekto struktūra, kūrimo darbo eiga, kodo formatavimas,
API ir maršrutų (Vue Router) aprašymai — pateikta faile [`guide.md`](guide.md).

---

<div align="center">
  <sub>CiVis — sujungiame tinkamus žmones su tinkamu darbu.</sub>
</div>
