import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

test("welcome screen explains the lending value", () => {
  render(<MemoryRouter><App /></MemoryRouter>);

  expect(screen.getByRole("heading", { name: /borrow what you need/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /sign in/i })).toBeInTheDocument();
});
