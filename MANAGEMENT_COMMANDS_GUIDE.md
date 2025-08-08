# Management Commands สำหรับ Sample Data

## คำสั่งที่มีให้ใช้งาน

### 1. `load_sample_data` 
โหลดข้อมูลตัวอย่างพื้นฐาน 3 บริษัท (Demo Companies)

```bash
# โหลดข้อมูลพื้นฐาน
python manage.py load_sample_data

# โหลดข้อมูลแม้ว่าจะมีข้อมูลอยู่แล้ว
python manage.py load_sample_data --force
```

**ข้อมูลที่สร้าง:**
- EcoPack Demo (Startup)
- Demo Ventures (Investor) 
- Demo Corporation (Corporate)

### 2. `load_full_sample_data`
โหลดข้อมูลตัวอย่างครบถ้วน 15 บริษัท (Production Sample Data)

```bash
# โหลดข้อมูลครบถ้วน
python manage.py load_full_sample_data

# โหลดข้อมูลแม้ว่าจะมีข้อมูลอยู่แล้ว
python manage.py load_full_sample_data --force
```

**ข้อมูลที่สร้าง:**
- **5 Startups**: EcoPack Thailand, PlasticFree Solutions, OceanClean Indonesia, CircularPack Malaysia, GreenTech Philippines
- **5 Investors**: SEA Seed Ventures, Green Impact Fund, Asia Climate Capital, Circular Ventures Asia, Pacific Green Partners
- **5 Corporates**: Unilever SEA, Nestlé Thailand, SCG, Grab Holdings, CP Group

### 3. `check_sample_data`
ตรวจสอบสถานะข้อมูลตัวอย่างในฐานข้อมูล

```bash
python manage.py check_sample_data
```

**ผลลัพธ์:**
- จำนวนบริษัททั้งหมด
- จำนวนแยกตามประเภท (Startup/Investor/Corporate)
- รายชื่อบริษัทตัวอย่าง

## การใช้งานใน Railway

### Production Deployment
Railway จะรัน `load_full_sample_data --force` อัตโนมัติในขั้นตอน deployment:

```bash
python manage.py migrate
python manage.py load_full_sample_data --force
python manage.py collectstatic --noinput
gunicorn seamap.wsgi:application
```

### Manual Commands ใน Railway
```bash
# เข้าไป Railway shell
railway shell

# ตรวจสอบข้อมูล
python manage.py check_sample_data

# โหลดข้อมูลใหม่
python manage.py load_full_sample_data --force
```

## Logic การทำงาน

### `load_sample_data`
- ตรวจสอบว่ามี demo companies อยู่แล้วหรือไม่
- ถ้ามี >=3 demo companies แล้ว จะไม่สร้างใหม่ (ยกเว้นใช้ --force)
- ถ้ามีบริษัทอื่นแต่ไม่มี demo companies จะสร้าง demo companies

### `load_full_sample_data`
- ตรวจสอบว่ามี sample companies ชื่อเฉพาะอยู่แล้วหรือไม่
- ถ้ามี >=10 sample companies แล้ว จะไม่สร้างใหม่ (ยกเว้นใช้ --force)
- สร้างข้อมูลครบถ้วน 15 บริษัทในครั้งเดียว

## ข้อมูลที่สร้างขึ้น

### Startup Companies (5)
1. **EcoPack Thailand** - Biodegradable packaging from agricultural waste
2. **PlasticFree Solutions** - B2B sustainable packaging platform
3. **OceanClean Indonesia** - Marine robots for plastic waste collection
4. **CircularPack Malaysia** - Plastic waste recycling and remanufacturing
5. **GreenTech Philippines** - Enzyme-based plastic biodegradation

### Investor Companies (5)
1. **SEA Seed Ventures** - Early-stage VC focused on climate tech
2. **Green Impact Fund** - Impact investment fund for sustainability
3. **Asia Climate Capital** - Growth-stage climate technology VC
4. **Circular Ventures Asia** - Circular economy investment specialist
5. **Pacific Green Partners** - Angel investor network for environmental tech

### Corporate Companies (5)
1. **Unilever Southeast Asia** - Multinational consumer goods
2. **Nestlé Thailand** - Food & beverage giant with sustainability focus
3. **SCG (Siam Cement Group)** - Industrial conglomerate
4. **Grab Holdings** - Super-app with sustainable transportation
5. **Charoen Pokphand Group** - Agribusiness and sustainable development

## Troubleshooting

### ปัญหาที่อาจพบ:
```bash
# หากได้ error เกี่ยวกับ database
python manage.py check --database default

# หากได้ error เกี่ยวกับ migrations
python manage.py showmigrations

# หากต้องการลบข้อมูลเก่าทั้งหมด
python manage.py flush
python manage.py load_full_sample_data
```

### การตรวจสอบข้อมูล:
```bash
# ตรวจสอบผ่าน Django shell
python manage.py shell
>>> from member.models import Company
>>> Company.objects.count()
>>> Company.objects.filter(company_type='startup').count()
```
