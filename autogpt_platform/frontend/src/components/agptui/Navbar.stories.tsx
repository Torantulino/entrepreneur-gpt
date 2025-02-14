import type { Meta, StoryObj } from "@storybook/react";
import { Navbar } from "./Navbar";
import { userEvent, within } from "@storybook/test";
import { IconType } from "../ui/icons";
import { ProfileDetails } from "@/lib/autogpt-server-api/types";

// Mock the API responses
const mockProfileData: ProfileDetails = {
  name: "John Doe",
  username: "johndoe",
  description: "",
  links: [],
  avatar_url: "https://avatars.githubusercontent.com/u/123456789?v=4",
};

const defaultMenuItemGroups = [
  {
    items: [
      { icon: IconType.Edit, text: "Edit profile", href: "/profile/edit" },
    ],
  },
  {
    items: [
      {
        icon: IconType.LayoutDashboard,
        text: "Creator Dashboard",
        href: "/dashboard",
      },
      {
        icon: IconType.UploadCloud,
        text: "Publish an agent",
        href: "/publish",
      },
    ],
  },
  {
    items: [{ icon: IconType.Settings, text: "Settings", href: "/settings" }],
  },
  {
    items: [
      {
        icon: IconType.LogOut,
        text: "Log out",
        onClick: () => console.log("Logged out"),
      },
    ],
  },
];

const defaultLinks = [
  { name: "Marketplace", href: "/marketplace" },
  { name: "Library", href: "/library" },
  { name: "Build", href: "/builder" },
];

const meta = {
  title: "AGPT UI/Navbar",
  component: Navbar,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
  argTypes: {
    links: { control: "object" },
    menuItemGroups: { control: "object" },
    mockUser: { control: "object" },
    mockClientProps: { control: "object" },
  },
} satisfies Meta<typeof Navbar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    links: defaultLinks,
    menuItemGroups: defaultMenuItemGroups,
    mockUser: {
      id: "123",
      email: "test@test.com",
      user_metadata: {
        name: "Test User",
      },
      app_metadata: {
        provider: "email",
      },
      aud: "test",
      created_at: new Date().toISOString(),
    },
    mockClientProps: {
      credits: 1500,
      profile: mockProfileData,
    },
  },
  parameters: {
    mockBackend: {
      credits: 1500,
      profile: mockProfileData,
    },
  },
};

export const WithCredits: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockBackend: {
      credits: 1500,
    },
  },
};

export const WithLargeCredits: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockBackend: {
      credits: 999999,
    },
  },
};

export const WithZeroCredits: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockBackend: {
      credits: 0,
    },
  },
};

export const WithInteraction: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockBackend: {
      credits: 1500,
      profile: mockProfileData,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const profileTrigger = canvas.getByRole("button");

    await userEvent.click(profileTrigger);

    // Wait for the popover to appear
    await canvas.findByText("Edit profile");
  },
};
