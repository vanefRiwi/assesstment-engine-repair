// One-shot job used by docker compose: creates the RS256 key pair on first start.
// The private key goes to a volume mounted only by auth-service; the public key to one mounted by business-service.
import { generateKeyPairSync } from "node:crypto";
import { chmodSync, existsSync, writeFileSync } from "node:fs";

const privatePath = "/keys/private/jwt-private.pem";
const publicPath = "/keys/public/jwt-public.pem";

if (existsSync(privatePath) && existsSync(publicPath)) {
  console.log("JWT key pair already exists.");
  process.exit(0);
}

const { privateKey, publicKey } = generateKeyPairSync("rsa", {
  modulusLength: 2048,
  publicKeyEncoding: { type: "spki", format: "pem" },
  privateKeyEncoding: { type: "pkcs8", format: "pem" },
});
writeFileSync(privatePath, privateKey, { mode: 0o400 });
writeFileSync(publicPath, publicKey, { mode: 0o444 });
chmodSync(privatePath, 0o400);
console.log("JWT key pair generated.");
