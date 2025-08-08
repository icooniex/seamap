# Cloudflare R2 Setup Guide for SEA-MaP

This guide will help you setup Cloudflare R2 object storage for handling media files (profile pictures, company logos, and documents) on Railway.

## Why Cloudflare R2?

- **Persistent Storage**: Unlike Railway's ephemeral filesystem, R2 provides permanent file storage
- **Cost Effective**: Cheaper than AWS S3 with no egress fees
- **Global CDN**: Fast delivery worldwide through Cloudflare's network
- **S3 Compatible**: Uses standard S3 API for easy integration

## Step 1: Create Cloudflare R2 Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **R2 Object Storage** in the sidebar
3. Click **Create bucket**
4. Enter bucket name: `seamap-media` (or your preferred name)
5. Choose location: **Automatic** (recommended)
6. Click **Create bucket**

## Step 2: Get R2 API Credentials

1. In R2 dashboard, click **Manage R2 API tokens**
2. Click **Create API token**
3. Configure the token:
   - **Token name**: `seamap-railway-access`
   - **Permissions**: `Object Read & Write`
   - **Specify bucket**: Select your `seamap-media` bucket
   - **TTL**: Leave blank (no expiration)
4. Click **Create API Token**
5. **IMPORTANT**: Copy the `Access Key ID` and `Secret Access Key` - you won't see them again!

## Step 3: Get Your Account ID

1. In Cloudflare dashboard, look at the right sidebar
2. Copy your **Account ID** - you'll need this for the endpoint URL

## Step 4: Configure Railway Environment Variables

Add these environment variables to your Railway project:

```bash
USE_CLOUDFLARE_R2=true
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key_from_step_2
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key_from_step_2
CLOUDFLARE_R2_BUCKET_NAME=seamap-media
CLOUDFLARE_R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
```

Replace `your-account-id` with the Account ID from Step 3.

## Step 5: Optional - Setup Custom Domain (Recommended)

For better performance and SEO, setup a custom domain:

1. In your R2 bucket settings, go to **Settings** > **Custom Domain**
2. Enter your domain: `media.yourdomain.com`
3. Add the CNAME record to your DNS:
   ```
   media.yourdomain.com CNAME your-bucket-name.your-account-id.r2.cloudflarestorage.com
   ```
4. Add this environment variable to Railway:
   ```bash
   CLOUDFLARE_R2_CUSTOM_DOMAIN=media.yourdomain.com
   ```

## Step 6: Deploy to Railway

1. Push your code changes to the repository
2. Railway will automatically deploy with R2 configuration
3. The setup command will create the bucket structure and test the connection

## Testing the Setup

After deployment, test that media files work:

1. Go to your Railway app
2. Try uploading a profile picture or company logo
3. Check that images display correctly
4. Verify files are stored in your R2 bucket (Cloudflare dashboard > R2 > your bucket)

## File Organization

Your R2 bucket will be organized as:

```
seamap-media/
├── media/
│   ├── profile_pictures/
│   │   └── user_123/
│   │       └── profile.jpg
│   ├── company_logos/
│   │   └── company_456/
│   │       └── logo.png
│   └── documents/
│       ├── company_789/
│       │   └── document.pdf
│       └── user_101/
│           └── file.docx
└── private/
    └── documents/
        └── sensitive_files/
```

## Cost Estimation

Cloudflare R2 pricing (as of 2024):
- **Storage**: $0.015 per GB per month
- **Class A Operations** (writes): $4.50 per million
- **Class B Operations** (reads): $0.36 per million
- **Egress**: FREE (no bandwidth charges)

For a typical startup platform:
- ~1000 users with profile pictures (1MB each) = 1GB = $0.015/month
- ~500 company logos (500KB each) = 250MB = $0.004/month
- **Total**: ~$0.02/month for storage + minimal operation costs

## Troubleshooting

### Files not uploading
- Check environment variables are set correctly in Railway
- Verify R2 API token has write permissions
- Check Railway logs for error messages

### Images not displaying
- Verify CLOUDFLARE_R2_CUSTOM_DOMAIN is set correctly
- Check bucket policies allow public read access
- Test direct R2 URLs in browser

### Performance issues
- Setup custom domain for faster loading
- Enable Cloudflare caching rules
- Consider image optimization

## Migration from Local Storage

If you have existing media files:

1. Download all files from `/media/` directory
2. Upload them to R2 using the AWS CLI or Cloudflare's web interface
3. Maintain the same folder structure
4. Update database records if needed

## Security Notes

- **Public Files**: Profile pictures and company logos are stored with public read access
- **Private Files**: Documents will be stored with private access and signed URLs
- **API Keys**: Never commit API keys to code - use environment variables only
- **Bucket Policies**: Configure appropriate CORS and access policies
