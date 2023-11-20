# Docker Installation

This installation method assumes that the PowerDNS server is already up and running. Additionally, we assume you have an Nginx server with a publicly exposed address `<CSR-IP>`, which is running on the same host as the Docker daemon.

Let's consider setting up CSR Proxy for signing CSRs for `go.example.com`. We also assume that our service will respond to the URL `https://csr-proxy.example.com/`.

Before proceeding further, ensure you have:

- PowerDNS FQDN
- PowerDNS API URL
- PowerDNS API Key

## DNS Setup

On DNS servers that are master for `example.com`:

Create an `A` record for `csr-proxy.example.com`:

```dns
csr-proxy IN A <CSR-IP>
```

Create a glue record to pass domain control to PowerDNS:

```dns
go IN NS pdns.example.com.
```

## PowerDNS Setup

On the PowerDNS server, create a zone:

```bash
pdnsutil create-zone go.example.com
```

And add an A record:

```bash
pdnsutil add-record go.example.com @ A 127.0.0.1
```

## Docker Setup

* Allocate an unused port for port mapping (later referred to as <port>)
* Create a directory to store state (later referred to as <state path>)
* Create a directory and place the following `docker-compose.yml`:

```yaml title="docker-compose.yml" 
version: "3"
services:
  csrp:
    image: "gufolabs/csr_proxy:master"
    restart: on-failure
    ports:
      - 127.0.0.1:<port>:8000
    volumes:
      - "<state path>:/var/lib/csr-proxy/" 
    logging:
      options:
        max-size: "10m"
        max-file: "3"
    environment:
      CSR_PROXY_API_HOST: 0.0.0.0
      CSR_PROXY_SUBJ: "${CSR_PROXY_SUBJ}"
      CSR_PROXY_EMAIL: "${CSR_PROXY_EMAIL}"
      CSR_PROXY_ACME_DIRECTORY: "${CSR_PROXY_ACME_DIRECTORY}"
      CSR_PROXY_PDNS_API_URL: "${CSR_PROXY_PDNS_API_URL}"
      CSR_PROXY_PDNS_API_KEY: "${CSR_PROXY_ACME_API_KEY}"
```

Create a .env file with our settings:

``` title=".env"
CSR_PROXY_SUBJ=CN=go.example.com
CSR_PROXY_EMAIL=test@example.com
CSR_PROXY_ACME_DIRECTORY=https://acme-v02.api.letsencrypt.org/directory
CSR_PROXY_PDNS_API_URL=https://pdns.example.com/
CSR_PROXY_PDNS_API_KEY=<API KEY>
```

Run our service:

```
docker compose up -d
```

## Nginx Setup

Add a file `/etc/nginx/conf.d/csr-proxy.example.com.conf` to your Nginx server. 
Note, we're leaving the certificate generation process out of the scope of this guide.

```nginx title="/etc/nginx/conf.d/csr-proxy.example.com.conf"
upstream csrp {
    server 127.0.0.1:<port>;
}

server {
    listen 443 ssl http2;
    server_name csr-proxy.example.com;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_certificate /etc/nginx/ssl/certificates/csr-proxy.example.com.crt;   
    ssl_certificate_key /etc/nginx/ssl/certificates/csr-proxy.example.com.key;  
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains";
    add_header X-Content-Type-Options nosniff;
    ssl_stapling off;
    ssl_stapling_verify off;

    access_log  /var/log/nginx/csr-proxy.example.com.access.log timed_upstream;
    error_log  /var/log/nginx/csr-proxy.example.com.error.log debug;

    location / {
        proxy_pass http://csrp_getnoc;
        proxy_read_timeout 60;
        proxy_redirect off;
        proxy_buffering off;
        gzip on;
        gzip_types text/html text/css text/x-js application/javascript application/json application/font-woff2;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_hide_header Vary;
    } 
}
```

And apply configuration:

```
service nginx reload
```

## Checking

Create private key:

```bash
openssl genrsa -out my.key 4096
```

Create certificate signing request:

```bash
openssl req -key my.key -new -out my.csr -subj /CN=go.example.com
```

Sign the CSR:

```bash
curl -X POST -d @my.csr -o my.crt https://csr-proxy.example.com/v1/sign
```

Check the `my.crt` file for the certificate.

```bash
head my.crt
-----BEGIN CERTIFICATE-----
MIIF5jCCBM6gAwIBAgISBForJGaLnlOVGSsH1AjiJxgCMA0GCSqGSIb3DQEBCwUA
MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD
...
```