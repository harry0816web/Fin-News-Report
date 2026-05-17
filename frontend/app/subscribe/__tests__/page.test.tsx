import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import SubscribePage from "../page";

vi.mock("@/components/SubscribeForm", () => ({
  default: () => <div data-testid="subscribe-form">表單元件</div>,
}));

describe("SubscribePage", () => {
  it("renders heading and description", () => {
    render(<SubscribePage />);
    expect(screen.getByText("訂閱台灣財經日報")).toBeDefined();
    expect(screen.getByText("每天早上 09:00 收到最新財經摘要")).toBeDefined();
  });

  it("renders SubscribeForm component", () => {
    render(<SubscribePage />);
    expect(screen.getByTestId("subscribe-form")).toBeDefined();
  });
});
