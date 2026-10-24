// Bundles the two files Home Assistant loads (committed, because HACS does not run builds):
//   laa-dashboard.js        loaded for every user: the dashboard strategy and the redirect of non-administrators
//   laa-dashboard-panel.js  the administrators' panel
import { build } from "esbuild";

const common = { bundle: true, format: "esm", target: "es2022", minify: true, legalComments: "none", logLevel: "info",
  tsconfigRaw: { compilerOptions: { experimentalDecorators: true, useDefineForClassFields: false } } };
await build({ ...common, entryPoints: ["src/dashboard.ts"], outfile: "../custom_components/laa_dashboard/frontend/laa-dashboard.js" });
await build({ ...common, entryPoints: ["src/panel.ts"], outfile: "../custom_components/laa_dashboard/frontend/laa-dashboard-panel.js" });
