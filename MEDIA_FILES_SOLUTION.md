# การแก้ไข Media Files 404 ใน Railway

## ปัญหาที่พบ
Railway ไม่มี persistent file storage ทำให้ media files ที่ upload หายไปเมื่อ deploy ใหม่

## วิธีแก้ไข

### 1. ใช้ Template Tags สำหรับแสดงรูปภาพ

ใน template ให้ใช้ template tags แทนการเรียก URL โดยตรง:

```html
{% load media_tags %}

<!-- แทนที่ -->
<img src="{{ member.profile_picture.url }}" alt="Profile">

<!-- ใช้ -->
{% profile_picture_url member as profile_url %}
<img src="{{ profile_url }}" alt="Profile">

<!-- หรือ -->
<img src="{% profile_picture_url member %}" alt="Profile">
```

### 2. Template Tags ที่มีให้ใช้

#### `profile_picture_url`
สำหรับรูป profile ของ member:
```html
{% load media_tags %}
{% profile_picture_url member as profile_url %}
<img src="{{ profile_url }}" alt="{{ member.user.get_full_name }}">
```

#### `company_logo_url`
สำหรับ logo ของบริษัท:
```html
{% load media_tags %}
{% company_logo_url company as logo_url %}
<img src="{{ logo_url }}" alt="{{ company.company_name }}">
```

#### `safe_image_url`
สำหรับรูปภาพทั่วไปที่มี default fallback:
```html
{% load media_tags %}
{% safe_image_url challenge.featured_image '/static/images/default-challenge.png' as image_url %}
<img src="{{ image_url }}" alt="{{ challenge.title }}">
```

### 3. Default Images ที่ถูกสร้างขึ้น

- `/static/images/default-profile.png` - สำหรับ profile pictures
- `/static/images/default-company-logo.png` - สำหรับ company logos ทั่วไป
- `/static/images/default-startup-logo.png` - สำหรับ startup logos
- `/static/images/default-investor-logo.png` - สำหรับ investor logos
- `/static/images/default-corporate-logo.png` - สำหรับ corporate logos

### 4. URL Handler สำหรับ Production

ระบบจะ:
1. ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
2. ถ้าไม่มี จะ redirect ไปยัง default image ที่เหมาะสม
3. ป้องกัน 404 errors สำหรับ media files

### 5. Management Commands

#### `setup_media`
สร้าง media directories และ default files:
```bash
python manage.py setup_media
```

### 6. การใช้ใน Models

Models มี methods สำหรับ get URLs พร้อม fallback:

```python
# Member model
member.get_profile_picture_url()

# Company model  
company.get_company_logo_url()
```

### 7. ตัวอย่างการใช้งานใน Templates

#### Profile Page
```html
{% load media_tags %}

<div class="profile-section">
    {% profile_picture_url member as profile_url %}
    <img src="{{ profile_url }}" 
         alt="{{ member.user.get_full_name }}"
         class="profile-picture">
</div>
```

#### Company Card
```html
{% load media_tags %}

<div class="company-card">
    {% company_logo_url company as logo_url %}
    <img src="{{ logo_url }}" 
         alt="{{ company.company_name }}"
         class="company-logo">
    <h3>{{ company.company_name }}</h3>
</div>
```

#### Challenge/Problem Images
```html
{% load media_tags %}

<div class="featured-image">
    {% safe_image_url challenge.featured_image '/static/images/default-challenge.png' as image_url %}
    <img src="{{ image_url }}" 
         alt="{{ challenge.title }}"
         class="challenge-image">
</div>
```

### 8. การ Deploy

Railway จะรัน commands ในลำดับนี้:
1. `python manage.py migrate` - อัปเดต database
2. `python manage.py setup_media` - สร้าง media structure และ default files
3. `python manage.py load_full_sample_data --force` - โหลด sample data
4. `python manage.py collectstatic --noinput` - รวบรวม static files
5. `gunicorn seamap.wsgi:application` - เริ่ม web server

### 9. ข้อจำกัดของ Railway

- **ไม่มี Persistent Storage**: Files ที่ upload จะหายเมื่อ deploy ใหม่
- **แนะนำ**: ใช้ cloud storage (AWS S3, Cloudinary) สำหรับ production จริง
- **Workaround**: ใช้ default images และ fallback URLs

### 10. การปรับปรุงใน Future

สำหรับ production จริง ควร:
1. ใช้ AWS S3 หรือ Cloudinary สำหรับเก็บ media files
2. อัปเดต `DEFAULT_FILE_STORAGE` ใน settings
3. ตั้งค่า CDN สำหรับ performance ที่ดีขึ้น

## สรุป

ตอนนี้ระบบจะไม่แสดง 404 errors สำหรับ media files อีกต่อไป โดยจะใช้ default images แทนเมื่อไฟล์ไม่พบ ใช้ template tags ที่สร้างขึ้นใน templates เพื่อประสบการณ์ที่ดีกว่า
