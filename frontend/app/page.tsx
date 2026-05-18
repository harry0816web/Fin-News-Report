"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchNews } from "@/lib/api";
import type { DailyDigest, Category } from "@/types/news";
import CategorySection from "@/components/CategorySection";
import LoadingSkeleton from "@/components/LoadingSkeleton";

const CATEGORY_ORDER: Category[] = ["科技股市", "總體經濟", "上市公司公告", "國際財經"];

function formatDigestDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${year}年${Number(month)}月${Number(day)}日`;
}

export default function HomePage() {
  const [digest, setDigest] = useState<DailyDigest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchNews()
      .then((data) => {
        setDigest(data);
      })
      .catch(() => {
        setError(true);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const formattedDate = digest ? formatDigestDate(digest.date) : "";

  const groupedArticles = digest
    ? CATEGORY_ORDER.reduce<Record<string, typeof digest.articles>>(
        (acc, cat) => {
          acc[cat] = digest.articles.filter((a) => a.category === cat);
          return acc;
        },
        {}
      )
    : {};

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">台灣財經日報</h1>
          {formattedDate && (
            <p className="text-sm text-gray-500 mt-1">{formattedDate}</p>
          )}
        </div>
        <Link
          href="/subscribe"
          className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700"
        >
          訂閱 Email
        </Link>
      </div>

      {loading && <LoadingSkeleton />}

      {!loading && error && (
        <p className="text-red-600 text-center py-12">載入失敗，請稍後再試</p>
      )}

      {!loading && !error && !digest && (
        <p className="text-gray-500 text-center py-12">今日摘要尚未生成，請稍後再試</p>
      )}

      {!loading && !error && digest && (
        <div>
          {CATEGORY_ORDER.map((category) => (
            <CategorySection
              key={category}
              category={category}
              articles={groupedArticles[category] ?? []}
            />
          ))}
        </div>
      )}
    </div>
  );
}
