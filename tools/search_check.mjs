// Site search check (Nov 14): runs the headline searches in articles/search-also.json ("checks") against the Pagefind
// index the workflow just built, and prints any whose first result isn't the expected page. It never fails the build;
// a miss means a synonym (an article's also: line, or a chart's entry in that file) needs a look.
// Usage: node tools/search_check.mjs public
// The ranking options must match assets/search.js.
import { readFile } from "node:fs/promises";

const root = process.argv[2] || "public";
const RANKING = { metaWeights: { title: 5, also: 10, kind: 0, sub: 2, reading: 0 } };
globalThis.fetch = async (url) => {                        // Pagefind fetches its own pieces; serve them from disk
  const path = String(url).split("?")[0];
  try {
    return new Response(await readFile(root + path), { status: 200 });
  } catch {
    return new Response("", { status: 404 });
  }
};
try {
  const checks = JSON.parse(await readFile("articles/search-also.json", "utf8")).checks || [];
  const pf = await import(new URL(`../${root}/pagefind/pagefind.js`, import.meta.url));
  await pf.options({ basePath: "/pagefind/", ranking: RANKING });
  const misses = [];
  for (const [q, want] of checks) {
    const s = await pf.search(q);
    const first = s.results.length ? (await s.results[0].data()).meta.title : "(nothing)";
    if (!first.startsWith(want)) misses.push(`  "${q}": first is "${first}", expected "${want}…"`);
  }
  console.log(`search check: ${checks.length - misses.length} of ${checks.length} headline searches put the expected page first`);
  if (misses.length) console.log(misses.join("\n"));
} catch (e) {
  console.log(`search check: skipped (${e.message})`);
}
