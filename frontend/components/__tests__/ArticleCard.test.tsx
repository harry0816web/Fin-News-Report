import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ArticleCard from "../ArticleCard";
import type { AnalyzedArticle } from "@/types/news";

const mockArticle: AnalyzedArticle = {
  id: "1",
  title: "台積電財報優於預期",
  url: "https://example.com/article/1",
  source: "經濟日報",
  published_at: "2026-05-16T08:30:00+08:00",
  category: "科技股市",
  summary: "台積電 Q2 財報表現亮眼...",
  impact_analysis: "• 正面影響：台股可能上漲\n• 需注意：匯率風險",
  sentiment: "positive",
};

describe("ArticleCard", () => {
  it("renders article title and source", () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText("台積電財報優於預期")).toBeDefined();
    expect(screen.getByText(/經濟日報/)).toBeDefined();
  });

  it("shows sentiment badge", () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText("正面")).toBeDefined();
  });

  it("expands to show details on click", () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.queryByText("📋 新聞摘要")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /台積電財報優於預期/ }));
    expect(screen.getByText("📋 新聞摘要")).toBeDefined();
    expect(screen.getByText("台積電 Q2 財報表現亮眼...")).toBeDefined();
  });

  it("collapses on second click", () => {
    render(<ArticleCard article={mockArticle} />);
    const btn = screen.getByRole("button", { name: /台積電財報優於預期/ });
    fireEvent.click(btn);
    expect(screen.getByText("📋 新聞摘要")).toBeDefined();
    fireEvent.click(btn);
    expect(screen.queryByText("📋 新聞摘要")).toBeNull();
  });
});
