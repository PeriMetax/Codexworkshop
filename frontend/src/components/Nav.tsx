import Link from "next/link";

const links = [
  ["/upload", "Upload"],
  ["/results", "Validation Results"],
  ["/review", "Review Queue"],
  ["/sync", "Sync Status"],
  ["/dashboard", "Dashboard"],
] as const;

export function Nav() {
  return (
    <nav style={{ display: "flex", gap: 12, marginBottom: 20 }}>
      {links.map(([href, label]) => (
        <Link key={href} href={href}>{label}</Link>
      ))}
    </nav>
  );
}
