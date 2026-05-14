"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Send } from "lucide-react";
import toast from "react-hot-toast";
import api from "@/lib/api";

export default function CommentBox({ postId }: { postId: number }) {
  const router = useRouter();
  const [content, setContent] = useState("");
  const [guestName, setGuestName] = useState("");
  const [guestEmail, setGuestEmail] = useState("");
  const [pending, startTransition] = useTransition();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (content.trim().length < 2) {
      toast.error("Bình luận quá ngắn");
      return;
    }

    try {
      await api.post(`/comments/post/${postId}`, {
        content,
        guest_name: guestName || undefined,
        guest_email: guestEmail || undefined,
      });
      toast.success("Bình luận đã gửi, chờ admin duyệt!");
      setContent("");
      setGuestName("");
      setGuestEmail("");
      startTransition(() => router.refresh());
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Gửi thất bại, vui lòng thử lại";
      toast.error(message);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      aria-labelledby="comment-form-heading"
      className="mt-8 bg-brand-50/50 rounded-xl p-6 border border-brand-100"
    >
      <h3
        id="comment-form-heading"
        className="font-display text-lg font-semibold text-stone-800 mb-4"
      >
        Để lại bình luận
      </h3>

      <div className="grid sm:grid-cols-2 gap-4 mb-4">
        <div>
          <label htmlFor="guest_name" className="block text-sm text-stone-600 mb-1.5">
            Tên hiển thị
          </label>
          <input
            id="guest_name"
            type="text"
            value={guestName}
            onChange={(e) => setGuestName(e.target.value)}
            maxLength={100}
            className="w-full px-3 py-2 rounded-lg border border-brand-200 bg-white focus:outline-none focus:border-brand-400 text-sm"
            placeholder="Tên của bạn"
          />
        </div>
        <div>
          <label htmlFor="guest_email" className="block text-sm text-stone-600 mb-1.5">
            Email <span className="text-xs text-stone-400">(không hiển thị)</span>
          </label>
          <input
            id="guest_email"
            type="email"
            value={guestEmail}
            onChange={(e) => setGuestEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-brand-200 bg-white focus:outline-none focus:border-brand-400 text-sm"
            placeholder="you@example.com"
          />
        </div>
      </div>

      <div className="mb-4">
        <label htmlFor="comment_content" className="block text-sm text-stone-600 mb-1.5">
          Nội dung bình luận
        </label>
        <textarea
          id="comment_content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          minLength={2}
          maxLength={1000}
          rows={4}
          className="w-full px-3 py-2 rounded-lg border border-brand-200 bg-white focus:outline-none focus:border-brand-400 text-sm resize-y"
          placeholder="Chia sẻ ý kiến của bạn về bài viết..."
          aria-describedby="comment-help"
        />
        <p id="comment-help" className="text-xs text-stone-400 mt-1.5" aria-live="polite">
          {content.length}/1000 ký tự. Bình luận sẽ hiển thị sau khi được duyệt.
        </p>
      </div>

      <button
        type="submit"
        disabled={pending || content.trim().length < 2}
        className="btn-primary text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="w-4 h-4" />
        {pending ? "Đang gửi..." : "Gửi bình luận"}
      </button>
    </form>
  );
}
