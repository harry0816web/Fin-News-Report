"use client";

import { useState } from "react";
import type { AnalyzedArticle } from "@/types/news";

interface ArticleCardProps {
  article: AnalyzedArticle;
}

const sentimentConfig = {
  positive: { label: "正面", className: "bg-green-100 text-green-800" },
  negative: { label: "負面", className: "bg-red-100 text-red-800" },
  neutral: { label: "中性", className: "bg-gray-100 text-gray-700" },
} as const;

export default function ArticleCard({ article }: ArticleCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const sentiment = sentimentConfig[article.sentiment] ?? sentimentConfig.neutral;

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
      <div
        className="flex items-start justify-between gap-2 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        aria-expanded={isExpanded}
      >
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 leading-snug">{article.title}</h3>
          <p className="text-sm text-gray-500 mt-1">
            {article.source} ｜ {new Date(article.published_at).toLocaleString("zh-TW")}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sentiment.className}`}>
            {sentiment.label}
          </span>
          <span className="text-gray-400 text-sm">{isExpanded ? "▼" : "▶"}</span>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4 border-t border-gray-100 pt-4">
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-1">📋 新聞摘要</p>
            <p className="text-sm text-gray-600 leading-relaxed">{article.summary}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-1">📈 對台灣市場的潛在影響</p>
            <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">
              {article.impact_analysis}
            </p>
          </div>
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
          >
            🔗 原文連結
          </a>
        </div>
      )}
    </div>
  );
}
