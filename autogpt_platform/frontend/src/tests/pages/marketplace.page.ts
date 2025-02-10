import { ElementHandle, Locator, Page } from "@playwright/test";
import { BasePage } from "./base.page";
import path from "path";

export class MarketplacePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async isLoaded(): Promise<boolean> {
    console.log(`checking if marketplace page is loaded`);
    try {
      // Wait for the marketplace page
      await this.page.getByTestId("marketplace-page").waitFor({
        state: "visible",
        timeout: 10_000,
      });

      return true;
    } catch (error) {
      return false;
    }
  }

  // async listAgents(): Promise<Agent[]> {
  //   console.log(`listing agents in marketplace`);
  // Wait for table rows to be available
  // const rows = await this.page.locator("tbody tr[data-testid]").all();

  // const agents: Agent[] = [];

  // for (const row of rows) {
  //   // Get the id from data-testid attribute
  //   const id = (await row.getAttribute("data-testid")) || "";

  //   // Get columns - there are 3 cells per row (name, run count, last run)
  //   const cells = await row.locator("td").all();

  //   // Extract name from first cell
  //   const name = (await row.getAttribute("data-name")) || "";

  //   // Extract run count from second cell
  //   const runCountText = (await cells[1].textContent()) || "0";
  //   const runCount = parseInt(runCountText, 10);

  //   // Extract last run from third cell's title attribute (contains full timestamp)
  //   // If no title, the cell will be empty indicating no last run
  //   const lastRunCell = cells[2];
  //   const lastRun = (await lastRunCell.getAttribute("title")) || "";

  //   agents.push({
  //     id,
  //     name,
  //     runCount,
  //     lastRun,
  //   });
  // }

  // agents.reduce((acc, agent) => {
  //   if (!agent.id.includes("flow-run")) {
  //     acc.push(agent);
  //   }
  //   return acc;
  // }, [] as Agent[]);

  // return agents;
  // }

  async clickAgent(id: string) {
    console.log(`selecting agent ${id} in marketplace`);
    await this.page.getByTestId(id).click();
  }
}
