import type { Meta, StoryObj } from "@storybook/react";
import { SearchBar } from "./SearchBar";
import { userEvent, within, expect } from "@storybook/test";

const meta = {
  title: "AGPT UI/Search Bar",
  component: SearchBar,
  parameters: {
    layout: {
      center: true,
      padding: 0,
    },
    nextjs: {
      appDirectory: true,
      navigation: {
        pathname: "/search",
        query: {
          searchTerm: "",
        },
      },
    },
  },
  tags: ["autodocs"],
  argTypes: {
    placeholder: { control: "text" },
    backgroundColor: { control: "text" },
    iconColor: { control: "text" },
    textColor: { control: "text" },
    placeholderColor: { control: "text" },
  },
  decorators: [
    (Story) => (
      <div className="mx-auto w-full max-w-(--breakpoint-lg) p-4">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof SearchBar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: 'Search for tasks like "optimise SEO"',
  },
};

export const CustomStyles: Story = {
  args: {
    placeholder: "Enter your search query",
    backgroundColor: "bg-blue-100",
    iconColor: "text-blue-500",
    textColor: "text-blue-700",
    placeholderColor: "text-blue-400",
  },
};

export const WithInteraction: Story = {
  args: {
    placeholder: "Type and press Enter",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText("Type and press Enter");

    await userEvent.type(input, "test query");
    await userEvent.keyboard("{Enter}");

    await expect(input).toHaveValue("test query");
  },
};

export const EmptySubmit: Story = {
  args: {
    placeholder: "Empty submit test",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText("Empty submit test");

    await userEvent.keyboard("{Enter}");

    await expect(input).toHaveValue("");
  },
};
