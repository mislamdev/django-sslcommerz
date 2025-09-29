# Deployment

This guide covers deploying Django SSLCOMMERZ in production environments.

## Production Checklist

### Security Requirements

- [ ] **Environment Variables**: Store credentials in environment variables, not code
- [ ] **HTTPS Only**: All callback URLs must use HTTPS in production
- [ ] **SSL Verification**: Keep `VERIFY_SSL=True` for API requests
- [ ] **Sandbox Mode**: Set `IS_SANDBOX=False` for production
- [ ] **Request Logging**: Disable `LOG_REQUESTS` in production
- [ ] **Secret Management**: Use proper secret management systems

### Configuration Validation

```python
from sslcommerz.utils import is_production_ready, get_environment_info

# Check production readiness
if is_production_ready():
    print("✅ Configuration is production ready")
else:
    print("❌ Configuration needs attention")
    print(get_environment_info())
```

## Environment-Specific Settings

### Development Environment

```python
# settings/development.py
SSLCOMMERZ = {
    'STORE_ID': 'test_store_id',
    'STORE_PASSWORD': 'test_store_password',
    'IS_SANDBOX': True,
    'SUCCESS_URL': 'http://localhost:8000/payment/success/',
    'FAIL_URL': 'http://localhost:8000/payment/fail/',
    'CANCEL_URL': 'http://localhost:8000/payment/cancel/',
    'IPN_URL': 'http://localhost:8000/payment/ipn/',
    'LOG_REQUESTS': True,  # Enable for debugging
    'VERIFY_SSL': True,
}
```

### Staging Environment

```python
# settings/staging.py
from decouple import config

SSLCOMMERZ = {
    'STORE_ID': config('SSLCOMMERZ_STORE_ID'),
    'STORE_PASSWORD': config('SSLCOMMERZ_STORE_PASSWORD'),
    'IS_SANDBOX': True,  # Still use sandbox for staging
    'SUCCESS_URL': config('SSLCOMMERZ_SUCCESS_URL'),
    'FAIL_URL': config('SSLCOMMERZ_FAIL_URL'),
    'CANCEL_URL': config('SSLCOMMERZ_CANCEL_URL'),
    'IPN_URL': config('SSLCOMMERZ_IPN_URL'),
    'LOG_REQUESTS': False,
    'VERIFY_SSL': True,
}
```

### Production Environment

```python
# settings/production.py
from decouple import config

SSLCOMMERZ = {
    'STORE_ID': config('SSLCOMMERZ_STORE_ID'),
    'STORE_PASSWORD': config('SSLCOMMERZ_STORE_PASSWORD'),
    'IS_SANDBOX': False,  # Production mode
    'SUCCESS_URL': config('SSLCOMMERZ_SUCCESS_URL'),
    'FAIL_URL': config('SSLCOMMERZ_FAIL_URL'),
    'CANCEL_URL': config('SSLCOMMERZ_CANCEL_URL'),
    'IPN_URL': config('SSLCOMMERZ_IPN_URL'),
    'LOG_REQUESTS': False,
    'VERIFY_SSL': True,
    'TIMEOUT': 30,
}

# Additional production settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
      - SSLCOMMERZ_STORE_ID=${SSLCOMMERZ_STORE_ID}
      - SSLCOMMERZ_STORE_PASSWORD=${SSLCOMMERZ_STORE_PASSWORD}
      - SSLCOMMERZ_IS_SANDBOX=False
      - SSLCOMMERZ_SUCCESS_URL=${SSLCOMMERZ_SUCCESS_URL}
      - SSLCOMMERZ_FAIL_URL=${SSLCOMMERZ_FAIL_URL}
      - SSLCOMMERZ_CANCEL_URL=${SSLCOMMERZ_CANCEL_URL}
      - SSLCOMMERZ_IPN_URL=${SSLCOMMERZ_IPN_URL}
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myproject
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
```

## Kubernetes Deployment

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sslcommerz-config
data:
  DJANGO_SETTINGS_MODULE: "myproject.settings.production"
  SSLCOMMERZ_IS_SANDBOX: "false"
  SSLCOMMERZ_VERIFY_SSL: "true"
  SSLCOMMERZ_LOG_REQUESTS: "false"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sslcommerz-secrets
type: Opaque
data:
  store-id: <base64-encoded-store-id>
  store-password: <base64-encoded-store-password>
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
      - name: web
        image: myregistry/django-app:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: sslcommerz-config
        env:
        - name: SSLCOMMERZ_STORE_ID
          valueFrom:
            secretKeyRef:
              name: sslcommerz-secrets
              key: store-id
        - name: SSLCOMMERZ_STORE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: sslcommerz-secrets
              key: store-password
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Cloud Platform Deployments

### Heroku

```bash
# Procfile
web: gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT

# runtime.txt
python-3.10.2

# Set environment variables
heroku config:set SSLCOMMERZ_STORE_ID=your_store_id
heroku config:set SSLCOMMERZ_STORE_PASSWORD=your_store_password
heroku config:set SSLCOMMERZ_IS_SANDBOX=False
heroku config:set SSLCOMMERZ_SUCCESS_URL=https://yourapp.herokuapp.com/payment/success/
heroku config:set SSLCOMMERZ_FAIL_URL=https://yourapp.herokuapp.com/payment/fail/
heroku config:set SSLCOMMERZ_CANCEL_URL=https://yourapp.herokuapp.com/payment/cancel/
heroku config:set SSLCOMMERZ_IPN_URL=https://yourapp.herokuapp.com/payment/ipn/
```

### AWS Elastic Beanstalk

```python
# .ebextensions/01_sslcommerz.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: myproject.settings.production
    SSLCOMMERZ_IS_SANDBOX: "false"
    SSLCOMMERZ_VERIFY_SSL: "true"
```

## Monitoring and Logging

### Application Monitoring

```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/sslcommerz.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'sslcommerz': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Sentry Integration

```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)
```

### Health Checks

```python
# health/views.py
from django.http import JsonResponse
from sslcommerz.utils import get_environment_info

def health_check(request):
    """Basic health check endpoint."""
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
    })

def readiness_check(request):
    """Readiness check including SSLCOMMERZ configuration."""
    try:
        from sslcommerz.config import validate_config
        validate_config()
        
        return JsonResponse({
            'status': 'ready',
            'sslcommerz': 'configured',
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=503)
```

## Performance Optimization

### Database Optimization

```python
# Optimize transaction queries
class Transaction(models.Model):
    # ... existing fields
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer_email', 'created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['tran_id']),  # Most common lookup
        ]
```

### Caching

```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache configuration validation
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def cached_sslcommerz_config(request):
    from sslcommerz.utils import get_environment_info
    return JsonResponse(get_environment_info())
```

## Security Best Practices

### HTTPS Configuration

```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### IPN Security

```python
# Custom IPN view with additional security
class SecureIPNView(BaseIPNView):
    def dispatch(self, request, *args, **kwargs):
        # Verify IP whitelist (if SSLCOMMERZ provides specific IPs)
        allowed_ips = ['203.202.245.102', '203.202.245.103']  # Example IPs
        client_ip = self.get_client_ip(request)
        
        if client_ip not in allowed_ips:
            logger.warning(f"IPN request from unauthorized IP: {client_ip}")
            return HttpResponse('Unauthorized', status=401)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup_sslcommerz_data.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/sslcommerz"

# Backup transactions
pg_dump -t sslcommerz_transaction myproject > $BACKUP_DIR/transactions_$DATE.sql

# Backup refunds
pg_dump -t sslcommerz_refundtransaction myproject > $BACKUP_DIR/refunds_$DATE.sql

# Compress and upload to S3 (example)
tar -czf $BACKUP_DIR/sslcommerz_backup_$DATE.tar.gz $BACKUP_DIR/*_$DATE.sql
aws s3 cp $BACKUP_DIR/sslcommerz_backup_$DATE.tar.gz s3://mybucket/backups/
```

## Troubleshooting

### Common Production Issues

1. **IPN Not Received**
   - Check firewall settings
   - Verify IPN URL is accessible from internet
   - Check server logs for blocked requests

2. **SSL Certificate Issues**
   - Verify certificate is valid
   - Check intermediate certificates
   - Test with SSL checker tools

3. **Configuration Issues**
   - Use management command: `python manage.py test_sslcommerz`
   - Check environment variables
   - Verify Django settings

### Debugging Commands

```bash
# Check configuration
python manage.py test_sslcommerz

# Test connectivity
curl -X POST https://securepay.sslcommerz.com/gwprocess/v4/api.php

# Check logs
tail -f /var/log/django/sslcommerz.log

# Database health
python manage.py dbshell -c "SELECT COUNT(*) FROM sslcommerz_transaction;"
```
