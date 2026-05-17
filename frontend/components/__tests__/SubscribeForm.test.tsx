import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import SubscribeForm from "../SubscribeForm";

// mock the api module
vi.mock("@/lib/api", () => ({
  subscribeEmail: vi.fn(),
}));

import { subscribeEmail } from "@/lib/api";

const mockSubscribeEmail = subscribeEmail as ReturnType<typeof vi.fn>;

describe("SubscribeForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows validation error for empty email", async () => {
    render(<SubscribeForm />);
    fireEvent.click(screen.getByRole("button", { name: "訂閱" }));
    expect(screen.getByText("請輸入 Email")).toBeDefined();
  });

  it("shows validation error for invalid email", async () => {
    render(<SubscribeForm />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "notanemail" } });
    fireEvent.click(screen.getByRole("button", { name: "訂閱" }));
    expect(screen.getByText("Email 格式不正確")).toBeDefined();
  });

  it("shows success message after 201 response", async () => {
    mockSubscribeEmail.mockResolvedValueOnce({ status: 201, message: "subscribed" });
    render(<SubscribeForm />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "test@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: "訂閱" }));
    await waitFor(() => {
      expect(screen.getByText(/訂閱成功/)).toBeDefined();
    });
  });

  it("shows already subscribed message after 200 response", async () => {
    mockSubscribeEmail.mockResolvedValueOnce({ status: 200, message: "already subscribed" });
    render(<SubscribeForm />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "test@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: "訂閱" }));
    await waitFor(() => {
      expect(screen.getByText(/已訂閱/)).toBeDefined();
    });
  });
});
