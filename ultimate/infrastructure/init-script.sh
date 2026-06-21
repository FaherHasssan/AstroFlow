#!/bin/bash
# ==============================================================================
# AstroFlow - Production Node Cloud-Init Provisioning Engine
# Automatically installs runtimes, hardens firewalls, and initializes automated 
# encrypted PostgreSQL backup cronjobs for raw server initialization.
# ==============================================================================

set -euo pipefail

# 1. System Update & Base Dependencies
echo "[*] Updating system packages and installing core dependencies..."
apt-get update -y && apt-get upgrade -y
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    ufw \
    cron \
    openssl \
    tar

# 2. Configure Host Firewall Boundaries via UFW
echo "[*] Hardening networking interfaces with Uncomplicated Firewall (UFW)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Explicitly allow SSH (Rate limited to block botnet brute-force), HTTP, and HTTPS
ufw limit 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

echo "y" | ufw enable
ufw status verbose

# 3. Install Docker Engine Runtime & Docker Compose Protocol
echo "[*] Installing Docker runtimes securely via official signed repositories..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

# 4. Encrypted PostgreSQL Backup System Automation
echo "[*] Deploying automated encrypted Postgres backup cronjob system..."
BACKUP_DIR="/var/backups/astroflow_postgres"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

# Generate a strong encryption key for the backup archives natively via OpenSSL
BACKUP_SECRET_KEY=$(openssl rand -hex 32)
echo "$BACKUP_SECRET_KEY" > "$BACKUP_DIR/.encryption_key"
chmod 400 "$BACKUP_DIR/.encryption_key"

# Create the automated backup script payload executed by Cron
cat << 'EOF' > /usr/local/bin/pg_backup.sh
#!/bin/bash
set -e
BACKUP_DIR="/var/backups/astroflow_postgres"
KEY_FILE="$BACKUP_DIR/.encryption_key"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMP_DUMP="/tmp/db_dump_$TIMESTAMP.sql"
ENCRYPTED_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.enc"

# Execute a logical dump directly against the running production Docker container
# Assumes the container name resolves to 'db' or 'infrastructure-db-1'
DB_CONTAINER=$(docker ps -q -f name=db | head -n 1)
docker exec $DB_CONTAINER pg_dump -U postgres leaddb > "$TEMP_DUMP"

# Encrypt the raw SQL dump using OpenSSL AES-256-CBC cypher suite
openssl enc -aes-256-cbc -salt -in "$TEMP_DUMP" -out "$ENCRYPTED_FILE" -pass file:"$KEY_FILE" -pbkdf2

# Clean up raw unencrypted artifacts and enforce 30-day retention policies
rm "$TEMP_DUMP"
find "$BACKUP_DIR" -name "*.enc" -type f -mtime +30 -delete

logger "AstroFlow PostgreSQL backup cleanly generated, encrypted, and secured: $ENCRYPTED_FILE"
EOF

chmod +x /usr/local/bin/pg_backup.sh

# Inject cronjob to run daily at 03:00 AM server time silently
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/pg_backup.sh >> /var/log/pg_backup.log 2>&1") | crontab -

echo "[*] Provisioning Sequence Complete. The isolated node is ready for Docker Compose deployment."
