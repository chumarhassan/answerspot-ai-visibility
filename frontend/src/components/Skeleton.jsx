export function Skeleton({ width, height = 14, radius, style }) {
  return (
    <span
      className="skeleton"
      aria-hidden="true"
      style={{ display: "block", width, height, borderRadius: radius, ...style }}
    />
  );
}
export function SkeletonText({ lines = 3, gap = 10 }) {
  return (
    <div aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className="skeleton-line"
          height={12}
          width={i === lines - 1 ? "60%" : "100%"}
          radius={999}
          style={{ marginTop: i ? gap : 0 }}
        />
      ))}
    </div>
  );
}