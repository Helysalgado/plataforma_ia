#!/bin/bash
# =============================================================================
# BioAI Hub - SSL Certificate Setup Script
# =============================================================================
# This script sets up Let's Encrypt SSL certificates for bioai.ccg.unam.mx
#
# Usage:
#   ./scripts/setup-ssl.sh
#
# Requirements:
#   - Docker and docker-compose installed
#   - DNS records configured (A record pointing to server IP)
#   - Ports 80 and 443 open in firewall

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== BioAI Hub - SSL Setup ===${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production not found${NC}"
    echo "Please copy .env.example to .env.production and configure it"
    exit 1
fi

# Load environment variables
source .env.production

# Validate required variables
if [ -z "$EMAIL_HOST_USER" ]; then
    echo -e "${RED}Error: EMAIL_HOST_USER not set in .env.production${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating directories...${NC}"
mkdir -p nginx/conf.d
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p logs/nginx

echo -e "${YELLOW}Step 2: Starting Nginx (HTTP only) for ACME challenge...${NC}"
# Temporary Nginx config for certificate generation
cat > nginx/conf.d/temp.conf <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name bioai.ccg.unam.mx www.bioai.ccg.unam.mx;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 "BioAI Hub - Setting up SSL...\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Start Nginx temporarily
docker run -d --name nginx_temp \
    -p 80:80 \
    -v $(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro \
    -v $(pwd)/certbot/www:/var/www/certbot:ro \
    nginx:alpine

sleep 5

echo -e "${YELLOW}Step 3: Obtaining SSL certificate from Let's Encrypt...${NC}"
docker run --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL_HOST_USER \
    --agree-tos \
    --no-eff-email \
    -d bioai.ccg.unam.mx \
    -d www.bioai.ccg.unam.mx

# Check if certificates were obtained
if [ ! -d "certbot/conf/live/bioai.ccg.unam.mx" ]; then
    echo -e "${RED}Error: Failed to obtain SSL certificates${NC}"
    docker stop nginx_temp && docker rm nginx_temp
    exit 1
fi

echo -e "${GREEN}✓ SSL certificates obtained successfully!${NC}\n"

echo -e "${YELLOW}Step 4: Stopping temporary Nginx...${NC}"
docker stop nginx_temp && docker rm nginx_temp

echo -e "${YELLOW}Step 5: Setting up auto-renewal cron job...${NC}"
# Create renewal script
cat > scripts/renew-ssl.sh <<'RENEWAL_EOF'
#!/bin/bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
RENEWAL_EOF

chmod +x scripts/renew-ssl.sh

# Add cron job (runs daily at 2am)
(crontab -l 2>/dev/null; echo "0 2 * * * cd /var/www/bioai && ./scripts/renew-ssl.sh >> /var/log/letsencrypt-renew.log 2>&1") | crontab -

echo -e "${GREEN}✓ Auto-renewal configured (daily at 2 AM)${NC}\n"

echo -e "${GREEN}=== SSL Setup Complete! ===${NC}\n"
echo -e "Certificates location: certbot/conf/live/bioai.ccg.unam.mx/"
echo -e "Next steps:"
echo -e "  1. Start production services: ${YELLOW}docker-compose -f docker-compose.prod.yml up -d${NC}"
echo -e "  2. Check logs: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "  3. Test HTTPS: ${YELLOW}curl -I https://bioai.ccg.unam.mx${NC}\n"
