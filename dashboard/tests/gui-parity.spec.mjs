import { expect, test } from "@playwright/test";

// case-research-dashboard had no e2e coverage at all before this: main carried
// no .federation/gui-capabilities.json and no scripts/check_gui_parity.py — the
// gate itself was missing, not just failing. This spec runs against the real
// backend and the real committed ledgers (470 master cases, a live candidate
// queue) rather than stubs, and cross-checks what's rendered against what the
// API actually returned, so a mutation that breaks the data path fails a named
// test instead of silently shipping.

test("Cases tab renders the real case count and the search box filters it", async ({ page }) => {
  const casesResponse = page.waitForResponse(
    (response) => response.url().includes("/cases") && response.status() === 200,
  );
  await page.goto("/", { waitUntil: "domcontentloaded" });
  const cases = await (await casesResponse).json();
  expect(Array.isArray(cases), "GET /cases did not return an array").toBe(true);
  expect(cases.length, "the committed master ledger should not be empty").toBeGreaterThan(0);

  const countBadge = page.locator("input[placeholder='Search…']").locator("xpath=preceding-sibling::span[1]");
  await expect(countBadge).toHaveText(String(cases.length));

  // A query that cannot match any real description or location string.
  await page.getByPlaceholder("Search…").fill("zzz-no-such-sighting-zzz");
  await expect(countBadge).toHaveText("0");
});

test("the evidence-tier filter narrows the grid to matching real cases", async ({ page }) => {
  const casesResponse = page.waitForResponse(
    (response) => response.url().includes("/cases") && response.status() === 200,
  );
  await page.goto("/", { waitUntil: "domcontentloaded" });
  const cases = await (await casesResponse).json();
  const t1Count = cases.filter((c) => c.evidence_tier === "T1").length;

  // Two comboboxes render in the filter row: decade first, evidence tier second.
  await page.getByRole("combobox").nth(1).click();
  await page.getByRole("option", { name: "T1" }).click();

  const countBadge = page.locator("input[placeholder='Search…']").locator("xpath=preceding-sibling::span[1]");
  await expect(countBadge).toHaveText(String(t1Count));
});

test("Statistics tab renders the real totals from the backend", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  const statsResponse = page.waitForResponse(
    (response) => response.url().includes("/stats") && response.status() === 200,
  );
  await page.getByRole("tab", { name: "Statistics" }).click();
  const stats = await (await statsResponse).json();

  await expect(page.getByText("Total")).toBeVisible();
  await expect(page.getByText(String(stats.total), { exact: true })).toBeVisible();
  await expect(page.getByText(String(stats.mapped), { exact: true })).toBeVisible();
});

test("Candidates tab renders the real review queue", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  const candidatesResponse = page.waitForResponse(
    (response) => response.url().includes("/candidates") && response.status() === 200,
  );
  await page.getByRole("tab", { name: "Candidates" }).click();
  const candidates = await (await candidatesResponse).json();

  await expect(page.getByText(`${candidates.length} candidates in queue`)).toBeVisible();
  if (candidates.length > 0) {
    await expect(page.getByText(candidates[0].candidate_id, { exact: true })).toBeVisible();
  }
});
