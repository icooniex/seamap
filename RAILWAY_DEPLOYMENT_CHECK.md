# การตรวจสอบ Sample Data หลัง Deploy ไป Railway

## วิธีตรวจสอบว่า Sample Data ถูกสร้างขึ้นหรือไม่

### 1. ตรวจสอบผ่าน Railway Dashboard
1. เข้าไปที่ Railway project dashboard
2. ดู Deploy logs ในส่วน "Logs" tab
3. มองหา output จาก command `python manage.py load_sample_data`
4. ควรเห็น message เช่น:
   ```
   Loading sample company data...
   Creating startup...
   Creating investor... 
   Creating corporate...
   Successfully loaded sample data!
   Total Companies: 3
   - Startups: 1
   - Investors: 1
   - Corporates: 1
   ```

### 2. ตรวจสอบผ่าน Railway CLI (ถ้ามี)
```bash
# เข้าไปใน Railway shell
railway shell

# รัน command ตรวจสอบข้อมูล
python manage.py check_sample_data
```

### 3. ตรวจสอบผ่าน Django Admin
1. เข้าไปที่ `/admin/` ของเว็บไซต์
2. ล็อกอินด้วย superuser account
3. ดูใน section "Member" > "Company Profiles"
4. ควรเห็นบริษัทตัวอย่าง:
   - EcoPack Demo (Startup)
   - Demo Ventures (Investor)
   - Demo Corporation (Corporate)

### 4. ตรวจสอบผ่าน API/Web Interface
เข้าไปที่หน้าแรกของเว็บไซต์และดูว่ามีข้อมูลบริษัทแสดงหรือไม่

## หากไม่มีข้อมูล Sample Data

### วิธีแก้ไข 1: รัน Manual Command
```bash
# เข้าไป Railway shell
railway shell

# รัน command สร้างข้อมูลตัวอย่าง
python manage.py load_sample_data --force
```

### วิธีแก้ไข 2: Re-deploy
1. ไปที่ Railway dashboard
2. กด "Deploy" อีกครั้ง
3. รอให้ deployment เสร็จ
4. ตรวจสอบ logs อีกครั้ง

### วิธีแก้ไข 3: ตรวจสอบ Environment Variables
ให้แน่ใจว่า environment variables ถูกต้อง:
- `DATABASE_URL` ต้องมีค่า
- `DJANGO_SETTINGS_MODULE` = `seamap.settings`

## Troubleshooting

### ปัญหาที่อาจพบ:
1. **Database connection error**: ตรวจสอบ `DATABASE_URL`
2. **Migration error**: ตรวจสอบว่า migration ทำงานสำเร็จ
3. **Permission error**: ตรวจสอบ file permissions

### Debug Commands:
```bash
# ตรวจสอบสถานะ database
python manage.py check_sample_data

# ตรวจสอบ migration
python manage.py showmigrations

# ตรวจสอบ database tables
python manage.py dbshell
```

## Expected Sample Data

หลังจาก deploy สำเร็จ ควรมีข้อมูลดังนี้:

### Demo Users:
- `ecopack_demo` - Startup founder
- `investor_demo` - Investor  
- `corporate_demo` - Corporate representative

### Demo Companies:
1. **EcoPack Demo** (Startup)
   - Location: Thailand
   - Stage: Early Growth
   - Focus: Eco-friendly packaging

2. **Demo Ventures** (Investor)
   - Location: Singapore
   - Type: Venture Capital
   - Deal Size: $1M - $5M

3. **Demo Corporation** (Corporate)
   - Location: Singapore
   - Type: Multinational Corporation
   - Focus: Manufacturing & Sustainability

## ติดต่อสำหรับการช่วยเหลือ

หากยังมีปัญหา สามารถ:
1. ตรวจสอบ Railway logs ก่อน
2. ลองรัน management commands ใน Railway shell
3. ตรวจสอบว่า database schema ถูกต้อง
