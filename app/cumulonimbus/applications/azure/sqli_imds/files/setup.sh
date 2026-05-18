#!/bin/bash
# Sets up SQL Server Express + vulnerable Node.js app on Ubuntu 22.04
set -e
export DEBIAN_FRONTEND=noninteractive

# ── SQL Server 2022 ────────────────────────────────────────────────────────────
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy main" \
  > /etc/apt/sources.list.d/mssql-server-2022.list

apt-get update -qq
ACCEPT_EULA=Y apt-get install -y mssql-server

MSSQL_SA_PASSWORD='Sql@dmin1234' MSSQL_PID='Express' \
  /opt/mssql/bin/mssql-conf -n setup accepteula

systemctl enable mssql-server
systemctl start mssql-server

# ── sqlcmd tools ───────────────────────────────────────────────────────────────
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
https://packages.microsoft.com/ubuntu/22.04/prod jammy main" \
  > /etc/apt/sources.list.d/mssql-release.list

ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev
export PATH="$PATH:/opt/mssql-tools18/bin"

# Wait until SQL Server accepts connections
for i in {1..30}; do
  sqlcmd -S localhost -U sa -P 'Sql@dmin1234' -Q "SELECT 1" > /dev/null 2>&1 && break
  sleep 3
done

# ── Database setup ─────────────────────────────────────────────────────────────
sqlcmd -S localhost -U sa -P 'Sql@dmin1234' \
  -Q "CREATE DATABASE users;" 2>/dev/null || true

sqlcmd -S localhost -U sa -P 'Sql@dmin1234' -d users -Q "
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Users')
  CREATE TABLE dbo.Users (
    Id   INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(4000)
  );"

# ── Node.js ────────────────────────────────────────────────────────────────────
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
apt-get install -y nodejs > /dev/null 2>&1

mkdir -p /opt/sqlapp
cd /opt/sqlapp
npm init -y > /dev/null 2>&1
npm install express body-parser mssql > /dev/null 2>&1

# Use Python to write server.js — avoids bash escaping issues with JS template literals
python3 - << 'PYEOF'
code = r"""const express = require('express');
const bodyParser = require('body-parser');
const sql = require('mssql');

const config = {
  user: 'sa',
  password: 'Sql@dmin1234',
  server: 'localhost',
  port: 1433,
  database: 'users',
  options: { encrypt: false, trustServerCertificate: true }
};

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', async (req, res) => {
  let rows = '';
  try {
    const pool = await sql.connect(config);
    const r = await pool.request()
      .query('SELECT TOP 20 Name FROM dbo.Users ORDER BY Id DESC');
    rows = r.recordset
      .map(x => `<li style="word-break:break-all;font-family:monospace;font-size:12px">${x.Name}</li>`)
      .join('');
    await sql.close();
  } catch (_) {}

  res.send(`<!DOCTYPE html><html><head><title>User Manager</title></head><body>
<h1>User Manager</h1>
<form method="POST" action="/add-user">
  <input name="username" type="text" placeholder="Username" style="width:500px">
  <button type="submit">Add User</button>
</form>
<h2>Recent entries</h2><ul>${rows}</ul>
</body></html>`);
});

app.post('/add-user', async (req, res) => {
  const username = req.body.username;
  try {
    const pool = await sql.connect(config);
    await pool.request()
      .query(`INSERT INTO dbo.Users (Name) VALUES ('${username}')`);
    await sql.close();
  } catch (err) {
    try { await sql.close(); } catch (_) {}
  }
  res.redirect('/');
});

app.listen(80, '0.0.0.0');
"""
open('/opt/sqlapp/server.js', 'w').write(code.strip())
PYEOF

# ── Systemd service ────────────────────────────────────────────────────────────
cat > /etc/systemd/system/sqlapp.service << 'SVCEOF'
[Unit]
Description=Vulnerable SQL Web App
After=network.target mssql-server.service
Requires=mssql-server.service

[Service]
ExecStart=/usr/bin/node /opt/sqlapp/server.js
Restart=on-failure
RestartSec=5
WorkingDirectory=/opt/sqlapp
User=root

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable sqlapp
systemctl start sqlapp
