# AIOS — Secured Attachments Runbook (template edition)

Serve attachments from a **private** object-storage bucket via a signature-gated Worker/Function
that only returns an object when the URL carries a valid **non-expiring HMAC signature**. Result:
files that **render inline in your vault app**, are **portable** across storage providers, keep
the vault repo **text-only**, and are **not publicly guessable** (and revocable by rotating one
secret). Private/sensitive files stay local instead, never uploaded.

**Two tiers only — no public tier.** Sharing = hand someone the signed URL.

This is the generic, placeholder-based version of this runbook. If you keep a filled-in copy for your
own instance (real domain, bucket, and paths), mirror any change between the two.

---

## 0. Why this shape
- **Private bucket** — no public access, no default provider URL, no open custom domain pointed directly at it.
- **Gate via Worker/Function**: `GET https://<cdn.yourdomain.com>/<key>?sig=<hmac>` → validates the signature, streams the object, else 403.
- **Signature is in the URL** → self-authenticating, so the vault app's inline fetch renders it without any separate auth flow.
- **Non-expiring** → links never rot on their own. **Revoke** by rotating the signing secret (invalidates every link at once; re-sign the vault in the same pass).
- **Cost**: with Cloudflare R2 + Workers specifically, almost certainly **$0** at personal-vault scale (10 GB / 1M writes / 10M reads per month free tier, zero egress, 100k Worker requests/day free tier). Any S3-compatible provider + edge-function platform works the same way.

## 1. Create the private bucket
Create a bucket (e.g. `<your-bucket>`) in your storage provider. **Do not** enable public access
or connect a public domain. Leave it private.

## 2. Generate a signing secret
```bash
openssl rand -hex 32     # copy the output — this is SIGN_SECRET
```

## 3. Create the Worker (Cloudflare example — adapt for another edge-function platform)
`wrangler.toml`:
```toml
name = "<your-worker-name>"
main = "worker.js"
compatibility_date = "2026-01-01"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "<your-bucket>"
# Do NOT put routes here — the custom domain (cdn.yourdomain.com) is added in the dashboard
# after deploy. (A `routes`/`route` key must be top-level, before any [[...]] table, or the
# deploy tool warns "unexpected field in r2_buckets".)
```
`worker.js`:
```js
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const key = decodeURIComponent(url.pathname.replace(/^\/+/, ""));
    const sig = url.searchParams.get("sig") || "";
    if (!key) return new Response("Not found", { status: 404 });
    const expected = await hmac(env.SIGN_SECRET, key);
    if (!safeEqual(sig, expected)) return new Response("Forbidden", { status: 403 });
    const obj = await env.BUCKET.get(key);
    if (!obj) return new Response("Not found", { status: 404 });
    const h = new Headers();
    obj.writeHttpMetadata(h);        // forwards the object's stored Content-Type/Content-Disposition
    h.set("etag", obj.httpEtag);
    h.set("Cache-Control", "private, max-age=86400");
    // Objects are stored with Content-Disposition: inline (step 4b) so they render in an
    // iframe/vault app. Append &dl=1 to any signed URL to force a real "Save As" download
    // instead — overrides the response header only, not the signature check, since dl isn't
    // part of the signed payload (it's a display preference, not an authorization grant).
    if (url.searchParams.get("dl")) {
      const filename = key.split("/").pop();
      h.set("Content-Disposition", `attachment; filename="${filename}"`);
    }
    return new Response(obj.body, { headers: h });
  }
};
async function hmac(secret, msg) {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg));
  return [...new Uint8Array(mac)].map(b => b.toString(16).padStart(2, "0")).join("");
}
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
```
Deploy + set the secret + point the custom domain:
```bash
npm i -g wrangler
wrangler deploy                     # creates + uploads the Worker (with the bucket binding)
wrangler secret put SIGN_SECRET     # paste the value from step 2
wrangler secret list                # confirm SIGN_SECRET is set
```
> If you run `secret put` *before* `deploy`, it may ask "create a new Worker?" — answer **yes**, then run `deploy` to upload the code. And if you're only picking up a `worker.js` code change on an already-deployed Worker, `wrangler deploy` alone is enough — no need to redo the secret or domain steps.

Then add `cdn.yourdomain.com` as a **Custom Domain** on the Worker (dashboard → your Worker →
Settings → Domains & Routes → Add → Custom Domain). It must resolve through the **Worker**, not
directly to the bucket, or the bucket serves publicly.

## 4. Upload tooling
### 4a. Configure the remote (rclone example)
```bash
brew install rclone
rclone config create <remote-name> s3 provider=Cloudflare \
  access_key_id=<ACCESS_KEY_ID> secret_access_key=<SECRET> \
  region=auto endpoint=https://<ACCOUNT_ID>.r2.cloudflarestorage.com \
  no_check_bucket=true
```
> `no_check_bucket=true` is required for R2: scoped API tokens can't run bucket-level ops, so without it the upload tool tries to create the bucket on upload and gets `403 AccessDenied`. (Already have the remote misconfigured? Fix it with `rclone config update <remote-name> no_check_bucket true`.)

### 4b. Upload with the correct disposition header — load-bearing, don't skip
```bash
rclone copyto <file> <remote-name>:<your-bucket>/<key> --header-upload "Content-Disposition: inline"
```
Without this header, uploaded objects have **no** disposition metadata at all, and browsers
default to force-downloading regardless of Content-Type. This one flag is what makes inline
preview possible at all.

## 5. Make the signing secret available to whatever signs URLs locally
```bash
echo 'export AIOS_R2_SIGN_SECRET="<same value as step 2>"' >> ~/.zshrc && source ~/.zshrc
```
(Do **not** put the secret in the vault's `attachments.json` — that file only ever names the env
var, never the value.)

## 6. Configure the vault for secured mode
Edit `<vault>/.aios/attachments.json` (gitignored — never commit this file):
```json
{
  "defaultDestination": "r2",
  "localFolder": "attachments",
  "privateFolder": "Private/attachments",
  "r2": {
    "remote": "<remote-name>",
    "bucket": "<your-bucket>",
    "workerBaseUrl": "https://cdn.yourdomain.com",
    "keyTemplate": "attachments/{yyyy}/{mm}/{filename}",
    "signSecretEnv": "AIOS_R2_SIGN_SECRET"
  }
}
```
See `attachments.example.json` in the vault for the fully-annotated version, including the fields
that make the flow work from an agent session with no local shell/secret access (staged uploads,
resolved asynchronously).

## 7. Test
```bash
KEY="attachments/2026/07/test.txt"
echo "hello secured storage" > /tmp/test.txt
rclone copyto /tmp/test.txt "<remote-name>:<your-bucket>/${KEY}" --header-upload "Content-Disposition: inline"
SIG=$(printf '%s' "$KEY" | openssl dgst -sha256 -hmac "$AIOS_R2_SIGN_SECRET" -hex | sed 's/^.* //')
echo "https://cdn.yourdomain.com/${KEY}?sig=${SIG}"     # opens; without ?sig → 403
```

## 8. Orphan reconciler (mandatory, not optional)
The vault app never tracks remote objects — without this, the bucket grows forever with dead
files the moment a note stops referencing them. Save as `<vault>/.aios/reconcile-attachments.sh`
(inside `.aios/`, which is gitignored):
```bash
#!/usr/bin/env bash
set -euo pipefail
VAULT="<vault>"; REMOTE="<remote-name>"; BUCKET="<your-bucket>"
BASE="https://cdn.yourdomain.com"
referenced=$(grep -rhoE "${BASE}/[^)\"' ?]+" "$VAULT" --include='*.md' | sed "s#${BASE}/##" | sort -u)
present=$(rclone lsf "${REMOTE}:${BUCKET}" -R | sort -u)
orphans=$(comm -23 <(echo "$present") <(echo "$referenced") || true)
if [ -z "${orphans// }" ]; then echo "No orphans."; exit 0; fi
echo "Orphans:"; echo "$orphans"
if [ "${1:-}" = "--delete" ]; then
  echo "$orphans" | while read -r k; do [ -n "$k" ] && rclone deletefile "${REMOTE}:${BUCKET}/${k}" && echo "deleted $k"; done
else echo "(dry run — re-run with --delete)"; fi
```
Schedule weekly, dry-run for a couple of weeks before trusting `--delete` — see
`AIOS_MASTER_RUNBOOK.md` §5b.

## 9. Rotating / revoking
Rotating `SIGN_SECRET` invalidates every existing link at once. Then re-sign every URL in the
vault (a script that walks the vault, recomputes each `?sig=` from the key, and rewrites the URL —
see `AIOS_MASTER_RUNBOOK.md` §5c for the exact commands).

## 10. Portability & multi-instance use
- **Provider/host swap** later = point `cdn.yourdomain.com` at a new origin; markdown never changes, because every note only ever references the stable domain, never the raw provider URL.
- **Each person adopting this template stands up their own** bucket + Worker + secret — nothing here is shared across instances. Leaving `defaultDestination: vault` (in-repo, local) is a valid alternative if someone doesn't want to run the object-storage tier at all yet.

## 11. Embedding signed URLs in notes (the part that actually makes files preview)

A signed URL alone doesn't render — how you reference it in a note determines whether it previews
inline or just downloads. Full doctrine: `AIOS_LLD.md` §7 and the vault's own
`30 Atlas/Conventions.md § 📎 Attachments`. Summary, format by format:

| Format | Embed as | Why |
|---|---|---|
| image | `![file](url)` | Plain embed, no wrapper needed |
| txt | Collapsed callout, `<iframe src="url">` inside | Browsers render plain text natively |
| pdf | Collapsed callout, **`external-pdf` community plugin** code block (NOT an iframe) | Obsidian runs on Electron, which has a confirmed bug — `<iframe>` cannot render PDFs at all, blank frame every time. Not fixable via headers/CORS/the Worker. The plugin renders through Obsidian's own bundled PDF viewer instead. Install via BRAT (not in the official plugin directory): Settings → Community plugins → Browse → install "BRAT" → BRAT settings → Add Beta plugin → `tenebrisnox/external-PDF-plugin`. |
| docx / xlsx / pptx | Collapsed callout, `<iframe src="...">` pointed at Office Online's viewer: `https://view.officeapps.live.com/op/embed.aspx?src=<url-encoded signed URL>` | Browsers can't render Office formats directly; renders via JS/canvas, so it isn't affected by the Electron PDF bug |
| csv | Plain link, never embedded | Chrome/Firefox force-download csv even with correct headers — no reliable inline path exists |

**The collapsed callout shape** (every iframe/plugin case):
```markdown
> [!doc]- 📎 filename.ext
> <iframe src="<signed URL>" width="100%" height="600"></iframe>
>
> [⬇ Download original](<signed URL>&dl=1)
```
`[!doc]-` is stock Obsidian callout syntax — the `-` makes it foldable-and-collapsed by default;
nothing plugin-specific about the folding itself.

**Two spacing rules, non-negotiable** (both discovered from a real broken render):
1. A bare `>` line between the embedded block (iframe or the `external-pdf` fenced block) and the download link, or the link gets swallowed as literal text instead of rendering as a link.
2. A genuinely blank line (no `>`) between one attachment's callout and the next, or consecutive `>` lines merge into a single blockquote and the second attachment's header renders as inert text inside the first one's callout.

Whatever script finishes an upload (§4b, or its automated equivalent) should generate this
markdown itself, unconditionally including both spacing rules — never leave the calling agent/
human to hand-write the embed syntax, since that's exactly how the spacing bugs were discovered.
