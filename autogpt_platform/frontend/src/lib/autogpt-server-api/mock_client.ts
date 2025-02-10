import { faker } from "@faker-js/faker";
import BackendAPI from "./client";
import { Block, BlockUIType, ProfileDetails, User } from "./types";

export interface MockClientProps {
  credits?: number;
  blocks?: Block[];
  profile?: ProfileDetails;
  isAuthenticated?: boolean;
}

// Default mock data
export const DEFAULT_MOCK_DATA: Required<MockClientProps> = {
  credits: 10,
  blocks: [
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
  ],
  profile: {
    name: "John Doe",
    username: "johndoe",
    description: "",
    links: [],
    avatar_url: "https://avatars.githubusercontent.com/u/123456789?v=4",
  },
  isAuthenticated: true,
};

export default class MockClient extends BackendAPI {
  private props: Required<MockClientProps>;

  constructor(props: MockClientProps = {}) {
    super();
    this.props = {
      ...DEFAULT_MOCK_DATA,
      ...props,
    };
  }

  override isAuthenticated(): Promise<boolean> {
    return Promise.resolve(this.props.isAuthenticated);
  }

  override createUser(): Promise<User> {
    return Promise.resolve({
      id: faker.string.uuid(),
      email: "test@test.com",
    } satisfies User);
  }

  override getUserCredit(page?: string): Promise<{ credits: number }> {
    return Promise.resolve({ credits: this.props.credits });
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
    return Promise.resolve(this.props.blocks);
  }

  override getStoreProfile(page?: string): Promise<ProfileDetails> {
    return Promise.resolve(this.props.profile);
  }
}
