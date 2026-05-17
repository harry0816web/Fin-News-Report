import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import HomePage from "../page";

vi.mock("@/lib/api", () => ({
  fetchNews: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

import { fetchNews } from "@/lib/api";
const mockFetchNews = fetchNews as ReturnType<typeof vi.fn>;

const mockDigest = {
  date: "2026-05-16",
  generated_at: "2026-05-16T09:00:00+08:00",
  article_count: 2,
  articles: [
    {
      id: "1",
      title: "台積電財報超預期",
      url: "https://example.com/1",
      source: "經濟日報",
      published_at: "2026-05-16T08:00:00+08:00",
      category: "科技股市",
      summary: "摘要",
      impact_analysis: "影響",
      sentiment: "positive" as const,
    },
  ],
};

describe("HomePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading skeleton initially", () => {
    mockFetchNews.mockReturnValue(new Promise(() => {}));
    render(<HomePage />);
    expect(screen.getByLabelText("載入中")).toBeDefined();
  });

  it("shows empty state when API returns null (404)", async () => {
    mockFetchNews.mockResolvedValue(null);
    render(<HomePage />);
    await waitFor(() => {
      expect(screen.getByText("今日摘要尚未生成，請稍後再試")).toBeDefined();
    });
  });

  it("shows articles when data is loaded", async () => {
    mockFetchNews.mockResolvedValue(mockDigest);
    render(<HomePage />);
    await waitFor(() => {
      expect(screen.getByText("台積電財報超預期")).toBeDefined();
    });
  });

  it("shows error state when API throws", async () => {
    mockFetchNews.mockRejectedValue(new Error("Network error"));
    render(<HomePage />);
    await waitFor(() => {
      expect(screen.getByText("載入失敗，請稍後再試")).toBeDefined();
    });
  });
});
