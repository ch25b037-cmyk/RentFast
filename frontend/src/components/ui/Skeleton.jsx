export function Skeleton({ className = "" }) {
  return <span aria-hidden="true" className={`skeleton ${className}`} />;
}

export function EmptyState({ title, copy, action }) {
  return (
    <div className="empty-state">
      <div className="empty-mark" aria-hidden="true">+</div>
      <h2>{title}</h2>
      <p>{copy}</p>
      {action}
    </div>
  );
}
