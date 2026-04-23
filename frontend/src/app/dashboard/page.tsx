import { fetchJson } from "@/lib/api";

export default async function DashboardPage() {
  const data = await fetchJson<any>("/dashboard");
  return (
    <div>
      <h2>Dashboard / Summary</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
