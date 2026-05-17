import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import DatePicker from "../DatePicker";

describe("DatePicker", () => {
  it("shows empty message when no dates", () => {
    render(<DatePicker availableDates={[]} selectedDate="" onChange={vi.fn()} />);
    expect(screen.getByText("暫無歷史資料")).toBeDefined();
  });

  it("renders date buttons", () => {
    const dates = ["2026-05-16", "2026-05-15"];
    render(<DatePicker availableDates={dates} selectedDate="2026-05-16" onChange={vi.fn()} />);
    expect(screen.getByText("5月16日")).toBeDefined();
    expect(screen.getByText("5月15日")).toBeDefined();
  });

  it("highlights selected date", () => {
    const dates = ["2026-05-16", "2026-05-15"];
    render(<DatePicker availableDates={dates} selectedDate="2026-05-16" onChange={vi.fn()} />);
    const selectedBtn = screen.getByRole("button", { name: "5月16日" });
    expect(selectedBtn.className).toContain("bg-blue-600");
  });

  it("calls onChange with clicked date", () => {
    const dates = ["2026-05-16", "2026-05-15"];
    const onChange = vi.fn();
    render(<DatePicker availableDates={dates} selectedDate="2026-05-16" onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "5月15日" }));
    expect(onChange).toHaveBeenCalledWith("2026-05-15");
  });
});
