import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import HistoryPage from "../page";

vi.mock("@/lib/api", () => ({
  fetchAvailableDates: vi.fn(),
  fetchNews: vi.fn(),
}));

vi.mock("@/components/LoadingSkeleton", () => ({
  default: () => <div aria-label="載入中" />,
}));

import { fetchAvailableDates, fetchNews } from "@/lib/api";
const mockFetchDates = fetchAvailableDates as ReturnType<typeof vi.fn>;
const mockFetchNews = fetchNews as ReturnType<typeof vi.fn>;

const mockDigest = {
  date: "2026-05-16",
  generated_at: "2026-05-16T09:00:00+08:00",
  article_count: 1,
  articles: [
    {
      id: "1",
      title: "歷史文章測試",
      url: "https://example.com/1",
      source: "測試媒體",
      published_at: "2026-05-16T08:00:00+08:00",
      category: "科技股市",
      summary: "摘要",
      impact_analysis: "影響",
      sentiment: "neutral" as const,
    },
  ],
};

describe("HistoryPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders heading", () => {
    mockFetchDates.mockResolvedValue([]);
    mockFetchNews.mockResolvedValue(null);
    render(<HistoryPage />);
    expect(screen.getByText("歷史新聞")).toBeDefined();
  });

  it("shows date picker with available dates", async () => {
    mockFetchDates.mockResolvedValue(["2026-05-16", "2026-05-15"]);
    mockFetchNews.mockResolvedValue(mockDigest);
    render(<HistoryPage />);
    await waitFor(() => {
      expect(screen.getByText("5月16日")).toBeDefined();
    });
  });

  it("loads articles for selected date", async () => {
    mockFetchDates.mockResolvedValue(["2026-05-16", "2026-05-15"]);
    mockFetchNews.mockResolvedValue(mockDigest);
    render(<HistoryPage />);
    await waitFor(() => {
      expect(screen.getByText("歷史文章測試")).toBeDefined();
    });
  });
});
