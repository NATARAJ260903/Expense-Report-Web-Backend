import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dist = path.join(__dirname, "dist");
const port = Number(process.env.PORT || 3000);

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, { "Content-Type": type });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const requestPath = decodeURIComponent((req.url || "/").split("?")[0]);
  let filePath = path.join(dist, requestPath === "/" ? "index.html" : requestPath);

  if (!filePath.startsWith(dist)) {
    return send(res, 403, "Forbidden");
  }

  fs.stat(filePath, (statErr, stat) => {
    if (!statErr && stat.isFile()) {
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream" });
      fs.createReadStream(filePath).pipe(res);
      return;
    }

    // SPA fallback: send index.html for client-side routes.
    filePath = path.join(dist, "index.html");
    fs.readFile(filePath, (err, data) => {
      if (err) return send(res, 500, "Frontend build not found.");
      res.writeHead(200, { "Content-Type": mime[".html"] });
      res.end(data);
    });
  });
});

server.listen(port, "0.0.0.0", () => {
  console.log(`Expense Report frontend running on port ${port}`);
});
