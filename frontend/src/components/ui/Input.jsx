export function Input({ label, error, id, ...props }) {
  const errorId = error ? `${id}-error` : undefined;
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <input id={id} aria-invalid={Boolean(error)} aria-describedby={errorId} {...props} />
      {error && <small id={errorId} className="field-error" role="alert">{error}</small>}
    </label>
  );
}
