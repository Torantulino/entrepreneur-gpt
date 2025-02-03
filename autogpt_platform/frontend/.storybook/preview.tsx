import type { Preview } from "@storybook/react";
import { initialize, mswLoader } from "msw-storybook-addon";
import "../src/app/globals.css";
import { Providers } from "../src/app/providers";
// Initialize MSW
import React from "react";
initialize();

const preview: Preview = {
  parameters: {
    nextjs: {
      appDirectory: true,
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  loaders: [mswLoader],
  decorators: [
    (Story) => {
      return (
        <Providers useMockBackend={true}>
          <Story />
        </Providers>
      );
    },
  ],
};

export default preview;
