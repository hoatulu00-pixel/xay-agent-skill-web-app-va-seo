import { format } from "date-fns";
import { vi } from "date-fns/locale";
import { MessageCircle } from "lucide-react";
import type { Comment } from "@/lib/api";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getComments(postId: number): Promise<Comment[]> {
  try {
    const res = await fetch(`${API}/comments/post/${postId}`, {
      next: { revalidate: 30, tags: [`comments-${postId}`] },
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function CommentList({ postId }: { postId: number }) {
  const comments = await getComments(postId);

  return (
    <section aria-labelledby="comments-heading" className="mt-12">
      <h2
        id="comments-heading"
        className="font-display text-2xl font-semibold text-stone-800 flex items-center gap-2 mb-6"
      >
        <MessageCircle className="w-5 h-5 text-brand-500" />
        Bình luận ({comments.length})
      </h2>

      {comments.length === 0 ? (
        <p className="text-stone-400 italic">Chưa có bình luận. Hãy là người đầu tiên!</p>
      ) : (
        <ul className="space-y-6">
          {comments.map((c) => {
            const author = c.user?.full_name || c.guest_name || "Khách";
            return (
              <li
                key={c.id}
                className="border-l-2 border-brand-200 pl-4 py-1"
              >
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="font-medium text-stone-700">{author}</span>
                  <time
                    dateTime={c.created_at}
                    className="text-xs text-stone-400"
                  >
                    {format(new Date(c.created_at), "d MMM yyyy, HH:mm", { locale: vi })}
                  </time>
                </div>
                <div
                  className="prose-brand text-sm"
                  dangerouslySetInnerHTML={{ __html: c.content }}
                />
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
