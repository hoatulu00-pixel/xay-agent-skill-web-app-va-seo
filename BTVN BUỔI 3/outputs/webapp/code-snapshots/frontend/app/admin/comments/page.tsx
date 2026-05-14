"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Check, Flag, Trash2, MessageCircle } from "lucide-react";
import toast from "react-hot-toast";
import api, { type CommentAdmin } from "@/lib/api";

type StatusFilter = "pending" | "approved" | "flagged" | "all";

export default function AdminCommentsPage() {
  const [comments, setComments] = useState<CommentAdmin[]>([]);
  const [filter, setFilter] = useState<StatusFilter>("pending");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const params = filter === "all" ? "" : `?status=${filter}`;
      const res = await api.get<CommentAdmin[]>(`/comments/admin${params}`);
      setComments(res.data);
    } catch {
      toast.error("Không tải được danh sách bình luận");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [filter]);

  async function moderate(id: number, action: "approve" | "flag") {
    try {
      if (action === "approve") {
        await api.patch(`/comments/${id}/moderate`, { is_approved: true, is_flagged: false });
        toast.success("Đã duyệt");
      } else {
        await api.patch(`/comments/${id}/moderate`, { is_flagged: true, is_approved: false });
        toast.success("Đã gắn cờ");
      }
      load();
    } catch {
      toast.error("Thao tác thất bại");
    }
  }

  async function remove(id: number) {
    if (!confirm("Xóa bình luận này vĩnh viễn?")) return;
    try {
      await api.delete(`/comments/${id}`);
      toast.success("Đã xóa");
      load();
    } catch {
      toast.error("Xóa thất bại");
    }
  }

  const filterTabs: { key: StatusFilter; label: string }[] = [
    { key: "pending", label: "Chờ duyệt" },
    { key: "approved", label: "Đã duyệt" },
    { key: "flagged", label: "Đã gắn cờ" },
    { key: "all", label: "Tất cả" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-stone-800 flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-brand-500" />
          Bình luận
        </h1>
      </div>

      <div className="flex gap-1 mb-4 border-b border-gray-100">
        {filterTabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setFilter(t.key)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              filter === t.key
                ? "text-brand-500 border-b-2 border-brand-500"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {loading ? (
          <p className="text-stone-400 text-center py-12">Đang tải...</p>
        ) : comments.length === 0 ? (
          <p className="text-stone-400 text-center py-12">Không có bình luận</p>
        ) : (
          <ul className="divide-y divide-gray-50">
            {comments.map((c) => {
              const author = c.user?.full_name || c.guest_name || "Khách";
              const email = c.user?.email || c.guest_email || "—";
              return (
                <li key={c.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-stone-800 text-sm">{author}</span>
                        <span className="text-xs text-stone-400">{email}</span>
                        <time className="text-xs text-stone-400 ml-auto">
                          {format(new Date(c.created_at), "dd/MM/yyyy HH:mm")}
                        </time>
                      </div>
                      <p className="text-sm text-stone-600 mb-2">
                        Trên bài <span className="text-brand-500">#{c.post_id}</span>
                      </p>
                      <div
                        className="text-sm text-stone-700 prose-brand"
                        dangerouslySetInnerHTML={{ __html: c.content }}
                      />
                      <div className="flex items-center gap-2 mt-2">
                        {c.is_approved && (
                          <span className="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full">
                            Đã duyệt
                          </span>
                        )}
                        {c.is_flagged && (
                          <span className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full">
                            Đã gắn cờ
                          </span>
                        )}
                        {!c.is_approved && !c.is_flagged && (
                          <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                            Chờ duyệt
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-1 shrink-0">
                      {!c.is_approved && (
                        <button
                          onClick={() => moderate(c.id, "approve")}
                          aria-label="Duyệt bình luận"
                          className="p-1.5 text-stone-400 hover:text-green-500 transition-colors"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                      {!c.is_flagged && (
                        <button
                          onClick={() => moderate(c.id, "flag")}
                          aria-label="Gắn cờ bình luận"
                          className="p-1.5 text-stone-400 hover:text-orange-500 transition-colors"
                        >
                          <Flag className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => remove(c.id)}
                        aria-label="Xóa bình luận"
                        className="p-1.5 text-stone-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
