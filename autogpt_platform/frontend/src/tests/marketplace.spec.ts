import { expect, TestInfo } from "@playwright/test";
import { test } from "./fixtures";
import { BuildPage } from "./pages/build.page";
import { MonitorPage } from "./pages/monitor.page";
import { v4 as uuidv4 } from "uuid";
import { MarketplacePage } from "./pages/marketplace.page";

test.describe("Marketplace", () => {
  let buildPage: BuildPage;
  let monitorPage: MonitorPage;
  let marketplacePage: MarketplacePage;
  test.beforeEach(async ({ page, loginPage, testUser }, testInfo: TestInfo) => {
    buildPage = new BuildPage(page);
    monitorPage = new MonitorPage(page);
    marketplacePage = new MarketplacePage(page);

    // Start each test with login using worker auth
    await page.goto("/login");
    await loginPage.login(testUser.email, testUser.password);
    await test.expect(page).toHaveURL("/");

    // add a test agent
    const basicBlock = await buildPage.getDictionaryBlockDetails();
    const testAttachName = uuidv4();
    await buildPage.createSingleBlockAgent(
      `test-agent-${testAttachName}`,
      `test-agent-description-${testAttachName}`,
      basicBlock,
    );
    await buildPage.runAgent();
    await monitorPage.navbar.clickMonitorLink();
    await monitorPage.waitForPageLoad();
    await test.expect(monitorPage.isLoaded()).resolves.toBeTruthy();
    testInfo.attach("agent-testAttachName", { body: testAttachName });
  });

  test.afterAll(async ({}, testInfo: TestInfo) => {
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();
    await marketplacePage.deleteAgent(`test-agent-${testAttachName}`);
  });

  test("user can view marketplace", async ({ page }) => {
    await test.expect(marketplacePage.isLoaded()).resolves.toBeTruthy();
  });

  test("user can view marketplace page", async ({
    page,
  }, testInfo: TestInfo) => {
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
  });

  test("user can view a specific agent", async ({
    page,
  }, testInfo: TestInfo) => {
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();

    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.selectAgent(`test-agent-${testAttachName}`);
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace/agent"));
  });

  test("user can submit an agent to the marketplace", async ({
    page,
  }, testInfo: TestInfo) => {
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();

    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.submitAgent(`test-agent-${testAttachName}`);
  });

  test("admin can approve an agent", async ({ page }, testInfo: TestInfo) => {
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();

    // Submit the agent to the marketplace
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.submitAgent(`test-agent-${testAttachName}`);

    // Approve the agent
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.approveAgent(`test-agent-${testAttachName}`);

    // Check that the agent is in the marketplace
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    // Search for the agent
    const results = await marketplacePage.searchAgent(
      `test-agent-${testAttachName}`,
    );
    test.expect(results.length).toBe(1);
  });

  test("admin can reject an agent", async ({ page }, testInfo: TestInfo) => {
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();

    // Submit the agent to the marketplace
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.submitAgent(`test-agent-${testAttachName}`);

    // Reject the agent
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.rejectAgent(`test-agent-${testAttachName}`);

    // Check that the agent is not in the marketplace
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    const results = await marketplacePage.searchAgent(
      `test-agent-${testAttachName}`,
    );
    test.expect(results.length).toBe(0);
  });

  test("user can run a marketplace agent", async ({
    page,
  }, testInfo: TestInfo) => {
    // Get the agent testAttachName from the test info
    if (testInfo.attachments.length === 0 || !testInfo.attachments[0].body) {
      throw new Error("No agent testAttachName attached to the test");
    }
    const testAttachName = testInfo.attachments[0].body.toString();

    // Download the agent
    await marketplacePage.navbar.clickMarketplaceLink();
    await test.expect(page).toHaveURL(new RegExp("/.*marketplace"));
    await marketplacePage.selectAgent(`test-agent-${testAttachName}`);
    await marketplacePage.downloadAgent(`test-agent-${testAttachName}`);

    // Open the agent in the monitor page
    await monitorPage.navbar.clickMonitorLink();
    await test.expect(page).toHaveURL(new RegExp("/.*monitor"));
    await monitorPage.waitForPageLoad();
    await test.expect(monitorPage.isLoaded()).resolves.toBeTruthy();
    await monitorPage.clickAgent(`test-agent-${testAttachName}`);

    // Run the agent
    await buildPage.runAgent();
  });
});
