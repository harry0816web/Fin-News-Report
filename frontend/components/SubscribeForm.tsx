"use client";

import { useState } from "react";
import { subscribeEmail } from "@/lib/api";

type FormStatus = "idle" | "loading" | "success" | "error" | "already_subscribed";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function SubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<FormStatus>("idle");
  const [validationError, setValidationError] = useState("");

  function validate(): boolean {
    if (!email.trim()) {
      setValidationError("請輸入 Email");
      return false;
    }
    if (!EMAIL_REGEX.test(email)) {
      setValidationError("Email 格式不正確");
      return false;
    }
    setValidationError("");
    return true;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    setStatus("loading");
    try {
      const result = await subscribeEmail(email);
      if (result.status === 201) {
        setStatus("success");
      } else if (result.status === 200) {
        setStatus("already_subscribed");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div className="text-green-700 text-sm">
        ✅ 訂閱成功！將於明天起收到每日財經摘要
      </div>
    );
  }
  if (status === "already_subscribed") {
    return (
      <div className="text-blue-700 text-sm">
        ℹ️ 此 Email 已訂閱
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <input
          type="text"
          inputMode="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={status === "loading"}
        />
        {validationError && (
          <p className="text-red-600 text-xs mt-1">{validationError}</p>
        )}
      </div>
      <button
        type="submit"
        disabled={status === "loading"}
        className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {status === "loading" ? "訂閱中…" : "訂閱"}
      </button>
      {status === "error" && (
        <p className="text-red-600 text-xs">❌ 訂閱失敗，請稍後再試</p>
      )}
      <p className="text-gray-400 text-xs">訂閱後可隨時透過 Email 內退訂連結取消</p>
    </form>
  );
}
