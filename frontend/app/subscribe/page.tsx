import SubscribeForm from "@/components/SubscribeForm";

export default function SubscribePage() {
  return (
    <div className="max-w-md mx-auto py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">訂閱台灣財經日報</h1>
      <p className="text-gray-500 mb-8">每天早上 09:00 收到最新財經摘要</p>
      <SubscribeForm />
    </div>
  );
}
