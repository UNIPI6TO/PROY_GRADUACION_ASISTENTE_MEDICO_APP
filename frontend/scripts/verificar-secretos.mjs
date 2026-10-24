import fs from "node:fs";
import path from "node:path";

const distDir = path.resolve(process.cwd(), "dist");
const PATRONES_SECRETOS = [/AIza[0-9A-Za-z-_]{20,}/, /gsk_[0-9A-Za-z]{20,}/, /VITE_GEMINI_KEY/];

function escanearDirectorio(dir) {
  if (!fs.existsSync(dir)) {
    console.log("Directorio dist/ aún no generado. Ejecute npm run build primero.");
    return 0;
  }
  let hallazgos = 0;
  for (const entrada of fs.readdirSync(dir, { withFileTypes: true })) {
    const ruta = path.join(dir, entrada.name);
    if (entrada.isDirectory()) {
      hallazgos += escanearDirectorio(ruta);
    } else if (entrada.isFile() && /\.(js|html|css|json)$/.test(entrada.name)) {
      const contenido = fs.readFileSync(ruta, "utf8");
      for (const patron of PATRONES_SECRETOS) {
        if (patron.test(contenido)) {
          console.error(`[ALERTA SEGURIDAD] Posible clave expuesta en ${ruta} (${patron})`);
          hallazgos++;
        }
      }
    }
  }
  return hallazgos;
}

const total = escanearDirectorio(distDir);
if (total > 0) {
  process.exit(1);
} else {
  console.log("OK (OWASP LLM02): Cero claves privadas encontradas en el bundle del cliente.");
}
