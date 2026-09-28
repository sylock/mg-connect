/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./accounts/**/*.py",
    "./assets/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#FAF7F2",
        surface: "#FFFFFF",
        ink: "#27232B",
        muted: "#625A66",
        border: "#DCD4DE",
        focus: "#1D4ED8",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        card: "14px",
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        salon: {
          primary: "#6D365F",
          "primary-content": "#FFFFFF",
          secondary: "#F38F7D",
          "secondary-content": "#27232B",
          accent: "#F38F7D",
          "accent-content": "#27232B",
          neutral: "#27232B",
          "base-100": "#FFFFFF",
          "base-200": "#FAF7F2",
          "base-300": "#DCD4DE",
          info: "#DBEAFE",
          success: "#CCFBF1",
          warning: "#FEF3C7",
          error: "#FEE2E2",
        },
      },
    ],
    darkTheme: false,
    logs: false,
  },
};
