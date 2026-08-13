# Production deployment

The live `poeta.icu/verse/` deployment uses:

- `verse-web.service`, installed as `/etc/systemd/system/verse-web.service`;
- `nginx-verse-location.conf`, installed as
  `/etc/nginx/snippets/verse-web-location.conf` and included from the HTTPS
  `poeta.icu` server block.

The service binds only to `127.0.0.1:8769`. Nginx strips `/verse/` while
forwarding and supplies `X-Forwarded-Prefix: /verse`, allowing Flask to produce
correct subpath URLs.

After changing application code:

```sh
sudo systemctl restart verse-web
curl -fsS http://127.0.0.1:8769/health
```

After changing the Nginx snippet:

```sh
sudo nginx -t
sudo systemctl reload nginx
```
