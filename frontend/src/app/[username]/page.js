import { apis } from "@/app/urls";

export default async function userPreview({ params }) {
  const res = await fetch(`${apis.userData}${params.username}/`);
  if (!res.ok) {
    return <div className="text-3xl text-red">User not found</div>;
  }
  const user = await res.json();

  return (
    <div className="flex flex-col text-3xl text-purple-400">

    </div>
  );
}
