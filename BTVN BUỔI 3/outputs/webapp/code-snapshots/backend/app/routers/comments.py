from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
import bleach
from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentModerate, CommentOut, CommentAdminOut
from app.dependencies import get_admin_user
from app.services.auth_service import decode_token

router = APIRouter(prefix="/comments", tags=["comments"])

ALLOWED_TAGS = ["b", "i", "em", "strong", "a", "br"]
ALLOWED_ATTRS = {"a": ["href", "rel"]}


def _sanitize(html: str) -> str:
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    return bleach.linkify(cleaned, parse_email=False)


def _optional_user(request: Request, db: Session) -> Optional[User]:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.get(User, int(user_id))


@router.get("/post/{post_id}", response_model=List[CommentOut])
def list_comments_for_post(
    post_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="Post not found")
    return (
        db.query(Comment)
        .options(joinedload(Comment.user))
        .filter(Comment.post_id == post_id, Comment.is_approved == True, Comment.is_flagged == False)
        .order_by(desc(Comment.created_at))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )


@router.post("/post/{post_id}", response_model=CommentOut, status_code=201)
def create_comment(
    post_id: int,
    data: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="Post not found")

    user = _optional_user(request, db)
    if not user and not (data.guest_name and data.guest_email):
        raise HTTPException(status_code=400, detail="Guest must provide name and email")

    safe_content = _sanitize(data.content)

    comment = Comment(
        content=safe_content,
        guest_name=data.guest_name if not user else None,
        guest_email=data.guest_email if not user else None,
        user_id=user.id if user else None,
        post_id=post_id,
        is_approved=False,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return db.query(Comment).options(joinedload(Comment.user)).get(comment.id)


@router.get("/admin", response_model=List[CommentAdminOut])
def list_all_comments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|approved|flagged)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    q = db.query(Comment).options(joinedload(Comment.user))
    if status == "pending":
        q = q.filter(Comment.is_approved == False, Comment.is_flagged == False)
    elif status == "approved":
        q = q.filter(Comment.is_approved == True)
    elif status == "flagged":
        q = q.filter(Comment.is_flagged == True)
    return q.order_by(desc(Comment.created_at)).offset((page - 1) * limit).limit(limit).all()


@router.patch("/{comment_id}/moderate", response_model=CommentAdminOut)
def moderate_comment(
    comment_id: int,
    data: CommentModerate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return db.query(Comment).options(joinedload(Comment.user)).get(comment.id)


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
