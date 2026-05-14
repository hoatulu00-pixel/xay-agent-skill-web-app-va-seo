import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { format } from "date-fns";
import { vi } from "date-fns/locale";
import { ArrowLeft } from "lucide-react";
import type { Post } from "@/lib/api";
import CommentList from "@/components/blog/CommentList";
import CommentBox from "@/components/blog/CommentBox";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getPost(slug: string): Promise<Post | null> {
  try {
    const res = await fetch(`${API}/posts/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug);
  if (!post) return { title: "Không tìm thấy bài viết" };
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { images: post.cover_image_url ? [post.cover_image_url] : [] },
  };
}

export default async function BlogDetailPage({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug);
  if (!post) notFound();

  const date = post.published_at || post.created_at;

  return (
    <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Back */}
      <Link href="/blog" className="inline-flex items-center gap-1.5 text-stone-500 hover:text-brand-600 text-sm mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Quay lại blog
      </Link>

      {/* Category */}
      {post.category && (
        <span className="text-brand-500 font-medium text-sm uppercase tracking-wide">
          {post.category.name}
        </span>
      )}

      {/* Title */}
      <h1 className="font-display text-4xl md:text-5xl font-bold text-stone-800 leading-tight mt-3 mb-5">
        {post.title}
      </h1>

      {/* Meta */}
      <div className="flex items-center gap-4 text-sm text-stone-500 mb-8 pb-8 border-b border-brand-100">
        <span className="font-medium text-stone-700">{post.author.full_name}</span>
        <span>·</span>
        <time dateTime={date}>{format(new Date(date), "d MMMM yyyy", { locale: vi })}</time>
      </div>

      {/* Cover image */}
      {post.cover_image_url && (
        <div className="relative aspect-[16/9] rounded-2xl overflow-hidden mb-10">
          <Image src={post.cover_image_url} alt={post.title} fill className="object-cover" priority />
        </div>
      )}

      {/* Content */}
      <div
        className="prose-brand"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {/* Comments */}
      <CommentList postId={post.id} />
      <CommentBox postId={post.id} />

      {/* Footer */}
      <div className="mt-16 pt-8 border-t border-brand-100">
        <Link href="/blog" className="btn-outline">
          <ArrowLeft className="w-4 h-4" />
          Xem thêm bài viết
        </Link>
      </div>
    </article>
  );
}
