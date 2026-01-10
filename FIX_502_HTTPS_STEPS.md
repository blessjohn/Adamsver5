# Step-by-Step Guide to Fix 502 Error with HTTPS

## Issues Found and Fixed

### 1. **Critical Issue: Wrong proxy_pass in HTTPS block**
   - **Problem**: Line 82 in `nginx.conf` was using `proxy_pass http://127.0.0.1:8000;`
   - **Why it fails**: In Docker, nginx container cannot reach `127.0.0.1:8000` because gunicorn runs in a separate `web` container
   - **Fix**: Changed to `proxy_pass http://django;` (uses the upstream defined at top of config)

### 2. **Missing proxy_http_version**
   - **Problem**: HTTPS block was missing `proxy_http_version 1.1;`
   - **Why it matters**: Required for HTTP/1.1 keepalive connections and proper header handling
   - **Fix**: Added `proxy_http_version 1.1;` in HTTPS block

### 3. **X-Forwarded-Proto header**
   - **Problem**: Using `$scheme` variable which might not always resolve correctly
   - **Why it matters**: Django needs this header to detect HTTPS requests behind proxy
   - **Fix**: Explicitly set to `https` in HTTPS block

## Step-by-Step Deployment Instructions

### Step 1: Verify the Fix
```bash
# Check the nginx.conf file
cat nginx.conf
```

Verify that line 82 in the HTTPS block shows:
```nginx
proxy_pass http://django;
```

And that it includes:
```nginx
proxy_http_version 1.1;
proxy_set_header X-Forwarded-Proto https;
```

### Step 2: Test Nginx Configuration
```bash
# If nginx is running in Docker, test the config
docker-compose exec gateway nginx -t
```

Or if nginx is installed directly:
```bash
nginx -t
```

### Step 3: Restart Services
```bash
# Restart the nginx/gateway container
docker-compose restart gateway

# Or rebuild if needed
docker-compose up -d --build gateway
```

### Step 4: Check Container Logs
```bash
# Check nginx logs for errors
docker-compose logs gateway

# Check gunicorn/web logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f gateway web
```

### Step 5: Verify HTTPS Connection
```bash
# Test HTTPS endpoint
curl -k https://adams.org.in/

# Or test with verbose output
curl -v -k https://adams.org.in/
```

### Step 6: Check Network Connectivity
```bash
# Verify nginx can reach the web container
docker-compose exec gateway ping web

# Or test HTTP connection from nginx to web
docker-compose exec gateway curl http://web:8000/
```

### Step 7: Verify Django Settings
Ensure `adams/settings.py` has:
```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https",)
```

This tells Django to trust the `X-Forwarded-Proto` header from nginx.

## Additional Troubleshooting

### If 502 persists:

1. **Check if web container is running:**
   ```bash
   docker-compose ps
   ```

2. **Check if web container is healthy:**
   ```bash
   docker-compose exec web curl http://localhost:8000/
   ```

3. **Verify network connectivity:**
   ```bash
   docker-compose exec gateway curl http://web:8000/
   ```

4. **Check nginx error logs:**
   ```bash
   docker-compose exec gateway cat /var/log/nginx/error.log
   ```

5. **Verify SSL certificates exist:**
   ```bash
   docker-compose exec gateway ls -la /etc/letsencrypt/live/adams.org.in/
   ```

6. **Check if port 443 is exposed in docker-compose.yml:**
   - **IMPORTANT**: Your `docker-compose.yml` currently only exposes port 8080:80
   - If you need HTTPS access directly to the container, add port 443 mapping:
   ```yaml
   gateway:
     ports:
       - "8080:80"
       - "443:443"  # Add this line for HTTPS
   ```
   - **Note**: If you're using a reverse proxy (like another nginx or load balancer) in front of Docker, you may not need this
   - **Current setup**: Port 443 is NOT exposed, which means HTTPS requests from outside Docker won't reach nginx

## Key Configuration Points

### nginx.conf HTTPS Block Should Have:
- ✅ `proxy_pass http://django;` (NOT 127.0.0.1:8000)
- ✅ `proxy_http_version 1.1;`
- ✅ `proxy_set_header X-Forwarded-Proto https;`
- ✅ `proxy_set_header X-Forwarded-Host $host;`
- ✅ `proxy_set_header X-Real-IP $remote_addr;`
- ✅ `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`

### Django settings.py Should Have:
- ✅ `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https",)`
- ✅ `ALLOWED_HOSTS` includes your domain
- ✅ `CSRF_TRUSTED_ORIGINS` includes your HTTPS domain

## Expected Behavior After Fix

- ✅ HTTPS requests should work without 502 errors
- ✅ Django should detect HTTPS correctly
- ✅ CSRF protection should work with HTTPS
- ✅ Secure cookies should be set correctly

