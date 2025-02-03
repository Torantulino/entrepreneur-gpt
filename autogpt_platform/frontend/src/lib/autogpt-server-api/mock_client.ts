import { faker } from "@faker-js/faker";
import BackendAPI from "./client";
import { Block, BlockUIType, User } from "./types";

export default class MockClient extends BackendAPI {
  override isAuthenticated(): Promise<boolean> {
    return Promise.resolve(true);
  }

  override createUser(): Promise<User> {
    return Promise.resolve({
      id: faker.string.uuid(),
      email: "test@test.com",
    } satisfies User);
  }

  override getUserCredit(page?: string): Promise<{ credits: number }> {
    return Promise.resolve({ credits: 10 });
  }

  override getAutoTopUpConfig(): Promise<{
    amount: number;
    threshold: number;
  }> {
    return Promise.resolve({ amount: 10, threshold: 10 });
  }

  override setAutoTopUpConfig(config: {
    amount: number;
    threshold: number;
  }): Promise<{ amount: number; threshold: number }> {
    return Promise.resolve(config);
  }

  override requestTopUp(amount: number): Promise<{ checkout_url: string }> {
    return Promise.resolve({ checkout_url: "https://checkout.stripe.com" });
  }

  override getUserPaymentPortalLink(): Promise<{ url: string }> {
    return Promise.resolve({ url: "https://payment.stripe.com" });
  }

  override fulfillCheckout(): Promise<void> {
    return Promise.resolve();
  }

  override getBlocks(): Promise<Block[]> {
    return Promise.resolve([
      {
        id: faker.string.uuid(),
        name: faker.lorem.word(),
        description: faker.lorem.sentence(),
        inputSchema: {
          type: "object",
          properties: {},
        },
        outputSchema: {
          type: "object",
          properties: {},
        },
        staticOutput: false,
        categories: [],
        uiType: BlockUIType.STANDARD,
        costs: [],
        hardcodedValues: {},
      },
    ] satisfies Block[]);
  }
}
